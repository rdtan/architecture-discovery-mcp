from pathlib import Path
from src.models.project import ProjectInfo, DataEntity
from src.generators.excel_generator import create_workbook, add_sheet, save_workbook
from src.utils.naming import generate_encoding
from src.i18n import t, get_headers


# CRUD operation to translation key mapping
OPERATION_KEYS = {
    "C": "val.create",
    "R": "val.read",
    "U": "val.update",
    "D": "val.delete",
}


def generate_da06(
    project: ProjectInfo,
    entities: list[DataEntity],
    crud_records: list[dict],
    output_dir: Path,
    locale: str = "zh",
) -> Path:
    """Generate DA-06 Table-Function Relationship spreadsheet.

    Produces one row per CRUD record, mapping database tables to the application
    functions that create, read, update, or delete them.

    Args:
        project: The scanned project info.
        entities: List of DataEntity objects.
        crud_records: List of CRUD relationship dicts from analyze_crud().
        output_dir: Directory to write the output file.
        locale: Output language ("zh" or "en").

    Returns:
        Path to the generated .xlsx file.
    """
    wb = create_workbook()
    headers = get_headers("da06", locale)
    rows = []

    # Build entity lookup: class_name -> (table_name, 1-based index)
    entity_lookup: dict[str, tuple[str, int]] = {}
    for idx, entity in enumerate(entities, 1):
        entity_lookup[entity.class_name] = (entity.table_name, idx)

    for record in crud_records:
        entity_name = record.get("entity", "")
        lookup = entity_lookup.get(entity_name)

        # Skip records where entity is not found in the entities list
        if lookup is None:
            continue

        table_name, table_idx = lookup

        # Generate table encoding
        table_id = generate_encoding("DT", table_idx)

        # Translate operation type
        operation = record.get("operation", "")
        operation_key = OPERATION_KEYS.get(operation, "")
        operation_display = t(operation_key, locale) if operation_key else operation

        rows.append([
            project.name,
            table_id,
            table_name,
            operation_display,
            record.get("app_name", ""),
            record.get("module", ""),
            record.get("function", ""),
        ])

    add_sheet(wb, t("sheet.da06", locale), headers, rows, locale=locale)
    return save_workbook(wb, output_dir / "DA-06_库表-功能子项关系.xlsx")
