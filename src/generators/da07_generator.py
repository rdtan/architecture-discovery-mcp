from pathlib import Path
from src.models.project import ProjectInfo, EnumDefinition
from src.generators.excel_generator import create_workbook, add_sheet, save_workbook
from src.utils.naming import generate_encoding
from src.i18n import t, get_headers


def generate_da07(project: ProjectInfo, enums: list[EnumDefinition], output_dir: Path, locale: str = "zh") -> Path:
    wb = create_workbook()
    headers = get_headers("da07", locale)
    rows = []

    for enum_idx, enum_def in enumerate(enums, 1):
        enum_type_id = generate_encoding("DD", enum_idx)

        for value in enum_def.values:
            enum_cn_name = value.get("label") or value.get("name", "")
            enum_value = value.get("value") or value.get("name", "")
            enum_en_name = value.get("name", "")

            rows.append([
                enum_type_id,
                enum_def.class_name,
                enum_cn_name,
                enum_value,
                enum_en_name,
                t("val.enabled", locale),
                "",
            ])

    add_sheet(wb, t("sheet.da07", locale), headers, rows, locale=locale)
    return save_workbook(wb, output_dir / "DA-07_数据字典表.xlsx")
