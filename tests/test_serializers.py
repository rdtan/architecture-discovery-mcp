# tests/test_serializers.py
import pytest
from pathlib import Path
from src.models.project import (
    ProjectInfo, Module, ApiEndpoint, Integration, IntegrationType, DataEntity,
)
from src.serializers import project_to_dict, project_from_dict


@pytest.fixture
def sample_project():
    module = Module(
        name="order-service",
        path=Path("/tmp/order-service"),
        group_id="com.example",
        artifact_id="order-service",
        package_name="com.example.order",
        controllers=["OrderController"],
        services=["OrderService"],
        repositories=["OrderRepository"],
        entities=["Order"],
    )
    project = ProjectInfo(
        name="demo-project",
        path=Path("/tmp/demo-project"),
        modules=[module],
        frameworks=["Spring Boot", "MyBatis"],
        total_files=42,
    )
    return project


@pytest.fixture
def sample_endpoints():
    return [
        ApiEndpoint(
            module_name="order-service",
            class_name="OrderController",
            method_name="createOrder",
            http_method="POST",
            path="/api/orders",
            description="Create a new order",
            parameters=["orderRequest"],
            return_type="Order",
        )
    ]


@pytest.fixture
def sample_integrations():
    return [
        Integration(
            source_module="order-service",
            target_module="payment-service",
            integration_type=IntegrationType.HTTP,
            interface_name="PaymentClient",
            methods=["pay", "refund"],
            data_entities=["PaymentRequest"],
        )
    ]


def test_project_to_dict_roundtrip(sample_project, sample_endpoints, sample_integrations):
    data = project_to_dict(sample_project, sample_endpoints, sample_integrations)

    assert data["version"] == "1.0"
    assert data["project"]["name"] == "demo-project"
    assert len(data["project"]["modules"]) == 1
    assert data["project"]["modules"][0]["name"] == "order-service"
    assert data["project"]["frameworks"] == ["Spring Boot", "MyBatis"]
    assert len(data["api_endpoints"]) == 1
    assert data["api_endpoints"][0]["method_name"] == "createOrder"
    assert len(data["integrations"]) == 1
    assert data["integrations"][0]["integration_type"] == "HTTP"


def test_project_from_dict_roundtrip(sample_project, sample_endpoints, sample_integrations):
    data = project_to_dict(sample_project, sample_endpoints, sample_integrations)
    restored_project, restored_endpoints, restored_integrations = project_from_dict(data)

    assert restored_project.name == "demo-project"
    assert len(restored_project.modules) == 1
    assert restored_project.modules[0].name == "order-service"
    assert restored_project.modules[0].controllers == ["OrderController"]
    assert restored_project.frameworks == ["Spring Boot", "MyBatis"]
    assert restored_project.total_files == 42

    assert len(restored_endpoints) == 1
    assert restored_endpoints[0].http_method == "POST"
    assert restored_endpoints[0].path == "/api/orders"

    assert len(restored_integrations) == 1
    assert restored_integrations[0].integration_type == IntegrationType.HTTP
    assert restored_integrations[0].target_module == "payment-service"
