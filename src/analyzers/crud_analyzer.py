"""CRUD relationship analyzer between entities and application functions."""

import re
from src.models.project import ProjectInfo, DataEntity


# HTTP method to CRUD operation mapping
HTTP_METHOD_CRUD = {
    "POST": "C",
    "GET": "R",
    "PUT": "U",
    "PATCH": "U",
    "DELETE": "D",
}

# Method name prefix patterns to CRUD operation mapping
METHOD_NAME_PATTERNS = [
    (re.compile(r"^(create|save|add|insert)", re.IGNORECASE), "C"),
    (re.compile(r"^(get|find|list|query|search|select|fetch|load)", re.IGNORECASE), "R"),
    (re.compile(r"^(update|modify|edit|patch|put)", re.IGNORECASE), "U"),
    (re.compile(r"^(delete|remove|drop)", re.IGNORECASE), "D"),
]


def analyze_crud(project: ProjectInfo, entities: list[DataEntity]) -> list[dict]:
    """Analyze CRUD relationships between entities and application functions.

    Uses API endpoints (if available) to map HTTP methods to CRUD operations,
    then associates each endpoint with a data entity by name similarity.
    Falls back to inferring from controller/service/repository names when
    no API endpoints are available.

    Returns list of dicts:
    [{"entity": "Order", "data_domain": "order-service", "operation": "C",
      "app_name": "order-service", "module": "OrderController", "function": "createOrder"}, ...]
    """
    if not entities:
        return []

    # Build entity lookup: lowercase class name -> DataEntity
    entity_map = {e.class_name.lower(): e for e in entities}
    entity_names = [e.class_name for e in entities]

    records: list[dict] = []

    # Strategy 1: Use API endpoints if available
    if project.api_endpoints:
        for ep in project.api_endpoints:
            # Determine CRUD operation from HTTP method
            operation = HTTP_METHOD_CRUD.get(ep.http_method.upper())
            if not operation:
                # Try to infer from method name
                operation = _infer_crud_from_method_name(ep.method_name)
            if not operation:
                continue

            # Match endpoint to entity by controller/class name similarity
            matched_entity = _match_entity_by_class_name(
                ep.class_name, entity_names, entity_map
            )
            if not matched_entity:
                # Try matching by module name
                matched_entity = _match_entity_by_module(
                    ep.module_name, entity_names, entity_map
                )
            if not matched_entity:
                continue

            entity_obj = entity_map[matched_entity.lower()]
            records.append({
                "entity": matched_entity,
                "data_domain": entity_obj.data_domain or entity_obj.module_name,
                "operation": operation,
                "app_name": ep.module_name,
                "module": ep.class_name,
                "function": ep.method_name,
            })
    else:
        # Strategy 2: Infer from module controller/service/repository names
        records = _infer_from_modules(project, entities, entity_map, entity_names)

    return records


def _infer_crud_from_method_name(method_name: str) -> str | None:
    """Infer CRUD operation from a method name using prefix patterns."""
    for pattern, operation in METHOD_NAME_PATTERNS:
        if pattern.search(method_name):
            return operation
    return None


def _match_entity_by_class_name(
    class_name: str, entity_names: list[str], entity_map: dict
) -> str | None:
    """Match a controller/service class to an entity by stripping suffix and comparing."""
    # Strip common suffixes
    base_name = re.sub(
        r"(Controller|Service|ServiceImpl|Repository|Dao|Mapper)$", "", class_name
    )
    if not base_name:
        return None

    # Direct match
    if base_name.lower() in entity_map:
        return base_name

    # Partial match: check if entity name is contained in the base name or vice versa
    for entity_name in entity_names:
        if entity_name.lower() in base_name.lower() or base_name.lower() in entity_name.lower():
            return entity_name

    return None


def _match_entity_by_module(
    module_name: str, entity_names: list[str], entity_map: dict
) -> str | None:
    """Match a module name to an entity by partial string matching."""
    # Normalize module name: remove hyphens, compare case-insensitively
    normalized = module_name.replace("-", "").replace("_", "").lower()

    for entity_name in entity_names:
        if entity_name.lower() in normalized or normalized in entity_name.lower():
            return entity_name

    return None


def _infer_from_modules(
    project: ProjectInfo,
    entities: list[DataEntity],
    entity_map: dict,
    entity_names: list[str],
) -> list[dict]:
    """Infer CRUD records from module controller/repository class names."""
    records: list[dict] = []

    for module in project.modules:
        # Process controllers - infer from method naming conventions
        for controller_name in module.controllers:
            matched_entity = _match_entity_by_class_name(
                controller_name, entity_names, entity_map
            )
            if not matched_entity:
                continue

            entity_obj = entity_map[matched_entity.lower()]

            # Since we don't have method-level detail in this fallback,
            # generate generic CRUD entries for the controller
            records.append({
                "entity": matched_entity,
                "data_domain": entity_obj.data_domain or entity_obj.module_name,
                "operation": "R",
                "app_name": module.name,
                "module": controller_name,
                "function": f"get{matched_entity}",
            })

        # Process repositories - they imply all CRUD operations
        for repo_name in module.repositories:
            matched_entity = _match_entity_by_class_name(
                repo_name, entity_names, entity_map
            )
            if not matched_entity:
                continue

            entity_obj = entity_map[matched_entity.lower()]

            for op, method_prefix in [("C", "save"), ("R", "findBy"), ("U", "save"), ("D", "delete")]:
                records.append({
                    "entity": matched_entity,
                    "data_domain": entity_obj.data_domain or entity_obj.module_name,
                    "operation": op,
                    "app_name": module.name,
                    "module": repo_name,
                    "function": f"{method_prefix}{matched_entity}",
                })

    return records
