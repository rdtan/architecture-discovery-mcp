"""SQL field-level lineage analyzer.

Parses MyBatis mapper XML files to extract field-level data lineage from:
1. INSERT INTO ... SELECT ... — maps source columns to target columns
2. SELECT with table aliases — maps source table.column to result columns
"""

import re
import logging
from pathlib import Path
from xml.etree import ElementTree as ET

import sqlparse
from sqlparse.sql import IdentifierList, Identifier

from src.models.project import ProjectInfo, FieldLineage

logger = logging.getLogger(__name__)


def analyze_sql_lineage(project: ProjectInfo) -> list[FieldLineage]:
    """Scan MyBatis mapper XMLs for SQL-based field lineage.

    Detects:
    - INSERT INTO target_table (col1, col2) SELECT src.col1, src.col2 FROM source_table src
    - SELECT with JOINs: identifies which table each column comes from

    Returns FieldLineage records with confidence=0.7, evidence="SQL SELECT".
    """
    lineages: list[FieldLineage] = []

    for module in project.modules:
        mapper_dir = module.path / "src" / "main" / "resources" / "mapper"
        if not mapper_dir.exists():
            continue

        for xml_file in mapper_dir.rglob("*.xml"):
            try:
                file_lineages = _process_mapper_file(xml_file, module.name)
                lineages.extend(file_lineages)
            except Exception as e:
                logger.warning("Failed to parse mapper XML %s: %s", xml_file, e)

    return lineages


def _process_mapper_file(xml_file: Path, module_name: str) -> list[FieldLineage]:
    """Process a single mapper XML file for SQL lineage."""
    content = xml_file.read_text(encoding="utf-8", errors="ignore")

    # Remove DOCTYPE to avoid XML parsing issues with DTD references
    content = re.sub(r'<!DOCTYPE[^>]*>', '', content)

    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        logger.debug("XML parse error in %s, skipping SQL lineage", xml_file)
        return []

    lineages: list[FieldLineage] = []
    source_file = str(xml_file)

    # Process <insert>, <select>, <update> elements
    for tag in ("insert", "select", "update"):
        for element in root.findall(f".//{tag}"):
            sql = _extract_sql_from_element(element)
            if not sql:
                continue

            # Strip MyBatis placeholders
            sql = re.sub(r'[#$]\{[^}]*\}', "'?'", sql)

            if tag == "insert":
                insert_lineages = _parse_insert_select(sql, module_name, source_file)
                lineages.extend(insert_lineages)

            # SELECT with aliases (from any statement type that contains SELECT)
            if "SELECT" in sql.upper():
                select_lineages = _parse_select_aliases(sql, module_name, source_file)
                lineages.extend(select_lineages)

    return lineages


def _extract_sql_from_element(element: ET.Element) -> str:
    """Extract raw SQL text from a MyBatis XML element, stripping dynamic tags."""
    # itertext() gets all text content including text inside child elements
    parts = list(element.itertext())
    sql = " ".join(parts)
    # Normalize whitespace
    sql = re.sub(r'\s+', ' ', sql).strip()
    return sql


def _parse_insert_select(sql: str, module_name: str, source_file: str) -> list[FieldLineage]:
    """Parse INSERT INTO ... SELECT ... pattern.

    Extracts:
    - Target table and columns from INSERT INTO table (col1, col2, ...)
    - Source expressions from SELECT expr1, expr2, ... FROM source_table
    """
    lineages: list[FieldLineage] = []

    # Match INSERT INTO table_name (columns) SELECT ...
    insert_match = re.match(
        r'\s*INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)\s*SELECT\s+(.+?)\s+FROM\s+(.+)',
        sql,
        re.IGNORECASE | re.DOTALL,
    )
    if not insert_match:
        return []

    target_table = insert_match.group(1)
    target_cols_raw = insert_match.group(2)
    select_exprs_raw = insert_match.group(3)
    from_clause = insert_match.group(4)

    # Parse target columns
    target_cols = [c.strip() for c in target_cols_raw.split(",")]

    # Parse source expressions from SELECT clause
    source_exprs = _parse_select_columns(select_exprs_raw)

    # Extract table aliases from FROM/JOIN clause
    aliases = _extract_table_aliases("FROM " + from_clause)

    # Map each source expression to a target column
    for i, target_col in enumerate(target_cols):
        if i >= len(source_exprs):
            break

        source_expr = source_exprs[i]
        source_entity, source_field = _resolve_column_source(source_expr, aliases)

        if source_entity and source_field:
            lineages.append(FieldLineage(
                source_system=module_name,
                source_entity=source_entity,
                source_field=source_field,
                target_system=module_name,
                target_entity=target_table,
                target_field=target_col,
                mapping_type="direct",
                transform_expr="",
                trigger_mode="realtime",
                confidence=0.7,
                evidence="SQL SELECT",
                source_file=source_file,
                source_line=0,
            ))

    return lineages


