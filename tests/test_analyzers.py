import pytest
from src.scanner.project_scanner import scan_project
from src.analyzers.module_analyzer import analyze_modules
from src.analyzers.api_analyzer import analyze_apis
from src.analyzers.integration_analyzer import analyze_integrations
from src.models.project import IntegrationType


def test_analyze_modules_hierarchy(sample_project_path):
    project = scan_project(sample_project_path)
    result = analyze_modules(project)
    order_module = next(m for m in result.modules if m.name == "order-service")
    assert "OrderController" in order_module.controllers
    assert "OrderService" in order_module.services
    assert "Order" in order_module.entities


def test_analyze_modules_package(sample_project_path):
    project = scan_project(sample_project_path)
    result = analyze_modules(project)
    order_module = next(m for m in result.modules if m.name == "order-service")
    # package_name is set to the first package encountered during rglob
    assert "com.example.order" in order_module.package_name


def test_analyze_modules_user_service(sample_project_path):
    project = scan_project(sample_project_path)
    result = analyze_modules(project)
    user_module = next(m for m in result.modules if m.name == "user-service")
    assert "UserController" in user_module.controllers
    assert "UserService" in user_module.services


def test_analyze_modules_does_not_crash_on_missing_src(tmp_path):
    """Module with no src/main/java should be skipped gracefully."""
    from src.models.project import ProjectInfo, Module

    module = Module(name="empty-mod", path=tmp_path)
    project = ProjectInfo(name="test", path=tmp_path, modules=[module])
    result = analyze_modules(project)
    assert result.modules[0].controllers == []
    assert result.modules[0].services == []


def test_analyze_apis_count(sample_project_path):
    project = scan_project(sample_project_path)
    endpoints = analyze_apis(project)
    assert len(endpoints) >= 5  # 3 from order + 2 from user


def test_analyze_apis_details(sample_project_path):
    project = scan_project(sample_project_path)
    endpoints = analyze_apis(project)
    order_eps = [e for e in endpoints if e.module_name == "order-service"]
    assert len(order_eps) == 3
    create_ep = next(e for e in order_eps if e.method_name == "createOrder")
    assert create_ep.http_method == "POST"
    assert create_ep.path == "/api/orders"
    assert create_ep.class_name == "OrderController"


def test_analyze_apis_user_service(sample_project_path):
    project = scan_project(sample_project_path)
    endpoints = analyze_apis(project)
    user_eps = [e for e in endpoints if e.module_name == "user-service"]
    assert len(user_eps) == 2
    get_ep = next(e for e in user_eps if e.method_name == "getUser")
    assert get_ep.http_method == "GET"
    assert get_ep.path == "/api/users/{id}"


def test_analyze_apis_empty_project(tmp_path):
    """Project with no Java source should return empty list."""
    from src.models.project import ProjectInfo, Module

    module = Module(name="empty-mod", path=tmp_path)
    project = ProjectInfo(name="test", path=tmp_path, modules=[module])
    endpoints = analyze_apis(project)
    assert endpoints == []


# --- Integration Analyzer Tests ---


def test_analyze_integrations_feign(sample_project_path):
    project = scan_project(sample_project_path)
    integrations = analyze_integrations(project)
    assert len(integrations) >= 1
    feign_int = next(
        i for i in integrations if i.integration_type == IntegrationType.HTTP
    )
    assert feign_int.source_module == "order-service"
    assert feign_int.target_module == "payment-service"
    assert feign_int.interface_name == "PaymentClient"
    assert "createPayment" in feign_int.methods


def test_analyze_integrations_methods(sample_project_path):
    project = scan_project(sample_project_path)
    integrations = analyze_integrations(project)
    feign_int = next(
        i for i in integrations if i.target_module == "payment-service"
    )
    assert "getPaymentStatus" in feign_int.methods


def test_analyze_integrations_data_entities(sample_project_path):
    """Feign integrations should extract non-primitive return types as data entities."""
    project = scan_project(sample_project_path)
    integrations = analyze_integrations(project)
    feign_int = next(
        i for i in integrations if i.target_module == "payment-service"
    )
    assert "PaymentResponse" in feign_int.data_entities


def test_analyze_integrations_empty_project(tmp_path):
    """Project with no Java source should return empty list."""
    from src.models.project import ProjectInfo, Module

    module = Module(name="empty-mod", path=tmp_path)
    project = ProjectInfo(name="test", path=tmp_path, modules=[module])
    integrations = analyze_integrations(project)
    assert integrations == []


def test_analyze_integrations_missing_src(tmp_path):
    """Module with no src/main/java should be skipped gracefully."""
    from src.models.project import ProjectInfo, Module

    module = Module(name="no-src", path=tmp_path / "nonexistent")
    project = ProjectInfo(name="test", path=tmp_path, modules=[module])
    integrations = analyze_integrations(project)
    assert integrations == []
