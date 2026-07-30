from dataclasses import dataclass, field
import re

from src.parsers.java_parser import JavaClass

HTTP_METHOD_ANNOTATIONS = {
    "GetMapping": "GET",
    "PostMapping": "POST",
    "PutMapping": "PUT",
    "DeleteMapping": "DELETE",
    "PatchMapping": "PATCH",
    "RequestMapping": "",
}

MYBATIS_BASE_CLASSES = {"BaseEntity", "TreeEntity"}
MYBATIS_EXCLUDED_CLASSES = {"BaseEntity", "TreeEntity", "BaseController", "AjaxResult", "R", "TableDataInfo", "PageDomain"}


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

    # MyBatis entity detection: classes extending BaseEntity/TreeEntity in domain packages
    if not metadata.is_entity and java_class.extends_class in MYBATIS_BASE_CLASSES:
        if java_class.class_name not in MYBATIS_EXCLUDED_CLASSES:
            metadata.is_entity = True
            if not metadata.table_name:
                metadata.table_name = _extract_table_from_javadoc(java_class.documentation)

    # Extract endpoints for controllers and feign clients
    if metadata.is_controller or metadata.is_feign_client:
        metadata.endpoints = _extract_endpoints(java_class, metadata.base_path)

    return metadata


def _extract_table_from_javadoc(documentation: str) -> str:
    """Extract table name from Javadoc comment.

    Matches snake_case identifiers like 'sys_config', 'gen_table_column'.
    """
    if not documentation:
        return ""
    match = re.search(r'\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b', documentation)
    return match.group(1) if match else ""


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
