from pathlib import Path
from openpyxl import Workbook

from src.models.project import ProjectInfo, ApiEndpoint, Integration
from src.generators.excel_generator import create_workbook, add_sheet, save_workbook
from src.utils.naming import generate_encoding, camel_to_words
from src.i18n import t, get_headers
from src.generators.aa01_generator import _get_sub_modules


def generate_app_architecture(
    project: ProjectInfo,
    endpoints: list[ApiEndpoint],
    integrations: list[Integration],
    output_dir: Path,
    locale: str = "zh",
) -> Path:
    wb = create_workbook()

    # AA-01 应用系统模块清单
    rows_aa01 = []
    domain_id = generate_encoding("AD", 1)
    domain_name = project.name
    for mod_idx, module in enumerate(project.modules, 1):
        group_id = generate_encoding("AG", mod_idx)
        group_name = module.name
        sub_modules = _get_sub_modules(module, locale)
        if not sub_modules:
            sub_modules = [{"level1": module.name, "level2": ""}]
        for sub_idx, sub in enumerate(sub_modules, 1):
            rows_aa01.append([
                domain_id, domain_name,
                group_id, group_name,
                generate_encoding(f"AM-{mod_idx}", sub_idx), sub["level1"],
                generate_encoding(f"AM-{mod_idx}-{sub_idx}", 1) if sub["level2"] else "",
                sub["level2"],
                t("val.built", locale),
            ])
    add_sheet(wb, t("sheet.aa01", locale), get_headers("aa01", locale), rows_aa01, locale=locale)

    # AA-02 功能项清单
    rows_aa02 = []
    for idx, ep in enumerate(endpoints, 1):
        rows_aa02.append([
            generate_encoding("AF", idx),
            camel_to_words(ep.method_name),
            f"{ep.http_method} {ep.path}",
            ep.module_name,
            ep.http_method,
            ep.path,
        ])
    add_sheet(wb, t("sheet.aa02", locale), get_headers("aa02", locale), rows_aa02, locale=locale)

    # AA-03 功能子项清单
    rows_aa03 = []
    sub_idx = 0
    for ep_idx, ep in enumerate(endpoints, 1):
        parent_id = generate_encoding("AF", ep_idx)
        for param in ep.parameters:
            sub_idx += 1
            rows_aa03.append([
                generate_encoding("AFS", sub_idx),
                f"{camel_to_words(ep.method_name)} - {param}",
                t("val.param", locale, param=param),
                parent_id,
                ep.module_name,
            ])
        if not ep.parameters:
            sub_idx += 1
            rows_aa03.append([
                generate_encoding("AFS", sub_idx),
                camel_to_words(ep.method_name),
                f"{ep.http_method} {ep.path}",
                parent_id,
                ep.module_name,
            ])
    add_sheet(wb, t("sheet.aa03", locale), get_headers("aa03", locale), rows_aa03, locale=locale)

    # AA-04 功能项分布清单
    rows_aa04 = []
    for idx, ep in enumerate(endpoints, 1):
        rows_aa04.append([
            generate_encoding("AF", idx),
            camel_to_words(ep.method_name),
            project.name,
            t("val.microservice_app", locale),
            ep.module_name,
            ep.module_name,
        ])
    add_sheet(wb, t("sheet.aa04", locale), get_headers("aa04", locale), rows_aa04, locale=locale)

    # AA-05 应用集成清单
    rows_aa05 = []
    module_names = {m.name for m in project.modules}
    for idx, intg in enumerate(integrations, 1):
        is_cross_domain = intg.target_module not in module_names
        rows_aa05.append([
            generate_encoding("AI", idx),
            intg.source_module,
            intg.target_module,
            intg.integration_type.value,
            intg.interface_name,
            ", ".join(intg.methods),
            ", ".join(intg.data_entities),
            t("val.yes", locale) if is_cross_domain else t("val.no", locale),
        ])
    add_sheet(wb, t("sheet.aa05", locale), get_headers("aa05", locale), rows_aa05, locale=locale)

    return save_workbook(wb, output_dir / t("file.combined", locale))
