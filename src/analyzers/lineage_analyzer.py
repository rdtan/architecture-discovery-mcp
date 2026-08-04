"""MapStruct field lineage analyzer.

Scans for @Mapper interfaces and extracts @Mapping annotations
to produce field-level lineage records.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from src.models.project import ProjectInfo
from src.parsers.java_parser import parse_java_file, JavaClass, JavaMethod

logger = logging.getLogger(__name__)


try:
    from src.models.project import FieldLineage
except ImportError:

    @dataclass
    class FieldLineage:
        source_system: str
        source_entity: str
        source_field: str
        target_system: str
        target_entity: str
        target_field: str
        mapping_type: str
        transform_expr: str = ""
        trigger_mode: str = "realtime"
        confidence: float = 1.0
        evidence: str = ""
        source_file: str = ""
        source_line: int = 0


def analyze_mapstruct_lineage(project: ProjectInfo) -> list[FieldLineage]:
    """Scan project for MapStruct @Mapper interfaces and extract field mappings.

    Detection:
    1. Find interfaces annotated with @Mapper
    2. For each method, extract @Mapping(source="x", target="y") annotations
    3. Produce FieldLineage records with confidence=1.0 for explicit @Mapping.

    Returns list of FieldLineage records found across all modules.
    """
    lineages: list[FieldLineage] = []

    for module in project.modules:
        java_src = module.path / "src" / "main" / "java"
        if not java_src.exists():
            continue

        for java_file in java_src.rglob("*.java"):
            java_class = parse_java_file(java_file)
            if java_class is None:
                continue

            if not _is_mapper_interface(java_class):
                continue

            relative_path = str(java_file.relative_to(module.path))
            module_lineages = _extract_mappings_from_class(
                java_class, module.name, relative_path
            )
            lineages.extend(module_lineages)

    return lineages


def _is_mapper_interface(java_class: JavaClass) -> bool:
    """Check if a JavaClass is a MapStruct @Mapper interface."""
    if not java_class.is_interface:
        return False
    return "Mapper" in java_class.annotations


def _extract_mappings_from_class(
    java_class: JavaClass, module_name: str, source_file: str
) -> list[FieldLineage]:
    """Extract FieldLineage records from all methods of a @Mapper interface."""
    lineages: list[FieldLineage] = []

    for method in java_class.methods:
        source_entity = _infer_source_entity(method)
        target_entity = _infer_target_entity(method)

        mapping_annotations = [
            ann for ann in method.annotations if ann.get("name") == "Mapping"
        ]

        for ann in mapping_annotations:
            params = ann.get("params", {})
            source_field = params.get("source", "")
            target_field = params.get("target", "")

            if source_field and target_field:
                lineage = FieldLineage(
                    source_system=module_name,
                    source_entity=source_entity,
                    source_field=source_field,
                    target_system=module_name,
                    target_entity=target_entity,
                    target_field=target_field,
                    mapping_type="direct",
                    transform_expr="",
                    trigger_mode="realtime",
                    confidence=1.0,
                    evidence="MapStruct @Mapping",
                    source_file=source_file,
                    source_line=0,
                )
                lineages.append(lineage)

    return lineages


def _infer_source_entity(method: JavaMethod) -> str:
    """Infer source entity from the first method parameter type."""
    if method.parameters:
        return method.parameters[0].get("type", "")
    return ""


def _infer_target_entity(method: JavaMethod) -> str:
    """Infer target entity from the method return type."""
    return method.return_type or ""
