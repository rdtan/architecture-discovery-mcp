"""Parse MyBatis mapper XML files to extract entity-column mappings and table names."""

import re
import logging
from pathlib import Path
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


def parse_mapper_xmls(module_path: Path) -> dict[str, dict]:
    """Parse all mapper XML files in a module and return entity metadata.

    Scans `src/main/resources/mapper/` for XML files containing
    `<resultMap>` definitions.

    Returns:
        Dict keyed by class name (short, e.g. "SysConfig"):
        {
            "table_name": "sys_config",
            "columns": [
                {"property": "configId", "column": "config_id", "is_pk": True},
                {"property": "configName", "column": "config_name", "is_pk": False},
                ...
            ]
        }
    """
    mapper_dir = module_path / "src" / "main" / "resources" / "mapper"
    if not mapper_dir.exists():
        return {}

    result: dict[str, dict] = {}

    for xml_file in mapper_dir.rglob("*.xml"):
        try:
            _parse_single_mapper(xml_file, result)
        except Exception as e:
            logger.warning("Failed to parse mapper XML %s: %s", xml_file, e)

    return result


def parse_mapper_relationships(module_path: Path) -> list[dict]:
    """Parse <association> and <collection> elements from mapper XMLs.

    Scans `src/main/resources/mapper/` for XML files and extracts
    entity relationships defined via MyBatis association/collection mappings.

    Returns:
        List of relationship dicts:
        [{"source_entity": "Order", "target_entity": "OrderItem",
          "relationship_type": "1:N", "property": "items", "column": "order_id"},
         {"source_entity": "Order", "target_entity": "Customer",
          "relationship_type": "N:1", "property": "customer", "column": "customer_id"}]
    """
    mapper_dir = module_path / "src" / "main" / "resources" / "mapper"
    if not mapper_dir.exists():
        return []

    relationships: list[dict] = []

    for xml_file in mapper_dir.rglob("*.xml"):
        try:
            _parse_single_mapper_relationships(xml_file, relationships)
        except Exception as e:
            logger.warning("Failed to parse mapper relationships in %s: %s", xml_file, e)

    return relationships


def _parse_single_mapper_relationships(xml_file: Path, relationships: list[dict]) -> None:
    """Parse a single mapper XML file for association/collection relationships."""
    content = xml_file.read_text(encoding="utf-8", errors="ignore")

    # Remove DOCTYPE to avoid XML parsing issues with DTD references
    content = re.sub(r'<!DOCTYPE[^>]*>', '', content)

    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        logger.debug("XML parse error in %s, skipping relationship parsing", xml_file)
        return

    for result_map in root.findall(".//resultMap"):
        type_name = result_map.get("type", "")
        if not type_name:
            continue

        # Strip package prefix to get short entity name
        source_entity = type_name.rsplit(".", 1)[-1]

        _parse_associations(result_map, source_entity, relationships)
        _parse_collections(result_map, source_entity, relationships)


def _parse_associations(result_map: ET.Element, source_entity: str, relationships: list[dict]) -> None:
    """Parse <association> elements (N:1 / many-to-one relationships)."""
    for assoc in result_map.findall("association"):
        java_type = assoc.get("javaType", "")
        prop = assoc.get("property", "")
        column = assoc.get("column", "")

        if not java_type or not prop:
            continue

        # Strip package prefix from javaType
        target_entity = java_type.rsplit(".", 1)[-1]

        relationships.append({
            "source_entity": source_entity,
            "target_entity": target_entity,
            "relationship_type": "N:1",
            "property": prop,
            "column": column,
        })


def _parse_collections(result_map: ET.Element, source_entity: str, relationships: list[dict]) -> None:
    """Parse <collection> elements (1:N / one-to-many relationships)."""
    for coll in result_map.findall("collection"):
        of_type = coll.get("ofType", "")
        prop = coll.get("property", "")
        column = coll.get("column", "")

        if not of_type or not prop:
            continue

        # Strip package prefix from ofType
        target_entity = of_type.rsplit(".", 1)[-1]

        relationships.append({
            "source_entity": source_entity,
            "target_entity": target_entity,
            "relationship_type": "1:N",
            "property": prop,
            "column": column,
        })


def _parse_single_mapper(xml_file: Path, result: dict[str, dict]) -> None:
    """Parse a single mapper XML file and populate the result dict."""
    content = xml_file.read_text(encoding="utf-8", errors="ignore")

    # Remove DOCTYPE to avoid XML parsing issues with DTD references
    content = re.sub(r'<!DOCTYPE[^>]*>', '', content)

    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        logger.debug("XML parse error in %s, falling back to regex", xml_file)
        _parse_mapper_regex(xml_file, result)
        return

    # Extract resultMap elements
    for result_map in root.findall(".//resultMap"):
        type_name = result_map.get("type", "")
        if not type_name:
            continue

        # Strip package prefix if present
        short_name = type_name.rsplit(".", 1)[-1] if "." in type_name else type_name

        columns: list[dict] = []

        for id_elem in result_map.findall("id"):
            prop = id_elem.get("property", "")
            col = id_elem.get("column", "")
            if prop and col:
                columns.append({"property": prop, "column": col, "is_pk": True})

        for result_elem in result_map.findall("result"):
            prop = result_elem.get("property", "")
            col = result_elem.get("column", "")
            if prop and col:
                columns.append({"property": prop, "column": col, "is_pk": False})

        # Extract table name from SQL statements in this file
        table_name = _extract_table_name(content, short_name)

        if short_name not in result or len(columns) > len(result[short_name].get("columns", [])):
            result[short_name] = {
                "table_name": table_name,
                "columns": columns,
            }


def _parse_mapper_regex(xml_file: Path, result: dict[str, dict]) -> None:
    """Fallback regex-based parsing for malformed XML files."""
    content = xml_file.read_text(encoding="utf-8", errors="ignore")

    # Find resultMap type
    for match in re.finditer(
        r'<resultMap\s+type="([^"]+)"\s+id="([^"]+)"', content
    ):
        type_name = match.group(1)
        short_name = type_name.rsplit(".", 1)[-1] if "." in type_name else type_name

        columns: list[dict] = []

        # Find id and result elements (simplified regex)
        for col_match in re.finditer(
            r'<(id|result)\s+property="(\w+)"\s+column="(\w+)"', content
        ):
            tag = col_match.group(1)
            prop = col_match.group(2)
            col = col_match.group(3)
            columns.append({"property": prop, "column": col, "is_pk": tag == "id"})

        table_name = _extract_table_name(content, short_name)

        if short_name not in result or len(columns) > len(result[short_name].get("columns", [])):
            result[short_name] = {
                "table_name": table_name,
                "columns": columns,
            }


def _extract_table_name(content: str, class_name: str) -> str:
    """Extract table name from SQL statements in mapper XML content.

    Looks for patterns like 'from table_name' or 'into table_name'
    in SQL blocks.
    """
    # Common patterns: "from sys_config", "into sys_config", "update sys_config"
    table_patterns = re.findall(
        r'\b(?:from|into|update)\s+([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b',
        content,
        re.IGNORECASE,
    )

    if table_patterns:
        # Return the most frequently referenced table name
        from collections import Counter
        counts = Counter(t.lower() for t in table_patterns)
        return counts.most_common(1)[0][0]

    return ""
