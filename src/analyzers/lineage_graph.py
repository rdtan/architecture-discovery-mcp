"""Data lineage graph engine using NetworkX.

Builds a directed graph from FieldLineage and DataFlow records,
enabling forward tracing (where does data go?) and backward tracing
(where does data come from?) queries.
"""

import networkx as nx
from dataclasses import dataclass, field
from src.models.project import FieldLineage, DataFlow


@dataclass
class LineageNode:
    """A node in the lineage graph representing a field."""
    system: str
    entity: str
    field_name: str

    @property
    def key(self) -> str:
        """Unique key for this node: system.entity.field"""
        return f"{self.system}.{self.entity}.{self.field_name}"


@dataclass
class ImpactResult:
    """Result of an impact analysis query."""
    source_field: str          # The field being analyzed
    downstream_fields: list[str]  # All fields affected downstream
    paths: list[list[str]]     # All paths from source to downstream
    total_affected: int = 0


class LineageGraph:
    """Directed graph of field-level data lineage.

    Nodes are field identifiers (system.entity.field).
    Edges represent data flow with metadata (mapping_type, confidence, evidence).
    """

    def __init__(self):
        self._graph = nx.DiGraph()

    def build_from_lineages(self, lineages: list[FieldLineage], flows: list[DataFlow] | None = None):
        """Build the graph from FieldLineage records and optional DataFlow records.

        Each FieldLineage becomes an edge: source_field -> target_field
        DataFlow records add system-level edges for context.
        """
        for lineage in lineages:
            source_key = f"{lineage.source_system}.{lineage.source_entity}.{lineage.source_field}"
            target_key = f"{lineage.target_system}.{lineage.target_entity}.{lineage.target_field}"

            self._graph.add_edge(
                source_key,
                target_key,
                mapping_type=lineage.mapping_type,
                confidence=lineage.confidence,
                evidence=lineage.evidence,
                transform_expr=lineage.transform_expr,
            )

        # DataFlow adds system-level context edges (optional)
        if flows:
            for flow in flows:
                for data_obj in flow.data_objects:
                    source_key = f"{flow.source_system}.{flow.source_module}.{data_obj}"
                    target_key = f"{flow.target_system}.{flow.target_module}.{data_obj}"
                    self._graph.add_edge(
                        source_key,
                        target_key,
                        mapping_type="flow",
                        transport_type=flow.transport_type,
                        frequency=flow.frequency,
                    )

    def trace_forward(self, field_key: str) -> list[str]:
        """Trace forward: where does this field's data flow to?

        Args:
            field_key: "system.entity.field" identifier

        Returns:
            List of all downstream field keys (descendants in the graph).
        """
        if field_key not in self._graph:
            return []
        return sorted(nx.descendants(self._graph, field_key))

    def trace_backward(self, field_key: str) -> list[str]:
        """Trace backward: where does this field's data come from?

        Args:
            field_key: "system.entity.field" identifier

        Returns:
            List of all upstream field keys (ancestors in the graph).
        """
        if field_key not in self._graph:
            return []
        return sorted(nx.ancestors(self._graph, field_key))

    def impact_analysis(self, field_key: str) -> ImpactResult:
        """Analyze the impact of changing a field.

        Returns all downstream fields and the paths through which
        the change would propagate.
        """
        downstream = self.trace_forward(field_key)
        paths = []
        for target in downstream:
            for path in nx.all_simple_paths(self._graph, field_key, target):
                paths.append(path)

        return ImpactResult(
            source_field=field_key,
            downstream_fields=downstream,
            paths=paths,
            total_affected=len(downstream),
        )

    def get_direct_sources(self, field_key: str) -> list[dict]:
        """Get immediate predecessors with edge metadata."""
        if field_key not in self._graph:
            return []
        result = []
        for pred in self._graph.predecessors(field_key):
            edge_data = self._graph.edges[pred, field_key]
            result.append({
                "field": pred,
                "mapping_type": edge_data.get("mapping_type", ""),
                "confidence": edge_data.get("confidence", 1.0),
                "evidence": edge_data.get("evidence", ""),
            })
        return result

    def get_direct_targets(self, field_key: str) -> list[dict]:
        """Get immediate successors with edge metadata."""
        if field_key not in self._graph:
            return []
        result = []
        for succ in self._graph.successors(field_key):
            edge_data = self._graph.edges[field_key, succ]
            result.append({
                "field": succ,
                "mapping_type": edge_data.get("mapping_type", ""),
                "confidence": edge_data.get("confidence", 1.0),
                "evidence": edge_data.get("evidence", ""),
            })
        return result

    @property
    def node_count(self) -> int:
        return self._graph.number_of_nodes()

    @property
    def edge_count(self) -> int:
        return self._graph.number_of_edges()

    def get_all_nodes(self) -> list[str]:
        """Return all node keys in the graph."""
        return sorted(self._graph.nodes())

    def get_all_edges(self) -> list[tuple[str, str, dict]]:
        """Return all edges with metadata."""
        return [(u, v, d) for u, v, d in self._graph.edges(data=True)]
