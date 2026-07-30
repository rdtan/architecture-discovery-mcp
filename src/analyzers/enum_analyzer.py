import logging
import re
from pathlib import Path

from src.models.project import ProjectInfo, EnumDefinition

logger = logging.getLogger(__name__)

# Directory names that commonly hold enum classes
ENUM_DIR_NAMES = {"enum", "enums", "constant", "constants", "enumerations"}


def analyze_enums(project: ProjectInfo) -> list[EnumDefinition]:
    """Extract Java enum definitions from all modules in the project.

    Scans each module's Java source tree for enum classes by:
    1. Looking in well-known enum directories (enums/, constant/, etc.)
    2. Scanning all .java files for the `enum` keyword

    Returns a list of EnumDefinition dataclass instances.
    """
    enums: list[EnumDefinition] = []

    for module in project.modules:
        java_src = module.path / "src" / "main" / "java"
        if not java_src.exists():
            continue

        seen_files: set[Path] = set()

        # Strategy 1: files in well-known enum directories
        for java_file in java_src.rglob("*.java"):
            parent_name = java_file.parent.name.lower()
            if parent_name in ENUM_DIR_NAMES:
                seen_files.add(java_file)

        # Strategy 2: scan all .java files for enum keyword
        for java_file in java_src.rglob("*.java"):
            if java_file not in seen_files:
                try:
                    content = java_file.read_text(encoding="utf-8", errors="ignore")
                except Exception as e:
                    logger.warning("Failed to read %s: %s", java_file, e)
                    continue
                if re.search(r'\benum\s+\w+', content):
                    seen_files.add(java_file)

        # Parse each discovered enum file
        for java_file in sorted(seen_files):
            try:
                content = java_file.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:
                logger.warning("Failed to read %s: %s", java_file, e)
                continue

            try:
                parsed = _parse_enum(content)
            except Exception as e:
                logger.warning("Failed to parse enum in %s: %s", java_file, e)
                continue

            if parsed is None:
                continue

            enum_name, values = parsed
            enums.append(
                EnumDefinition(
                    module_name=module.artifact_id or module.name,
                    class_name=enum_name,
                    values=values,
                )
            )

    return enums


def _parse_enum(content: str) -> tuple[str, list[dict]] | None:
    """Parse enum constants from Java source content.

    Returns (enum_name, values_list) or None if no enum found.
    """
    # Find enum declaration and its body
    enum_match = re.search(r'enum\s+(\w+)[^{]*\{(.*?)(?:;|})', content, re.DOTALL)
    if not enum_match:
        return None

    enum_name = enum_match.group(1)
    body = enum_match.group(2).strip()

    if not body:
        return enum_name, []

    values: list[dict] = []
    # Split by commas that are not inside parentheses
    constants = _split_enum_constants(body)

    for ordinal, const_text in enumerate(constants):
        const_text = const_text.strip()
        if not const_text:
            continue

        # Match: CONSTANT_NAME or CONSTANT_NAME(args...)
        const_match = re.match(r'(\w+)\s*(?:\(([^)]*)\))?', const_text)
        if not const_match:
            continue

        name = const_match.group(1)
        # Skip Java keywords that might appear in enum body
        if name in ("private", "public", "protected", "static", "final",
                    "abstract", "int", "String", "void", "return", "this"):
            continue

        args_str = const_match.group(2)
        value = str(ordinal)
        label = ""

        if args_str:
            args = _parse_constructor_args(args_str)
            if len(args) >= 1:
                value = args[0]
            if len(args) >= 2:
                label = args[1]

        values.append({"name": name, "value": value, "label": label})

    return enum_name, values


def _split_enum_constants(body: str) -> list[str]:
    """Split enum body into individual constant declarations.

    Handles commas inside parentheses by tracking nesting depth.
    """
    parts: list[str] = []
    current = ""
    depth = 0

    for ch in body:
        if ch == '(':
            depth += 1
            current += ch
        elif ch == ')':
            depth -= 1
            current += ch
        elif ch == ',' and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += ch

    if current.strip():
        parts.append(current)

    return parts


def _parse_constructor_args(args_str: str) -> list[str]:
    """Parse constructor arguments, extracting string literal values.

    Returns a list of argument values (unquoted for strings).
    """
    args: list[str] = []
    current = ""
    in_string = False
    escape_next = False

    for ch in args_str:
        if escape_next:
            current += ch
            escape_next = False
            continue
        if ch == '\\' and in_string:
            escape_next = True
            current += ch
            continue
        if ch == '"':
            in_string = not in_string
            current += ch
            continue
        if ch == ',' and not in_string:
            args.append(_clean_arg(current.strip()))
            current = ""
            continue
        current += ch

    if current.strip():
        args.append(_clean_arg(current.strip()))

    return args


def _clean_arg(arg: str) -> str:
    """Remove surrounding quotes from a string argument."""
    if len(arg) >= 2 and arg.startswith('"') and arg.endswith('"'):
        return arg[1:-1]
    return arg
