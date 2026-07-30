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


# --- Field-level annotation parameter tests ---


def test_field_annotations_contain_params(order_service_path):
    """Field annotations should be dicts with name and params, not plain strings."""
    path = order_service_path / "src/main/java/com/example/order/entity/Order.java"
    result = parse_java_file(path)
    assert result is not None

    for f in result.fields:
        if "annotations" in f:
            for ann in f["annotations"]:
                assert isinstance(ann, dict), (
                    f"Expected annotation to be a dict, got {type(ann)}"
                )
                assert "name" in ann
                assert "params" in ann


def test_userid_field_column_annotation(order_service_path):
    """userId field should have @Column(name = 'user_id') captured with params."""
    path = order_service_path / "src/main/java/com/example/order/entity/Order.java"
    result = parse_java_file(path)
    assert result is not None

    user_id_field = next(f for f in result.fields if f["name"] == "userId")
    assert "annotations" in user_id_field

    column_ann = next(
        a for a in user_id_field["annotations"] if a["name"] == "Column"
    )
    assert column_ann == {"name": "Column", "params": {"name": "user_id"}}


def test_id_field_annotations(order_service_path):
    """id field should have @Id (no params) and @GeneratedValue with strategy param."""
    path = order_service_path / "src/main/java/com/example/order/entity/Order.java"
    result = parse_java_file(path)
    assert result is not None

    id_field = next(f for f in result.fields if f["name"] == "id")
    assert "annotations" in id_field

    id_ann = next(a for a in id_field["annotations"] if a["name"] == "Id")
    assert id_ann == {"name": "Id", "params": {}}

    gen_value_ann = next(
        a for a in id_field["annotations"] if a["name"] == "GeneratedValue"
    )
    assert gen_value_ann == {
        "name": "GeneratedValue",
        "params": {"strategy": "GenerationType.IDENTITY"},
    }
