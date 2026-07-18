from pathlib import Path
from src.models.project import ProjectInfo, ApiEndpoint
from src.generators.excel_generator import create_workbook, add_sheet, save_workbook
from src.utils.naming import generate_encoding, camel_to_words
from src.i18n import t, get_headers

HEADERS = get_headers("aa02")


def generate_aa02(project: ProjectInfo, endpoints: list[ApiEndpoint], output_dir: Path, locale: str = "zh") -> Path:
    wb = create_workbook()
    headers = get_headers("aa02", locale)
    rows = []

    for idx, ep in enumerate(endpoints, 1):
        rows.append([
            generate_encoding("AF", idx),
            camel_to_words(ep.method_name),
            f"{ep.http_method} {ep.path}",
            ep.module_name,
            ep.http_method,
            ep.path,
        ])

    add_sheet(wb, t("sheet.aa02", locale), headers, rows, locale=locale)
    return save_workbook(wb, output_dir / "AA-02_功能项清单.xlsx")
