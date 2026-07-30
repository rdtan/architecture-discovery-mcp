import pytest
from src.scanner.project_scanner import scan_project
from src.analyzers.enum_analyzer import analyze_enums


def test_analyze_enums_finds_order_status(sample_project_path):
    """Enum analyzer should discover OrderStatus enum in the fixture project."""
    project = scan_project(sample_project_path)
    enums = analyze_enums(project)
    assert len(enums) >= 1


def test_analyze_enums_order_status_values(sample_project_path):
    """OrderStatus enum should have exactly 4 values."""
    project = scan_project(sample_project_path)
    enums = analyze_enums(project)
    order_status = next(e for e in enums if e.class_name == "OrderStatus")
    assert len(order_status.values) == 4


def test_analyze_enums_first_value_details(sample_project_path):
    """First value of OrderStatus should be PENDING with correct value and label."""
    project = scan_project(sample_project_path)
    enums = analyze_enums(project)
    order_status = next(e for e in enums if e.class_name == "OrderStatus")
    first = order_status.values[0]
    assert first == {"name": "PENDING", "value": "pending", "label": "待处理"}


def test_analyze_enums_all_values(sample_project_path):
    """All OrderStatus values should have correct names."""
    project = scan_project(sample_project_path)
    enums = analyze_enums(project)
    order_status = next(e for e in enums if e.class_name == "OrderStatus")
    names = [v["name"] for v in order_status.values]
    assert names == ["PENDING", "PROCESSING", "COMPLETED", "CANCELLED"]


def test_analyze_enums_module_name(sample_project_path):
    """Enum should be associated with the correct module."""
    project = scan_project(sample_project_path)
    enums = analyze_enums(project)
    order_status = next(e for e in enums if e.class_name == "OrderStatus")
    assert order_status.module_name == "order-service"


def test_analyze_enums_empty_project(tmp_path):
    """Project with no Java source should return empty list."""
    from src.models.project import ProjectInfo, Module

    module = Module(name="empty-mod", path=tmp_path)
    project = ProjectInfo(name="test", path=tmp_path, modules=[module])
    enums = analyze_enums(project)
    assert enums == []


def test_analyze_enums_simple_enum(tmp_path):
    """Simple enum without constructor args should use ordinal as value."""
    from src.models.project import ProjectInfo, Module

    # Create a simple enum file
    java_dir = tmp_path / "src" / "main" / "java" / "com" / "example" / "enums"
    java_dir.mkdir(parents=True)
    enum_file = java_dir / "Color.java"
    enum_file.write_text(
        "package com.example.enums;\n\n"
        "public enum Color {\n"
        "    RED, GREEN, BLUE\n"
        "}\n",
        encoding="utf-8",
    )

    module = Module(name="test-mod", path=tmp_path, artifact_id="test-mod")
    project = ProjectInfo(name="test", path=tmp_path, modules=[module])
    enums = analyze_enums(project)

    assert len(enums) == 1
    assert enums[0].class_name == "Color"
    assert len(enums[0].values) == 3
    assert enums[0].values[0] == {"name": "RED", "value": "0", "label": ""}
    assert enums[0].values[1] == {"name": "GREEN", "value": "1", "label": ""}
    assert enums[0].values[2] == {"name": "BLUE", "value": "2", "label": ""}
