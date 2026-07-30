import pytest
from src.scanner.project_scanner import scan_project
from src.analyzers.data_entity_analyzer import analyze_data_entities


def test_analyze_data_entities_returns_entities(sample_project_path):
    """At least one DataEntity is returned from the sample project."""
    project = scan_project(sample_project_path)
    entities, relationships = analyze_data_entities(project)
    assert len(entities) >= 1


def test_analyze_data_entities_order_entity(sample_project_path):
    """Order entity has correct table_name and 4 fields."""
    project = scan_project(sample_project_path)
    entities, relationships = analyze_data_entities(project)
    order = next(e for e in entities if e.class_name == "Order")
    assert order.table_name == "orders"
    assert len(order.fields) == 4


def test_analyze_data_entities_order_id_field(sample_project_path):
    """The id field should be marked as primary key."""
    project = scan_project(sample_project_path)
    entities, _ = analyze_data_entities(project)
    order = next(e for e in entities if e.class_name == "Order")
    id_field = next(f for f in order.fields if f.name == "id")
    assert id_field.is_primary_key is True


def test_analyze_data_entities_order_userid_field(sample_project_path):
    """The userId field should have column_name='user_id' and java_type='Long'."""
    project = scan_project(sample_project_path)
    entities, _ = analyze_data_entities(project)
    order = next(e for e in entities if e.class_name == "Order")
    user_id_field = next(f for f in order.fields if f.name == "userId")
    assert user_id_field.column_name == "user_id"
    assert user_id_field.java_type == "Long"


def test_analyze_data_entities_order_module_name(sample_project_path):
    """Order entity should have data_domain set to the module name."""
    project = scan_project(sample_project_path)
    entities, _ = analyze_data_entities(project)
    order = next(e for e in entities if e.class_name == "Order")
    assert order.data_domain == "order-service"


def test_analyze_data_entities_empty_project(tmp_path):
    """Project with no Java source should return empty lists."""
    from src.models.project import ProjectInfo, Module

    module = Module(name="empty-mod", path=tmp_path)
    project = ProjectInfo(name="test", path=tmp_path, modules=[module])
    entities, relationships = analyze_data_entities(project)
    assert entities == []
    assert relationships == []


def test_analyze_data_entities_missing_src(tmp_path):
    """Module with no src/main/java should be skipped gracefully."""
    from src.models.project import ProjectInfo, Module

    module = Module(name="no-src", path=tmp_path / "nonexistent")
    project = ProjectInfo(name="test", path=tmp_path, modules=[module])
    entities, relationships = analyze_data_entities(project)
    assert entities == []
    assert relationships == []
