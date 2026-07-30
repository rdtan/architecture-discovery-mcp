import logging
from pathlib import Path

from src.models.project import ProjectInfo, Module
from src.parsers.java_parser import parse_java_file
from src.parsers.spring_parser import extract_spring_metadata, MYBATIS_BASE_CLASSES, MYBATIS_EXCLUDED_CLASSES

logger = logging.getLogger(__name__)


def analyze_modules(project: ProjectInfo) -> ProjectInfo:
    """Walk Java source files in each module and classify them using Spring annotations.

    Updates each module's controllers, services, repositories, and entities lists
    based on annotation-driven detection (overriding folder-based heuristics).
    Falls back to MyBatis heuristics for entity detection when no JPA @Entity is found.

    Args:
        project: A ProjectInfo instance (typically from scan_project).

    Returns:
        The same ProjectInfo instance with updated module classifications.
    """
    for module in project.modules:
        java_src = module.path / "src" / "main" / "java"
        if not java_src.exists():
            continue

        controllers: list[str] = []
        services: list[str] = []
        repositories: list[str] = []
        entities: list[str] = []
        mybatis_entities: list[str] = []
        first_package: str = ""

        for java_file in java_src.rglob("*.java"):
            try:
                java_class = parse_java_file(java_file)
            except Exception as e:
                logger.warning("Failed to parse %s: %s", java_file, e)
                continue

            if java_class is None:
                continue

            # Track the first package found for the module
            if not first_package and java_class.package_name:
                first_package = java_class.package_name

            metadata = extract_spring_metadata(java_class)
            if metadata.is_controller:
                controllers.append(java_class.class_name)
            elif metadata.is_service:
                services.append(java_class.class_name)
            elif metadata.is_repository:
                repositories.append(java_class.class_name)

            if "Entity" in java_class.annotations:
                entities.append(java_class.class_name)
            elif (java_class.extends_class in MYBATIS_BASE_CLASSES
                  and java_class.class_name not in MYBATIS_EXCLUDED_CLASSES):
                mybatis_entities.append(java_class.class_name)

        module.controllers = controllers
        module.services = services
        module.repositories = repositories
        # Use JPA entities if found, otherwise use MyBatis-detected entities
        module.entities = entities if entities else mybatis_entities

        if first_package:
            module.package_name = first_package

    return project
