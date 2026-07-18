from pathlib import Path
from src.models.project import ProjectInfo, ApiEndpoint
from src.generators.excel_generator import create_workbook, add_sheet, save_workbook
from src.utils.naming import generate_encoding, camel_to_words
from src.i18n import t, get_headers

HEADERS = get_headers("aa04")


def generate_aa04(project: ProjectInfo, endpoints: list[ApiEndpoint], output_dir: Path, locale: str = "zh") -> Path:
    wb = create_workbook()
    headers = get_headers("aa04", locale)
    rows = []

    for idx, ep in enumerate(endpoints, 1):
        rows.append([
            generate_encoding("AF", idx),
            camel_to_words(ep.method_name),
            project.name,
            t("val.microservice_app", locale),
            ep.module_name,
            ep.module_name,
        ])

    add_sheet(wb, t("sheet.aa04", locale), headers, rows, locale=locale)
    return save_workbook(wb, output_dir / "AA-04_功能项分布清单.xlsx")
