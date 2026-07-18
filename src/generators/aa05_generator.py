from pathlib import Path
from src.models.project import ProjectInfo, Integration
from src.generators.excel_generator import create_workbook, add_sheet, save_workbook
from src.utils.naming import generate_encoding
from src.i18n import t, get_headers

HEADERS = get_headers("aa05")


def generate_aa05(project: ProjectInfo, integrations: list[Integration], output_dir: Path, locale: str = "zh") -> Path:
    wb = create_workbook()
    headers = get_headers("aa05", locale)
    rows = []

    module_names = {m.name for m in project.modules}

    for idx, intg in enumerate(integrations, 1):
        is_cross_domain = intg.target_module not in module_names
        rows.append([
            generate_encoding("AI", idx),
            intg.source_module,
            intg.target_module,
            intg.integration_type.value,
            intg.interface_name,
            ", ".join(intg.methods),
            ", ".join(intg.data_entities),
            t("val.yes", locale) if is_cross_domain else t("val.no", locale),
        ])

    add_sheet(wb, t("sheet.aa05", locale), headers, rows, locale=locale)
    return save_workbook(wb, output_dir / "AA-05_应用集成清单.xlsx")
