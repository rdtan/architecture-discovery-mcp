"""DA-09 Data Flow Inventory generator.

Produces an Excel workbook with cross-system data flow records.
"""

from pathlib import Path

from src.models.project import ProjectInfo, DataFlow
from src.generators.excel_generator import create_workbook, add_sheet, save_workbook
from src.i18n import t, get_headers


def generate_da09(
    project: ProjectInfo,
    flows: list[DataFlow],
    output_dir: Path,
    locale: str = "zh",
) -> Path:
    """Generate DA-09 data flow inventory Excel workbook.

    Args:
        project: Project info.
        flows: List of DataFlow records.
        output_dir: Directory to write the output file.
        locale: "zh" or "en".

    Returns:
        Path to the generated Excel file.
    """
    wb = create_workbook()
    headers = get_headers("da09", locale)

    rows = []
    for f in flows:
        rows.append([
            f.flow_id,
            f"{f.source_system}/{f.source_module}" if f.source_module else f.source_system,
            f"{f.target_system}/{f.target_module}" if f.target_module else f.target_system,
            f.transport_type,
            ", ".join(f.data_objects) if f.data_objects else "",
            f.frequency,
            f.volume_estimate,
        ])

    sheet_name = t("sheet.da09", locale)
    add_sheet(wb, sheet_name, headers, rows, locale=locale)

    filename = t("file.da09", locale)
    return save_workbook(wb, output_dir / filename)
