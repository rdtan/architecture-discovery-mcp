import pytest
from src.analyzers.lineage_graph import LineageGraph, ImpactResult
from src.models.project import FieldLineage, DataFlow


@pytest.fixture
def sample_lineages():
    """Sample lineage records forming a chain: Order.id -> OrderDTO.orderId -> Report.sourceId"""
    return [
        FieldLineage(
            source_system="order-service", source_entity="Order", source_field="id",
            target_system="order-service", target_entity="OrderDTO", target_field="orderId",
            mapping_type="direct", confidence=1.0, evidence="MapStruct @Mapping",
        ),
        FieldLineage(
            source_system="order-service", source_entity="Order", source_field="customerName",
            target_system="order-service", target_entity="OrderDTO", target_field="buyer",
            mapping_type="direct", confidence=1.0, evidence="setter/getter chain",
        ),
        FieldLineage(
            source_system="order-service", source_entity="OrderDTO", source_field="orderId",
            target_system="report-service", target_entity="Report", target_field="sourceId",
            mapping_type="direct", confidence=0.7, evidence="SQL SELECT",
        ),
        FieldLineage(
            source_system="order-service", source_entity="Order", source_field="amount",
            target_system="order-service", target_entity="OrderDTO", target_field="totalAmount",
            mapping_type="direct", confidence=1.0, evidence="setter/getter chain",
        ),
    ]


@pytest.fixture
def graph(sample_lineages):
    g = LineageGraph()
    g.build_from_lineages(sample_lineages)
    return g


def test_build_graph(graph):
    assert graph.node_count == 7  # 4 source + 3 target (orderId is shared)
    assert graph.edge_count == 4


def test_trace_forward(graph):
    # Order.id flows to OrderDTO.orderId and then to Report.sourceId
    downstream = graph.trace_forward("order-service.Order.id")
    assert "order-service.OrderDTO.orderId" in downstream
    assert "report-service.Report.sourceId" in downstream


def test_trace_backward(graph):
    # Report.sourceId traces back to OrderDTO.orderId and Order.id
    upstream = graph.trace_backward("report-service.Report.sourceId")
    assert "order-service.OrderDTO.orderId" in upstream
    assert "order-service.Order.id" in upstream


def test_impact_analysis(graph):
    result = graph.impact_analysis("order-service.Order.id")
    assert isinstance(result, ImpactResult)
    assert result.total_affected == 2  # OrderDTO.orderId + Report.sourceId
    assert len(result.paths) >= 2  # Direct path + transitive path


def test_get_direct_sources(graph):
    sources = graph.get_direct_sources("order-service.OrderDTO.orderId")
    assert len(sources) == 1
    assert sources[0]["field"] == "order-service.Order.id"
    assert sources[0]["evidence"] == "MapStruct @Mapping"


def test_get_direct_targets(graph):
    targets = graph.get_direct_targets("order-service.Order.id")
    assert len(targets) == 1
    assert targets[0]["field"] == "order-service.OrderDTO.orderId"


def test_nonexistent_node(graph):
    assert graph.trace_forward("nonexistent.Entity.field") == []
    assert graph.trace_backward("nonexistent.Entity.field") == []


def test_empty_graph():
    g = LineageGraph()
    g.build_from_lineages([])
    assert g.node_count == 0
    assert g.edge_count == 0


def test_with_dataflows(sample_lineages):
    flows = [
        DataFlow(
            flow_id="DF-001",
            source_system="order-service", source_module="order-api",
            target_system="report-service", target_module="report-consumer",
            transport_type="MQ",
            data_objects=["OrderEvent"],
            frequency="realtime",
        )
    ]
    g = LineageGraph()
    g.build_from_lineages(sample_lineages, flows)
    # Should have extra nodes from the flow
    assert g.node_count > 7


# =============================================================================
# Additional edge-case tests
# =============================================================================


def test_cyclic_graph():
    """Cyclic lineage (A->B->A) should not cause infinite loops."""
    lineages = [
        FieldLineage(
            source_system="svc", source_entity="A", source_field="x",
            target_system="svc", target_entity="B", target_field="y",
            mapping_type="direct", confidence=1.0, evidence="test",
        ),
        FieldLineage(
            source_system="svc", source_entity="B", source_field="y",
            target_system="svc", target_entity="A", target_field="x",
            mapping_type="direct", confidence=1.0, evidence="test",
        ),
    ]
    g = LineageGraph()
    g.build_from_lineages(lineages)

    # Should not hang — NetworkX handles cycles in descendants/ancestors
    forward = g.trace_forward("svc.A.x")
    assert "svc.B.y" in forward

    backward = g.trace_backward("svc.B.y")
    assert "svc.A.x" in backward


def test_duplicate_edges():
    """Same source->target from two different evidence sources."""
    lineages = [
        FieldLineage(
            source_system="svc", source_entity="Order", source_field="id",
            target_system="svc", target_entity="DTO", target_field="orderId",
            mapping_type="direct", confidence=1.0, evidence="MapStruct",
        ),
        FieldLineage(
            source_system="svc", source_entity="Order", source_field="id",
            target_system="svc", target_entity="DTO", target_field="orderId",
            mapping_type="direct", confidence=0.7, evidence="setter",
        ),
    ]
    g = LineageGraph()
    g.build_from_lineages(lineages)

    # NetworkX overwrites edge data — should still have 1 edge, last one wins
    assert g.node_count == 2
    assert g.edge_count == 1

    sources = g.get_direct_sources("svc.DTO.orderId")
    assert len(sources) == 1
    # Last lineage's evidence overwrites
    assert sources[0]["evidence"] == "setter"


def test_get_all_nodes(graph):
    nodes = graph.get_all_nodes()
    assert isinstance(nodes, list)
    assert len(nodes) == 7
    assert all(isinstance(n, str) for n in nodes)
    # Should be sorted
    assert nodes == sorted(nodes)


def test_get_all_edges(graph):
    edges = graph.get_all_edges()
    assert isinstance(edges, list)
    assert len(edges) == 4
    for u, v, data in edges:
        assert isinstance(u, str)
        assert isinstance(v, str)
        assert isinstance(data, dict)
        assert "mapping_type" in data


def test_impact_analysis_no_downstream(graph):
    """A leaf node with no downstream should return empty impact."""
    result = graph.impact_analysis("report-service.Report.sourceId")
    assert result.total_affected == 0
    assert result.downstream_fields == []
    assert result.paths == []


def test_dataflow_empty_data_objects(sample_lineages):
    """DataFlow with empty data_objects should not add extra edges."""
    flows = [
        DataFlow(
            flow_id="DF-002",
            source_system="order-service", source_module="order-api",
            target_system="report-service", target_module="report-consumer",
            transport_type="MQ",
            data_objects=[],
            frequency="realtime",
        )
    ]
    g = LineageGraph()
    g.build_from_lineages(sample_lineages, flows)
    # Same as without flows — empty data_objects means no flow edges
    g2 = LineageGraph()
    g2.build_from_lineages(sample_lineages)
    assert g.node_count == g2.node_count
    assert g.edge_count == g2.edge_count
