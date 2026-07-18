import logging
from pathlib import Path
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

NS = {"m": "http://maven.apache.org/POM/4.0.0"}


def _find(parent, tag: str):
    """Find a child element, trying namespaced first then bare."""
    el = parent.find(f"m:{tag}", NS)
    if el is None:
        el = parent.find(tag)
    return el


def _find_all(parent, tag: str):
    """Find all child elements, trying namespaced first then bare."""
    elements = parent.findall(f"m:{tag}", NS)
    if not elements:
        elements = parent.findall(tag)
    return elements


def parse_pom(pom_path: Path) -> dict:
    """Parse a Maven POM file and return structured data.

    Args:
        pom_path: Path to the pom.xml file.

    Returns:
        Dictionary with group_id, artifact_id, version, packaging,
        modules, dependencies, and parent info.

    Raises:
        FileNotFoundError: If the pom_path does not exist.
    """
    if not pom_path.exists():
        raise FileNotFoundError(f"POM file not found: {pom_path}")

    try:
        tree = ET.parse(pom_path)
    except ET.ParseError as e:
        logger.error("Failed to parse POM at %s: %s", pom_path, e)
        return _empty_result()

    root = tree.getroot()

    def text(tag: str) -> str:
        el = _find(root, tag)
        return el.text.strip() if el is not None and el.text else ""

    result = {
        "group_id": text("groupId"),
        "artifact_id": text("artifactId"),
        "version": text("version"),
        "packaging": text("packaging") or "jar",
        "modules": [],
        "dependencies": [],
        "parent_group_id": "",
        "parent_artifact_id": "",
    }

    parent = _find(root, "parent")
    if parent is not None:
        gid = _find(parent, "groupId")
        aid = _find(parent, "artifactId")
        result["parent_group_id"] = gid.text.strip() if gid is not None and gid.text else ""
        result["parent_artifact_id"] = aid.text.strip() if aid is not None and aid.text else ""
        if not result["group_id"]:
            result["group_id"] = result["parent_group_id"]

    modules_el = _find(root, "modules")
    if modules_el is not None:
        for mod in _find_all(modules_el, "module"):
            if mod.text:
                result["modules"].append(mod.text.strip())

    deps_el = _find(root, "dependencies")
    if deps_el is not None:
        for dep in _find_all(deps_el, "dependency"):
            gid = _find(dep, "groupId")
            aid = _find(dep, "artifactId")
            result["dependencies"].append({
                "group_id": gid.text.strip() if gid is not None and gid.text else "",
                "artifact_id": aid.text.strip() if aid is not None and aid.text else "",
            })

    return result


def _empty_result() -> dict:
    """Return an empty result dict for error cases."""
    return {
        "group_id": "",
        "artifact_id": "",
        "version": "",
        "packaging": "jar",
        "modules": [],
        "dependencies": [],
        "parent_group_id": "",
        "parent_artifact_id": "",
    }
