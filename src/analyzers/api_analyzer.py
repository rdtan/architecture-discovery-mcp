import logging
from pathlib import Path

from src.models.project import ProjectInfo, ApiEndpoint
from src.parsers.java_parser import parse_java_file
from src.parsers.spring_parser import extract_spring_metadata

logger = logging.getLogger(__name__)


def analyze_apis(project: ProjectInfo) -> list[ApiEndpoint]:
    """Extract API endpoints from all controller classes in the project.

    Walks each module's Java source tree, identifies controllers via Spring
    annotations, and builds ApiEndpoint instances from their HTTP mappings.

    Args:
        project: A ProjectInfo instance (typically from scan_project).

    Returns:
        A list of ApiEndpoint dataclass instances.
    """
    endpoints: list[ApiEndpoint] = []

    for module in project.modules:
        java_src = module.path / "src" / "main" / "java"
        if not java_src.exists():
            continue

        for java_file in java_src.rglob("*.java"):
            try:
                java_class = parse_java_file(java_file)
            except Exception as e:
                logger.warning("Failed to parse %s: %s", java_file, e)
                continue

            if java_class is None:
                continue

            metadata = extract_spring_metadata(java_class)
            if not metadata.is_controller:
                continue

            for ep in metadata.endpoints:
                parameters = []
                for p in ep.get("parameters", []):
                    if isinstance(p, dict):
                        parameters.append(p.get("name", ""))
                    else:
                        parameters.append(str(p))

                endpoints.append(
                    ApiEndpoint(
                        module_name=module.name,
                        class_name=java_class.class_name,
                        method_name=ep["method_name"],
                        http_method=ep["http_method"],
                        path=ep["path"],
                        parameters=parameters,
                        return_type=ep.get("return_type", ""),
                    )
                )

    return endpoints
