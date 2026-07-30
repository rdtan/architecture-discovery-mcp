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


def generate_da05(
    project: ProjectInfo,
    entities: list[DataEntity],
    crud_records: list[dict],
    output_dir: Path,
    locale: str = "zh",
) -> Path:
    """Generate DA-05 Data Source List spreadsheet.

    Produces one row per CRUD record, mapping entities to the application
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
    headers = get_headers("da05", locale)
    rows = []

    # Build entity index lookup: class_name -> 1-based index
    entity_index: dict[str, int] = {}
    for idx, entity in enumerate(entities, 1):
        entity_index[entity.class_name] = idx

    for record in crud_records:
        entity_name = record.get("entity", "")
        entity_idx = entity_index.get(entity_name, 0)

        # Generate encoding IDs
        concept_entity_id = generate_encoding("DE", entity_idx) if entity_idx else ""
        logical_entity_id = generate_encoding("DL", entity_idx) if entity_idx else ""

        # Translate operation type
        operation = record.get("operation", "")
        operation_key = OPERATION_KEYS.get(operation, "")
        operation_display = t(operation_key, locale) if operation_key else operation

        rows.append([
            record.get("data_domain", ""),
            concept_entity_id,
            entity_name,
            logical_entity_id,
            entity_name,
            operation_display,
            record.get("app_name", ""),
            record.get("module", ""),
            record.get("function", ""),
        ])

    add_sheet(wb, t("sheet.da05", locale), headers, rows, locale=locale)
    return save_workbook(wb, output_dir / "DA-05_数据源清单.xlsx")