def _parse_select_aliases(sql: str, module_name: str, source_file: str) -> list[FieldLineage]:
    """Parse SELECT with table aliases to extract column-to-table mappings.

    For SELECT o.id as orderId, c.name as customerName FROM orders o JOIN customers c ...
    produces lineage: orders.id -> result.orderId, customers.name -> result.customerName
    """
    lineages: list[FieldLineage] = []

    # Find the SELECT ... FROM boundary
    select_match = re.match(
        r'\s*SELECT\s+(.+?)\s+FROM\s+(.+)',
        sql,
        re.IGNORECASE | re.DOTALL,
    )
    if not select_match:
        return []

    select_clause = select_match.group(1)
    from_clause = select_match.group(2)

    # Extract table aliases
    aliases = _extract_table_aliases("FROM " + from_clause)
    if not aliases:
        return []

    # Parse individual column expressions
    columns = _parse_select_columns(select_clause)

    for col_expr in columns:
        # Check if column has alias.column pattern
        source_entity, source_field = _resolve_column_source(col_expr, aliases)
        if not source_entity or not source_field:
            continue

        # Determine target field name (alias after AS, or the column name itself)
        target_field = _get_column_alias(col_expr) or source_field

        lineages.append(FieldLineage(
            source_system=module_name,
            source_entity=source_entity,
            source_field=source_field,
            target_system=module_name,
            target_entity="(result)",
            target_field=target_field,
            mapping_type="direct",
            transform_expr="",
            trigger_mode="realtime",
            confidence=0.7,
            evidence="SQL SELECT",
            source_file=source_file,
            source_line=0,
        ))

    return lineages


def _parse_select_columns(select_clause: str) -> list[str]:
    """Parse SELECT column list into individual expressions.

    Handles commas inside function calls correctly using sqlparse.
    """
    # Use sqlparse to tokenize
    parsed = sqlparse.parse(f"SELECT {select_clause}")[0]

    columns: list[str] = []

    # Find the first IdentifierList or single Identifier after SELECT
    for token in parsed.tokens:
        if isinstance(token, IdentifierList):
            for identifier in token.get_identifiers():
                columns.append(str(identifier).strip())
            return columns
        elif isinstance(token, Identifier):
            columns.append(str(token).strip())
            return columns

    # Fallback: simple comma split
    if not columns:
        columns = [c.strip() for c in select_clause.split(",")]

    return columns


def _extract_table_aliases(sql: str) -> dict[str, str]:
    """Extract table aliases from FROM/JOIN clauses.

    Returns {alias: table_name}, e.g. {"o": "orders", "c": "customers"}
    """
    aliases: dict[str, str] = {}

    # Match patterns like: FROM/JOIN table_name [AS] alias
    pattern = r'(?:FROM|JOIN)\s+(\w+)\s+(?:AS\s+)?(\w+)'
    for match in re.finditer(pattern, sql, re.IGNORECASE):
        table_name = match.group(1)
        alias = match.group(2)

        # Skip keywords that could be mistaken for aliases
        if alias.upper() in ('ON', 'WHERE', 'SET', 'LEFT', 'RIGHT', 'INNER',
                             'OUTER', 'CROSS', 'JOIN', 'AND', 'OR', 'GROUP',
                             'ORDER', 'HAVING', 'LIMIT', 'UNION'):
            continue

        aliases[alias] = table_name

    # Also add table names without aliases (table maps to itself)
    simple_pattern = r'(?:FROM|JOIN)\s+(\w+)(?:\s*(?:ON|WHERE|$))'
    for match in re.finditer(simple_pattern, sql, re.IGNORECASE):
        table_name = match.group(1)
        if table_name not in aliases.values():
            aliases[table_name] = table_name

    return aliases


def _resolve_column_source(expr: str, aliases: dict[str, str]) -> tuple[str, str]:
    """Resolve a column expression to (table_name, column_name).

    Given "o.order_no" and aliases {"o": "orders"}, returns ("orders", "order_no").
    Given "order_no" with no alias prefix, returns ("", "order_no").
    """
    # Strip any AS alias from the expression
    clean_expr = re.split(r'\s+[Aa][Ss]\s+', expr)[0].strip()
    # Also strip trailing alias without AS keyword
    # e.g. "o.id orderId" -> need to handle carefully
    # Only strip if there's a space and the part after is a simple identifier
    parts_space = clean_expr.split()
    if len(parts_space) == 2 and re.match(r'^\w+$', parts_space[1]):
        clean_expr = parts_space[0]

    # Check for alias.column pattern
    dot_match = re.match(r'^(\w+)\.(\w+)$', clean_expr)
    if dot_match:
        alias = dot_match.group(1)
        column = dot_match.group(2)
        table = aliases.get(alias, alias)
        return (table, column)

    # No alias prefix — can't determine source table
    return ("", clean_expr)


def _get_column_alias(expr: str) -> str:
    """Get the alias of a column expression (the part after AS or the trailing name).

    "o.id as orderId" -> "orderId"
    "o.id orderId" -> "orderId"
    "o.id" -> ""
    """
    # Check for AS keyword
    as_match = re.search(r'\s+[Aa][Ss]\s+(\w+)\s*$', expr)
    if as_match:
        return as_match.group(1)

    # Check for trailing alias (space-separated, no dots)
    parts = expr.strip().split()
    if len(parts) == 2 and re.match(r'^\w+$', parts[1]) and '.' not in parts[1]:
        return parts[1]

    return ""
