import logging
from pathlib import Path

from src.models.project import ProjectInfo, Module
from src.parsers.pom_parser import parse_pom

logger = logging.getLogger(__name__)

FRAMEWORK_MARKERS = {
    "spring-boot-starter-web": "Spring Boot",
    "spring-boot-starter": "Spring Boot",
    "spring-cloud-starter-openfeign": "Spring Cloud OpenFeign",
    "dubbo-spring-boot-starter": "Dubbo",
    "mybatis-spring-boot-starter": "MyBatis",
    "spring-boot-starter-data-jpa": "JPA/Hibernate",
}


def scan_project(project_path: Path) -> ProjectInfo:
    """Scan a Java/Maven project and return structured project information.

    Args:
        project_path: Root path of the Maven project (must contain pom.xml).

    Returns:
        ProjectInfo dataclass populated with modules, frameworks, and file counts.

    Raises:
        FileNotFoundError: If no pom.xml exists at project_path.
    """
    pom_path = project_path / "pom.xml"
    if not pom_path.exists():
        raise FileNotFoundError(f"No pom.xml found at {project_path}")

    pom_data = parse_pom(pom_path)

    info = ProjectInfo(
        name=pom_data["artifact_id"],
        path=project_path,
    )

    frameworks: set[str] = set()

    if pom_data["modules"]:
        for module_name in pom_data["modules"]:
            module_path = project_path / module_name
            if module_path.exists():
                # Check if this is a parent module with sub-modules
                sub_pom_path = module_path / "pom.xml"
                if sub_pom_path.exists():
                    sub_pom = parse_pom(sub_pom_path)
                    if sub_pom["modules"]:
                        # Recursively scan sub-modules
                        for sub_module_name in sub_pom["modules"]:
                            sub_module_path = module_path / sub_module_name
                            if sub_module_path.exists():
                                module = _scan_module(sub_module_path, sub_pom["group_id"] or pom_data["group_id"])
                                info.modules.append(module)
                                frameworks.update(_detect_frameworks(sub_module_path))
                            else:
                                logger.warning("Sub-module directory not found: %s", sub_module_path)
                    else:
                        module = _scan_module(module_path, pom_data["group_id"])
                        info.modules.append(module)
                        frameworks.update(_detect_frameworks(module_path))
                else:
                    module = _scan_module(module_path, pom_data["group_id"])
                    info.modules.append(module)
                    frameworks.update(_detect_frameworks(module_path))
            else:
                logger.warning("Module directory not found: %s", module_path)
    else:
        # Single-module project
        module = _scan_module(project_path, pom_data["group_id"])
        info.modules.append(module)
        frameworks.update(_detect_frameworks(project_path))

    info.frameworks = sorted(frameworks)
    info.total_files = sum(1 for _ in project_path.rglob("*.java"))

    return info


def _scan_module(module_path: Path, parent_group_id: str) -> Module:
    """Scan a single module directory and return a Module dataclass."""
    pom_path = module_path / "pom.xml"
    if pom_path.exists():
        try:
            pom_data = parse_pom(pom_path)
            group_id = pom_data["group_id"] or parent_group_id
            artifact_id = pom_data["artifact_id"]
        except Exception as e:
            logger.error("Failed to parse module POM at %s: %s", pom_path, e)
            group_id = parent_group_id
            artifact_id = module_path.name
    else:
        group_id = parent_group_id
        artifact_id = module_path.name

    java_src = module_path / "src" / "main" / "java"
    package_name = _detect_package(java_src)

    module = Module(
        name=artifact_id,
        path=module_path,
        group_id=group_id,
        artifact_id=artifact_id,
        package_name=package_name,
    )

    for java_file in java_src.rglob("*.java") if java_src.exists() else []:
        relative = java_file.relative_to(java_src)
        parts = relative.parts
        if len(parts) >= 2:
            layer = parts[-2]
            class_name = java_file.stem
            if layer == "controller":
                module.controllers.append(class_name)
            elif layer == "service":
                module.services.append(class_name)
            elif layer in ("repository", "dao", "mapper"):
                module.repositories.append(class_name)
            elif layer in ("entity", "model", "domain"):
                module.entities.append(class_name)

    return module


def _detect_package(java_src: Path) -> str:
    """Detect the base package name from the Java source tree."""
    if not java_src.exists():
        return ""
    for java_file in java_src.rglob("*.java"):
        relative = java_file.relative_to(java_src)
        parts = relative.parts[:-1]
        if parts:
            return ".".join(parts)
    return ""


def _detect_frameworks(module_path: Path) -> set[str]:
    """Detect frameworks used by a module based on its POM dependencies."""
    frameworks: set[str] = set()
    pom_path = module_path / "pom.xml"
    if pom_path.exists():
        try:
            pom_data = parse_pom(pom_path)
            for dep in pom_data["dependencies"]:
                marker = FRAMEWORK_MARKERS.get(dep["artifact_id"])
                if marker:
                    frameworks.add(marker)
        except Exception as e:
            logger.error("Failed to detect frameworks for %s: %s", module_path, e)
    return frameworks
