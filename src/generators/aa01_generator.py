from pathlib import Path
from src.models.project import ProjectInfo
from src.generators.excel_generator import create_workbook, add_sheet, save_workbook
from src.utils.naming import generate_encoding
from src.i18n import t, get_headers

HEADERS = get_headers("aa01")


def generate_aa01(project: ProjectInfo, output_dir: Path, locale: str = "zh") -> Path:
    wb = create_workbook()
    headers = get_headers("aa01", locale)
    rows = []

    domain_id = generate_encoding("AD", 1)
    domain_name = project.name

    for mod_idx, module in enumerate(project.modules, 1):
        group_id = generate_encoding("AG", mod_idx)
        group_name = module.name

        sub_modules = _get_sub_modules(module, locale)
        if not sub_modules:
            sub_modules = [{"level1": module.name, "level2": ""}]

        for sub_idx, sub in enumerate(sub_modules, 1):
            rows.append([
                domain_id, domain_name,
                group_id, group_name,
                generate_encoding(f"AM-{mod_idx}", sub_idx), sub["level1"],
                generate_encoding(f"AM-{mod_idx}-{sub_idx}", 1) if sub["level2"] else "",
                sub["level2"],
                t("val.built", locale),
            ])

    add_sheet(wb, t("sheet.aa01", locale), headers, rows, locale=locale)
    return save_workbook(wb, output_dir / "AA-01_应用系统模块清单.xlsx")


def _get_sub_modules(module, locale: str = "zh") -> list[dict]:
    layers = []
    if module.controllers:
        layers.append({"level1": t("layer.api", locale), "level2": ""})
    if module.services:
        layers.append({"level1": t("layer.business", locale), "level2": ""})
    if module.repositories:
        layers.append({"level1": t("layer.data_access", locale), "level2": ""})
    if module.entities:
        layers.append({"level1": t("layer.entity", locale), "level2": ""})
    return layers
