"""Combined data lineage generator.

Orchestrates all lineage analyzers and generators to produce:
- DA-08: Field-level lineage Excel
- DA-09: Data flow inventory Excel
- Lineage graph for impact analysis queries
"""

from pathlib import Path

from src.models.project import ProjectInfo, FieldLineage, DataFlow
from src.analyzers.data_entity_analyzer import analyze_data_entities
from src.analyzers.lineage_analyzer import analyze_mapstruct_lineage
from src.analyzers.setter_getter_analyzer import analyze_setter_getter_lineage
from src.analyzers.sql_lineage_analyzer import analyze_sql_lineage
from src.analyzers.dataflow_analyzer import analyze_dataflows
from src.analyzers.lineage_graph import LineageGraph
from src.generators.da08_generator import generate_da08
from src.generators.da09_generator import generate_da09
from src.generators.da_lineage_generator import generate_da_lineage


def generate_data_lineage(project: ProjectInfo, output_dir: Path, locale: str = "zh") -> dict:
    """Generate complete data lineage artifacts.

    Runs all lineage analyzers and produces DA-08, DA-09 files.
    Also returns the built LineageGraph for programmatic queries.

    Returns dict with:
        - "files": list of generated file paths
        - "stats": summary statistics
        - "graph": LineageGraph instance for queries
    """
    # Step 1: Run data entity analyzer (needed for BeanUtils field matching)
    entities, relationships = analyze_data_entities(project)

    # Step 2: Run all lineage analyzers
    all_lineages: list[FieldLineage] = []

    # L1a: MapStruct declarative mappings
    mapstruct_lineages = analyze_mapstruct_lineage(project)
    all_lineages.extend(mapstruct_lineages)

    # L1b: Setter/getter chains + BeanUtils
    setter_lineages = analyze_setter_getter_lineage(project, entities)
    all_lineages.extend(setter_lineages)

    # L1c: SQL field sources
    sql_lineages = analyze_sql_lineage(project)
    all_lineages.extend(sql_lineages)

    # L2: Cross-system data flows
    flows = analyze_dataflows(project)

    # Step 3: Build lineage graph
    graph = LineageGraph()
    graph.build_from_lineages(all_lineages, flows)

    # Step 4: Generate output files
    output_files: list[Path] = []

    da08_path = generate_da08(project, all_lineages, output_dir, locale)
    output_files.append(da08_path)

    da09_path = generate_da09(project, flows, output_dir, locale)
    output_files.append(da09_path)

    # Step 4b: Generate DA-LINEAGE diagram (PPTX)
    if graph.node_count > 0:
        lineage_pptx_path = generate_da_lineage(project, graph, output_dir, locale)
        output_files.append(lineage_pptx_path)

    # Step 5: Return results
    stats = {
        "total_lineages": len(all_lineages),
        "mapstruct_count": len(mapstruct_lineages),
        "setter_getter_count": len(setter_lineages),
        "sql_count": len(sql_lineages),
        "dataflow_count": len(flows),
        "graph_nodes": graph.node_count,
        "graph_edges": graph.edge_count,
    }

    return {
        "files": output_files,
        "stats": stats,
        "graph": graph,
    }
