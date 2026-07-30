from pathlib import Path
from src.models.project import ProjectInfo, DataEntity
from src.generators.excel_generator import create_workbook, add_sheet, save_workbook
from src.utils.naming import generate_encoding
from src.i18n import t, get_headers


def generate_da01(project: ProjectInfo, entities: list[DataEntity], output_dir: Path, locale: str = "zh") -> Path:
    wb = create_workbook()
    headers = get_headers("da01", locale)
    rows = []

    # Group entities by data_domain
    domain_order: list[str] = []
    domain_entities: dict[str, list[DataEntity]] = {}
    for entity in entities:
        domain = entity.data_domain or entity.module_name
        if domain not in domain_entities:
            domain_order.append(domain)
            domain_entities[domain] = []
        domain_entities[domain].append(entity)

    entity_idx = 0
    for domain_idx, domain in enumerate(domain_order, 1):
        domain_id = generate_encoding("DD", domain_idx)
        domain_name = domain

        for entity in domain_entities[domain]:
            entity_idx += 1
            entity_id = generate_encoding("DE", entity_idx)

            # Determine data category
            if entity.data_category:
                data_category = t(f"val.{entity.data_category}", locale) if f"val.{entity.data_category}" in _get_translation_keys() else entity.data_category
            else:
                data_category = t("val.transaction_data", locale)

            rows.append([
                domain_id,
                domain_name,
                entity_id,
                entity.class_name,
                entity.class_name,  # business object = class_name for now
                t("val.yes", locale),
                data_category,
                entity.module_name,
            ])

    add_sheet(wb, t("sheet.da01", locale), headers, rows, locale=locale)
    return save_workbook(wb, output_dir / "DA-01_概念实体清单.xlsx")


def _get_translation_keys() -> set[str]:
    """Return the set of known translation keys for checking existence."""
    from src.i18n import TRANSLATIONS
    return set(TRANSLATIONS.keys())
