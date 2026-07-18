import pytest
from pathlib import Path

from src.parsers.pom_parser import parse_pom
from src.scanner.project_scanner import scan_project


def test_parse_parent_pom(sample_project_path):
    result = parse_pom(sample_project_path / "pom.xml")
    assert result["group_id"] == "com.example"
    assert result["artifact_id"] == "ecommerce-platform"
    assert result["packaging"] == "pom"
    assert "order-service" in result["modules"]
    assert "user-service" in result["modules"]


def test_parse_child_pom(sample_project_path):
    result = parse_pom(sample_project_path / "order-service" / "pom.xml")
    assert result["artifact_id"] == "order-service"
    assert result["parent_artifact_id"] == "ecommerce-platform"
    deps = [d["artifact_id"] for d in result["dependencies"]]
    assert "spring-boot-starter-web" in deps
    assert "spring-cloud-starter-openfeign" in deps


def test_scan_project_detects_modules(sample_project_path):
    info = scan_project(sample_project_path)
    assert info.name == "ecommerce-platform"
    module_names = [m.name for m in info.modules]
    assert "order-service" in module_names
    assert "user-service" in module_names


def test_scan_project_detects_frameworks(sample_project_path):
    info = scan_project(sample_project_path)
    assert "Spring Boot" in info.frameworks


def test_scan_project_counts_files(sample_project_path):
    info = scan_project(sample_project_path)
    assert info.total_files >= 4
