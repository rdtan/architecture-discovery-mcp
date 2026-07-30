from pathlib import Path
from src.models.project import ProjectInfo, DataEntity, EntityField
from src.generators.excel_generator import create_workbook, add_sheet, save_workbook
from src.utils.naming import generate_encoding
from src.i18n import t, get_headers


def generate_da02(project: ProjectInfo, entities: list[DataEntity], output_dir: Path, locale: str = "zh") -> Path:
    wb = create_workbook()
    headers = get_headers("da02", locale)
    rows = []

    for entity_idx, entity in enumerate(entities, 1):
        data_domain = entity.data_domain or entity.module_name
        concept_entity_id = generate_encoding("DE", entity_idx)
        concept_entity_name = entity.class_name
        logical_entity_id = generate_encoding("DL", entity_idx)
        logical_entity_name = entity.class_name

        for field in entity.fields:
            attr_name = field.name
            attr_code = field.column_name if field.column_name else field.name
            data_type = field.java_type
            is_pk = t("val.yes", locale) if field.is_primary_key else t("val.no", locale)
            is_fk = t("val.yes", locale) if field.is_foreign_key else t("val.no", locale)
            is_not_null = t("val.yes", locale) if field.is_primary_key or not field.is_nullable else t("val.no", locale)

            rows.append([
                data_domain,
                concept_entity_id,
                concept_entity_name,
                logical_entity_id,
                logical_entity_name,
                attr_name,
                attr_code,
                data_type,
                is_pk,
                is_fk,
                is_not_null,
            ])

    add_sheet(wb, t("sheet.da02", locale), headers, rows, locale=locale)
    return save_workbook(wb, output_dir / "DA-02_逻辑实体清单.xlsx")
