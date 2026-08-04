"""Setter/getter chain and BeanUtils.copyProperties lineage analyzer.

Scans Java files for field-level mappings from:
1. Setter/getter chains: dto.setName(entity.getName()) -> maps entity.name -> dto.name
2. BeanUtils.copyProperties(source, target) -> maps all same-name fields from source to target
"""

import logging
import re
from pathlib import Path

from src.models.project import (
    ProjectInfo,
    DataEntity,
    EntityField,
    FieldLineage,
)
from src.parsers.java_parser import parse_java_file

logger = logging.getLogger(__name__)

# Pattern to match a getter call in an argument string: qualifier.getField()
# Simple form: order.getName()
_GETTER_PATTERN_SIMPLE = re.compile(r"^(\w+)\.(get(\w+))\(\)$")

# javalang repr form: MethodInvocation(..., member=getXxx, ..., qualifier=yyy, ...)
_GETTER_PATTERN_REPR = re.compile(
    r"MethodInvocation\(.*?member=(get\w+).*?qualifier=(\w+).*?\)"
)

# MemberReference repr form: MemberReference(member=xxx, ..., qualifier=, ...)
_MEMBER_REF_PATTERN = re.compile(
    r"MemberReference\(.*?member=(\w+).*?\)"
)


def _extract_member_name(arg_str: str) -> str:
    """Extract the variable name from an argument string.

    Handles both simple form ('dto') and javalang repr form
    ('MemberReference(member=dto, ...)').
    """
    match = _MEMBER_REF_PATTERN.search(arg_str)
    if match:
        return match.group(1)
    # Simple form: just a variable name
    return arg_str.split(".")[0].strip()


def analyze_setter_getter_lineage(
    project: ProjectInfo, entities: list[DataEntity]
) -> list[FieldLineage]:
    """Detect field-level lineage from setter/getter chains and BeanUtils.copyProperties.

    Scans all Java files in each module, parses method bodies, and:
    1. Identifies setter(getter()) patterns: dto.setX(entity.getY()) -> field mapping
    2. Identifies BeanUtils.copyProperties(src, tgt) -> all same-name fields mapped

    Returns FieldLineage records.
    """
    lineages: list[FieldLineage] = []

    # Build entity lookup: class_name -> DataEntity
    entity_map: dict[str, DataEntity] = {}
    for entity in entities:
        entity_map[entity.class_name] = entity

    for module in project.modules:
        java_src = module.path / "src" / "main" / "java"
        if not java_src.exists():
            continue

        for java_file in java_src.rglob("*.java"):
            java_class = parse_java_file(java_file)
            if java_class is None:
                continue

            relative_path = str(java_file.relative_to(module.path))

            for method in java_class.methods:
                if method.body is None:
                    continue

                body = method.body
                invocations = body.get("invocations", [])
                local_variables = body.get("local_variables", [])

                # Build variable type map from locals and method parameters
                var_type_map: dict[str, str] = {}
                for lv in local_variables:
                    var_type_map[lv["name"]] = lv["type_name"]
                for param in method.parameters:
                    var_type_map[param["name"]] = param["type"]

                # Detect setter/getter chains
                setter_lineages = _detect_setter_getter(
                    invocations, var_type_map, module.name, relative_path
                )
                lineages.extend(setter_lineages)

                # Detect BeanUtils.copyProperties
                beanutils_lineages = _detect_beanutils_copy(
                    invocations, var_type_map, entity_map, module.name, relative_path
                )
                lineages.extend(beanutils_lineages)

    return lineages


def _detect_setter_getter(
    invocations: list[dict],
    var_type_map: dict[str, str],
    module_name: str,
    source_file: str,
) -> list[FieldLineage]:
    """Detect setter(getter()) patterns and produce FieldLineage records."""
    lineages: list[FieldLineage] = []

    for inv in invocations:
        method_name = inv.get("method_name", "")
        qualifier = inv.get("qualifier", "")
        arguments = inv.get("arguments", [])
        line_number = inv.get("line_number", 0)

        # Must be a setter call: setXxx(...)
        if not method_name.startswith("set") or len(method_name) <= 3:
            continue
        if not qualifier:
            continue
        if not arguments:
            continue

        # Extract target field from setter name
        target_field = method_name[3:]  # strip "set"
        target_field = target_field[0].lower() + target_field[1:]  # lowercase first char

        # Check if argument is a getter call
        arg = arguments[0].strip()

        # Try simple form first: order.getName()
        match = _GETTER_PATTERN_SIMPLE.match(arg)
        if match:
            source_qualifier = match.group(1)
            source_field_raw = match.group(3)  # e.g. "Id", "CustomerName"
            source_field = source_field_raw[0].lower() + source_field_raw[1:]
        else:
            # Try javalang repr form: MethodInvocation(...member=getXxx...qualifier=yyy...)
            match = _GETTER_PATTERN_REPR.search(arg)
            if not match:
                continue
            getter_name = match.group(1)  # e.g. "getId"
            source_qualifier = match.group(2)  # e.g. "order"
            if not getter_name.startswith("get") or len(getter_name) <= 3:
                continue
            source_field_raw = getter_name[3:]  # strip "get"
            source_field = source_field_raw[0].lower() + source_field_raw[1:]

        # Resolve types
        target_type = var_type_map.get(qualifier, qualifier)
        source_type = var_type_map.get(source_qualifier, source_qualifier)

        lineage = FieldLineage(
            source_system=module_name,
            source_entity=source_type,
            source_field=source_field,
            target_system=module_name,
            target_entity=target_type,
            target_field=target_field,
            mapping_type="direct",
            transform_expr="",
            trigger_mode="realtime",
            confidence=1.0,
            evidence="setter/getter chain",
            source_file=source_file,
            source_line=line_number,
        )
        lineages.append(lineage)

    return lineages


def _detect_beanutils_copy(
    invocations: list[dict],
    var_type_map: dict[str, str],
    entity_map: dict[str, DataEntity],
    module_name: str,
    source_file: str,
) -> list[FieldLineage]:
    """Detect BeanUtils.copyProperties(src, tgt) and produce FieldLineage records."""
    lineages: list[FieldLineage] = []

    for inv in invocations:
        qualifier = inv.get("qualifier", "")
        method_name = inv.get("method_name", "")
        arguments = inv.get("arguments", [])
        line_number = inv.get("line_number", 0)

        if qualifier != "BeanUtils" or method_name != "copyProperties":
            continue
        if len(arguments) < 2:
            continue

        source_var = _extract_member_name(arguments[0].strip())
        target_var = _extract_member_name(arguments[1].strip())

        # Resolve types
        source_type = var_type_map.get(source_var, source_var)
        target_type = var_type_map.get(target_var, target_var)

        # Look up entities
        source_entity = entity_map.get(source_type)
        target_entity = entity_map.get(target_type)

        if source_entity is None or target_entity is None:
            # Still record that we saw a copy but can't resolve fields
            continue

        # Find overlapping field names
        source_fields = {f.name for f in source_entity.fields}
        target_fields = {f.name for f in target_entity.fields}
        common_fields = source_fields & target_fields

        for field_name in sorted(common_fields):
            lineage = FieldLineage(
                source_system=module_name,
                source_entity=source_type,
                source_field=field_name,
                target_system=module_name,
                target_entity=target_type,
                target_field=field_name,
                mapping_type="direct",
                transform_expr="",
                trigger_mode="realtime",
                confidence=0.7,
                evidence="BeanUtils.copyProperties",
                source_file=source_file,
                source_line=line_number,
            )
            lineages.append(lineage)

    return lineages
