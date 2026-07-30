import logging
import re
from pathlib import Path

from src.models.project import (
    ProjectInfo,
    DataEntity,
    DataRelationship,
    EntityField,
)
from src.parsers.java_parser import parse_java_file
from src.parsers.spring_parser import extract_spring_metadata, MYBATIS_BASE_CLASSES, MYBATIS_EXCLUDED_CLASSES
from src.parsers.mybatis_mapper_parser import parse_mapper_xmls

logger = logging.getLogger(__name__)

RELATIONSHIP_ANNOTATIONS = {
    "ManyToOne": "N:1",
    "OneToMany": "1:N",
    "ManyToMany": "N:N",
    "OneToOne": "1:1",
}


def analyze_data_entities(
    project: ProjectInfo,
) -> tuple[list[DataEntity], list[DataRelationship]]:
    """Analyze a project for data entity classes and their relationships.

    Supports two detection strategies:
    1. JPA: @Entity annotated classes with @Table, @Column, @Id annotations
    2. MyBatis: classes extending BaseEntity/TreeEntity in domain packages,
       with column mappings from mapper XML files

    Returns a tuple of (entities, relationships).
    """
    entities: list[DataEntity] = []
    relationships: list[DataRelationship] = []

    # Strategy 1: JPA detection
    entities, relationships = _detect_jpa_entities(project)

    # Strategy 2: MyBatis fallback if JPA found nothing
    if not entities:
        entities, relationships = _detect_mybatis_entities(project)

    return entities, relationships


def _detect_jpa_entities(
    project: ProjectInfo,
) -> tuple[list[DataEntity], list[DataRelationship]]:
    """Detect JPA @Entity annotated classes."""
    entities: list[DataEntity] = []
    relationships: list[DataRelationship] = []

    for module in project.modules:
        java_src = module.path / "src" / "main" / "java"
        if not java_src.exists():
            logger.debug("Module %s has no src/main/java, skipping", module.name)
            continue

        for java_file in java_src.rglob("*.java"):
            try:
                java_class = parse_java_file(java_file)
            except Exception:
                logger.warning("Failed to parse %s", java_file)
                continue

            if java_class is None:
                continue

            metadata = extract_spring_metadata(java_class)
            if not metadata.is_entity:
                continue

            # Only count as JPA if it has the @Entity annotation explicitly
            if "Entity" not in java_class.annotations:
                continue

            data_entity = DataEntity(
                module_name=module.artifact_id or module.name,
                class_name=java_class.class_name,
                table_name=metadata.table_name,
                data_domain=module.name,
            )

            for field_info in java_class.fields:
                entity_field = _build_entity_field(field_info)
                data_entity.fields.append(entity_field)

                rel = _extract_relationship(
                    field_info, java_class.class_name
                )
                if rel:
                    relationships.append(rel)

            entities.append(data_entity)

    return entities, relationships


