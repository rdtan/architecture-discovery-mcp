import pytest
from pathlib import Path

from src.parsers.java_parser import parse_java_file
from src.parsers.spring_parser import extract_spring_metadata


def test_parse_controller(order_service_path):
    path = order_service_path / "src/main/java/com/example/order/controller/OrderController.java"
    result = parse_java_file(path)
    assert result is not None
    assert result.class_name == "OrderController"
    assert result.package_name == "com.example.order.controller"
    assert "RestController" in result.annotations
    method_names = [m.name for m in result.methods]
    assert "createOrder" in method_names
    assert "getOrder" in method_names
    assert "updateStatus" in method_names


def test_parse_feign_client(order_service_path):
    path = order_service_path / "src/main/java/com/example/order/client/PaymentClient.java"
    result = parse_java_file(path)
    assert result is not None
    assert result.class_name == "PaymentClient"
    assert "FeignClient" in result.annotations
    assert result.is_interface is True


def test_parse_entity(order_service_path):
    path = order_service_path / "src/main/java/com/example/order/entity/Order.java"
    result = parse_java_file(path)
    assert result is not None
    assert "Entity" in result.annotations
    assert result.class_name == "Order"


def test_parse_invalid_file(tmp_path):
    bad_file = tmp_path / "Bad.java"
    bad_file.write_text("this is not valid java {{{{", encoding="utf-8")
    result = parse_java_file(bad_file)
    assert result is None


def test_parse_nonexistent_file():
    result = parse_java_file(Path("/nonexistent/Foo.java"))
    assert result is None


def test_extract_controller_metadata(order_service_path):
    path = order_service_path / "src/main/java/com/example/order/controller/OrderController.java"
    java_class = parse_java_file(path)
    metadata = extract_spring_metadata(java_class)
    assert metadata.is_controller is True
    assert metadata.base_path == "/api/orders"
    assert len(metadata.endpoints) == 3
    post_ep = next(e for e in metadata.endpoints if e["method_name"] == "createOrder")
    assert post_ep["http_method"] == "POST"
    assert post_ep["path"] == "/api/orders"


def test_extract_feign_metadata(order_service_path):
    path = order_service_path / "src/main/java/com/example/order/client/PaymentClient.java"
    java_class = parse_java_file(path)
    metadata = extract_spring_metadata(java_class)
    assert metadata.is_feign_client is True
    assert metadata.feign_name == "payment-service"
    assert len(metadata.endpoints) == 2


def test_extract_entity_metadata(order_service_path):
    path = order_service_path / "src/main/java/com/example/order/entity/Order.java"
    java_class = parse_java_file(path)
    metadata = extract_spring_metadata(java_class)
    assert metadata.is_entity is True
    assert metadata.table_name == "orders"


def test_controller_endpoint_paths(order_service_path):
    path = order_service_path / "src/main/java/com/example/order/controller/OrderController.java"
    java_class = parse_java_file(path)
    metadata = extract_spring_metadata(java_class)
    get_ep = next(e for e in metadata.endpoints if e["method_name"] == "getOrder")
    assert get_ep["http_method"] == "GET"
    assert get_ep["path"] == "/api/orders/{id}"
    put_ep = next(e for e in metadata.endpoints if e["method_name"] == "updateStatus")
    assert put_ep["http_method"] == "PUT"
    assert put_ep["path"] == "/api/orders/{id}/status"
