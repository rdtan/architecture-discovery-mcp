from pathlib import Path
from src.models.project import ProjectInfo, DataEntity
from src.generators.excel_generator import create_workbook, add_sheet, save_workbook
from src.utils.naming import generate_encoding
from src.i18n import t, get_headers


def generate_da04(project: ProjectInfo, entities: list[DataEntity], output_dir: Path, locale: str = "zh") -> Path:
    wb = create_workbook()
    headers = get_headers("da04", locale)
    rows = []

    for entity_idx, entity in enumerate(entities, 1):
        data_domain = entity.data_domain or entity.module_name
        physical_entity_id = generate_encoding("DP", entity_idx)
        physical_entity_name = entity.class_name
        table_id = generate_encoding("DT", entity_idx)
        table_name = entity.table_name

        for field in entity.fields:
            field_name = field.name
            field_code = field.column_name if field.column_name else field.name

            rows.append([
                data_domain,
                physical_entity_id,
                physical_entity_name,
                table_id,
                table_name,
                field_name,
                field_code,
                project.name,
                "",  # db_type - unknown from scan
            ])

    add_sheet(wb, t("sheet.da04", locale), headers, rows, locale=locale)
    return save_workbook(wb, output_dir / "DA-04_库表清单.xlsx")
