from pathlib import Path
from src.models.project import ProjectInfo, ApiEndpoint
from src.generators.excel_generator import create_workbook, add_sheet, save_workbook
from src.utils.naming import generate_encoding, camel_to_words
from src.i18n import t, get_headers

HEADERS = get_headers("aa03")


def generate_aa03(project: ProjectInfo, endpoints: list[ApiEndpoint], output_dir: Path, locale: str = "zh") -> Path:
    wb = create_workbook()
    headers = get_headers("aa03", locale)
    rows = []

    sub_idx = 0
    for ep_idx, ep in enumerate(endpoints, 1):
        parent_id = generate_encoding("AF", ep_idx)
        for param in ep.parameters:
            sub_idx += 1
            rows.append([
                generate_encoding("AFS", sub_idx),
                f"{camel_to_words(ep.method_name)} - {param}",
                t("val.param", locale, param=param),
                parent_id,
                ep.module_name,
            ])

        if not ep.parameters:
            sub_idx += 1
            rows.append([
                generate_encoding("AFS", sub_idx),
                camel_to_words(ep.method_name),
                f"{ep.http_method} {ep.path}",
                parent_id,
                ep.module_name,
            ])

    add_sheet(wb, t("sheet.aa03", locale), headers, rows, locale=locale)
    return save_workbook(wb, output_dir / "AA-03_功能子项清单.xlsx")
