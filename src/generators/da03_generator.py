from pathlib import Path
from src.models.project import ProjectInfo, DataEntity
from src.generators.excel_generator import create_workbook, add_sheet, save_workbook
from src.utils.naming import generate_encoding
from src.i18n import t, get_headers


def generate_da03(project: ProjectInfo, entities: list[DataEntity], output_dir: Path, locale: str = "zh") -> Path:
    wb = create_workbook()
    headers = get_headers("da03", locale)
    rows = []

    for entity_idx, entity in enumerate(entities, 1):
        data_domain = entity.data_domain or entity.module_name
        logical_entity_id = generate_encoding("DL", entity_idx)
        logical_entity_name = entity.class_name
        physical_entity_id = generate_encoding("DP", entity_idx)
        physical_entity_name = entity.class_name

        for field in entity.fields:
            field_name = field.name
            field_code = field.column_name if field.column_name else field.name
            data_type = field.java_type

            rows.append([
                data_domain,
                logical_entity_id,
                logical_entity_name,
                physical_entity_id,
                physical_entity_name,
                field_name,
                field_code,
                data_type,
            ])

    add_sheet(wb, t("sheet.da03", locale), headers, rows, locale=locale)
    return save_workbook(wb, output_dir / "DA-03_物理实体清单.xlsx")
