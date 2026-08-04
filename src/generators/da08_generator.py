"""DA-08 Field-Level Lineage generator.

Produces an Excel workbook with field-level mapping data.
"""

from pathlib import Path

from src.models.project import ProjectInfo, FieldLineage
from src.generators.excel_generator import create_workbook, add_sheet, save_workbook
from src.i18n import t, get_headers


def generate_da08(
    project: ProjectInfo,
    lineages: list[FieldLineage],
    output_dir: Path,
    locale: str = "zh",
) -> Path:
    """Generate DA-08 field-level lineage Excel workbook.

    Args:
        project: Project info (for naming context).
        lineages: List of FieldLineage records from all analyzers.
        output_dir: Directory to write the output file.
        locale: "zh" or "en".

    Returns:
        Path to the generated Excel file.
    """
    wb = create_workbook()
    headers = get_headers("da08", locale)

    rows = []
    for l in lineages:
        # Format confidence as human-readable label
        if l.confidence >= 0.9:
            conf_str = t("val.confidence_high", locale)
        elif l.confidence >= 0.6:
            conf_str = t("val.confidence_medium", locale)
        else:
            conf_str = t("val.confidence_low", locale)

        rows.append([
            l.source_system,
            l.source_entity,
            l.source_field,
            l.target_system,
            l.target_entity,
            l.target_field,
            l.mapping_type,
            l.transform_expr,
            l.trigger_mode,
            conf_str,
            l.evidence,
        ])

    sheet_name = t("sheet.da08", locale)
    add_sheet(wb, sheet_name, headers, rows, locale=locale)

    filename = t("file.da08", locale)
    return save_workbook(wb, output_dir / filename)
