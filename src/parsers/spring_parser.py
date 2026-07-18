from dataclasses import dataclass, field

from src.parsers.java_parser import JavaClass

HTTP_METHOD_ANNOTATIONS = {
    "GetMapping": "GET",
    "PostMapping": "POST",
    "PutMapping": "PUT",
    "DeleteMapping": "DELETE",
    "PatchMapping": "PATCH",
    "RequestMapping": "",
}


@dataclass
class SpringMetadata:
    is_controller: bool = False
    is_service: bool = False
    is_repository: bool = False
    is_feign_client: bool = False
    is_entity: bool = False
    base_path: str = ""
    feign_name: str = ""
    feign_url: str = ""
    table_name: str = ""
    endpoints: list[dict] = field(default_factory=list)


def extract_spring_metadata(java_class: JavaClass) -> SpringMetadata:
    """Extract Spring Framework metadata from a parsed JavaClass."""
    metadata = SpringMetadata()

    # Identify class-level stereotypes
    for ann in java_class.annotations:
        if ann in ("RestController", "Controller"):
            metadata.is_controller = True
        elif ann == "Service":
            metadata.is_service = True
        elif ann == "Repository":
            metadata.is_repository = True
        elif ann == "FeignClient":
            metadata.is_feign_client = True
        elif ann == "Entity":
            metadata.is_entity = True

    # Extract annotation parameters
    for detail in java_class.annotation_details:
        if detail["name"] == "RequestMapping":
            val = detail.get("value", "")
            if not val and "params" in detail:
                val = detail["params"].get("value", "")
            metadata.base_path = val
        elif detail["name"] == "FeignClient":
            params = detail.get("params", {})
            if isinstance(params, dict):
                metadata.feign_name = params.get("name", "") or params.get(
                    "value", ""
                )
                metadata.feign_url = params.get("url", "")
            else:
                metadata.feign_name = detail.get("value", "")
        elif detail["name"] == "Table":
            params = detail.get("params", {})
            metadata.table_name = (
                params.get("name", "")
                if isinstance(params, dict)
                else detail.get("value", "")
            )

    # Extract endpoints for controllers and feign clients
    if metadata.is_controller or metadata.is_feign_client:
        metadata.endpoints = _extract_endpoints(java_class, metadata.base_path)

    return metadata


def _extract_endpoints(java_class: JavaClass, base_path: str) -> list[dict]:
    """Extract HTTP endpoints from method-level annotations."""
    endpoints = []
    for method in java_class.methods:
        for ann in method.annotations:
            ann_name = ann["name"]
            if ann_name in HTTP_METHOD_ANNOTATIONS:
                http_method = HTTP_METHOD_ANNOTATIONS[ann_name]
                if ann_name == "RequestMapping":
                    params = ann.get("params", {})
                    http_method = params.get("method", "GET")

                path_suffix = ann.get("value", "")
                if not path_suffix and "params" in ann:
                    path_suffix = ann["params"].get("value", "")

                full_path = base_path.rstrip("/")
                if path_suffix:
                    full_path = full_path + "/" + path_suffix.lstrip("/")
                if not full_path:
                    full_path = base_path

                endpoints.append(
                    {
                        "method_name": method.name,
                        "http_method": http_method,
                        "path": full_path,
                        "parameters": method.parameters,
                        "return_type": method.return_type,
                    }
                )
                break  # Only take the first HTTP mapping annotation per method
    return endpoints