def _detect_mybatis_entities(
    project: ProjectInfo,
) -> tuple[list[DataEntity], list[DataRelationship]]:
    """Detect MyBatis-style domain entities using mapper XML and class heuristics."""
    entities: list[DataEntity] = []
    relationships: list[DataRelationship] = []

    for module in project.modules:
        java_src = module.path / "src" / "main" / "java"
        if not java_src.exists():
            continue

        # Parse mapper XMLs for this module to get column mappings
        mapper_data = parse_mapper_xmls(module.path)

        for java_file in java_src.rglob("*.java"):
            try:
                java_class = parse_java_file(java_file)
            except Exception:
                logger.warning("Failed to parse %s", java_file)
                continue

            if java_class is None:
                continue

            # Skip excluded utility classes
            if java_class.class_name in MYBATIS_EXCLUDED_CLASSES:
                continue

            # Determine if this is a MyBatis entity
            is_mybatis_entity = False
            table_name = ""

            # Signal 1: Class name matches a resultMap in mapper XML
            if java_class.class_name in mapper_data:
                is_mybatis_entity = True
                table_name = mapper_data[java_class.class_name].get("table_name", "")

            # Signal 2: Extends BaseEntity/TreeEntity
            if java_class.extends_class in MYBATIS_BASE_CLASSES:
                is_mybatis_entity = True

            # Signal 3: In a domain/ directory with a table name in Javadoc
            if not is_mybatis_entity:
                file_parts = java_file.parts
                if "domain" in file_parts or "entity" in file_parts:
                    javadoc_table = _extract_table_from_javadoc(java_class.documentation)
                    if javadoc_table:
                        is_mybatis_entity = True
                        table_name = javadoc_table

            if not is_mybatis_entity:
                continue

            # Extract table name (priority: mapper XML > Javadoc > camelCase conversion)
            if not table_name:
                table_name = _extract_table_from_javadoc(java_class.documentation)
            if not table_name:
                table_name = _camel_to_snake(java_class.class_name)

            # Build entity
            data_entity = DataEntity(
                module_name=module.artifact_id or module.name,
                class_name=java_class.class_name,
                table_name=table_name,
                data_domain=module.name,
            )

            # Build fields: merge Java fields with mapper XML column mappings
            mapper_columns = {}
            if java_class.class_name in mapper_data:
                for col in mapper_data[java_class.class_name].get("columns", []):
                    mapper_columns[col["property"]] = col

            for field_info in java_class.fields:
                field_name = field_info.get("name", "")

                # Skip static fields like serialVersionUID
                if field_name == "serialVersionUID":
                    continue

                java_type = field_info.get("type", "")
                mapper_col = mapper_columns.get(field_name)

                ef = EntityField(
                    name=field_name,
                    java_type=java_type,
                    column_name=mapper_col["column"] if mapper_col else _camel_to_snake(field_name),
                    is_primary_key=mapper_col["is_pk"] if mapper_col else False,
                )

                data_entity.fields.append(ef)

            # Only include entities that have real fields
            if data_entity.fields:
                entities.append(data_entity)

    return entities, relationships


def _build_entity_field(field_info: dict) -> EntityField:
    """Build an EntityField from a parsed field dict."""
    name = field_info.get("name", "")
    java_type = field_info.get("type", "")
    annotations = field_info.get("annotations", [])

    ef = EntityField(name=name, java_type=java_type)

    # Default column_name to the field name
    ef.column_name = name

    for ann in annotations:
        ann_name = ann.get("name", "")
        params = ann.get("params", {})

        if ann_name == "Id":
            ef.is_primary_key = True

        elif ann_name == "Column":
            col_name = params.get("name", "")
            if col_name:
                ef.column_name = col_name
            nullable = params.get("nullable", "")
            if nullable == "false":
                ef.is_nullable = False

        elif ann_name in ("ManyToOne", "OneToOne"):
            ef.is_foreign_key = True
            ef.fk_target_entity = java_type

    return ef


def _extract_relationship(
    field_info: dict, source_class: str
) -> DataRelationship | None:
    """Extract a DataRelationship if the field has a relationship annotation."""
    annotations = field_info.get("annotations", [])
    java_type = field_info.get("type", "")
    field_name = field_info.get("name", "")

    for ann in annotations:
        ann_name = ann.get("name", "")
        if ann_name in RELATIONSHIP_ANNOTATIONS:
            rel_type = RELATIONSHIP_ANNOTATIONS[ann_name]
            # For collection types, the target is the generic type param;
            # we approximate with the field type from the parser
            target_entity = java_type

            return DataRelationship(
                source_entity=source_class,
                target_entity=target_entity,
                relationship_type=rel_type,
                fk_field=field_name,
            )

    return None


def _extract_table_from_javadoc(documentation: str) -> str:
    """Extract table name from Javadoc comment."""
    if not documentation:
        return ""
    match = re.search(r'\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b', documentation)
    return match.group(1) if match else ""


def _camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case."""
    # Remove common prefixes
    for prefix in ("Sys", "Gen", "Qrtz"):
        if name.startswith(prefix) and len(name) > len(prefix):
            name = name[len(prefix):]
            name = prefix.lower() + "_" + name
            break

    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
