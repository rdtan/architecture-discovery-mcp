"""DA-IMPACT Impact Analysis Report generator.

Produces an Excel workbook showing the downstream impact of changing a specific field.
"""

import re
from pathlib import Path

from src.analyzers.lineage_graph import LineageGraph
from src.generators.excel_generator import create_workbook, add_sheet, save_workbook
from src.i18n import t, get_headers


def generate_da_impact(
    graph: LineageGraph,
    field_key: str,
    output_dir: Path,
    locale: str = "zh",
) -> Path:
    """Generate DA-IMPACT impact analysis Excel workbook.

    Args:
        graph: Built LineageGraph instance.
        field_key: Field to analyze, format "system.entity.field".
        output_dir: Directory to write the output file.
        locale: "zh" or "en".

    Returns:
        Path to the generated Excel file.
    """
    impact = graph.impact_analysis(field_key)

    wb = create_workbook()
    headers = get_headers("da_impact", locale)

    rows = []
    for path in impact.paths:
        target_key = path[-1]
        parts = target_key.split(".", 2)
        system = parts[0] if len(parts) > 0 else ""
        entity = parts[1] if len(parts) > 1 else ""
        field_name = parts[2] if len(parts) > 2 else ""

        path_str = " → ".join(path)
        depth = len(path) - 1

        min_confidence = 1.0
        last_mapping_type = ""
        for i in range(len(path) - 1):
            edge_data = graph._graph.edges.get((path[i], path[i + 1]), {})
            conf = edge_data.get("confidence", 1.0)
            if conf < min_confidence:
                min_confidence = conf
            if i == len(path) - 2:
                last_mapping_type = edge_data.get("mapping_type", "")

        rows.append([
            target_key,
            system,
            entity,
            field_name,
            path_str,
            depth,
            last_mapping_type,
            min_confidence,
        ])

    sheet_name = t("sheet.da_impact", locale)
    add_sheet(wb, sheet_name, headers, rows, locale=locale)

    field_sanitized = _sanitize_field_name(field_key)
    filename = t("file.da_impact", locale, field=field_sanitized)
    return save_workbook(wb, output_dir / filename)


def _sanitize_field_name(field_key: str) -> str:
    """Sanitize a field key for use in filenames."""
    sanitized = field_key.replace(".", "_")
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', sanitized)
    if len(sanitized) > 50:
        sanitized = sanitized[:50]
    return sanitized
