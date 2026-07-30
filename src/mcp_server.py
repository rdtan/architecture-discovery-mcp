import json
import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from src.scanner.project_scanner import scan_project
from src.analyzers.module_analyzer import analyze_modules
from src.analyzers.api_analyzer import analyze_apis
from src.analyzers.integration_analyzer import analyze_integrations
from src.generators.app_architecture_generator import generate_app_architecture
from src.generators.aa07_generator import generate_aa07
from src.generators.aa08_generator import generate_aa08
from src.generators.da_combined_generator import generate_all_da
from src.serializers import project_to_dict
from src.i18n import t

logging.basicConfig(level=logging.INFO)

mcp = FastMCP(
    "architecture-discovery",
    instructions="架构自动发现引擎 - 扫描 Java 项目源码，自动生成企业架构制品（AA/DA/TA）",
)


def _validate_project_path(project_path: str, locale: str = "zh") -> Path:
    path = Path(project_path)
    if not path.exists():
        raise ValueError(t("err.path_not_found", locale, path=project_path))
    if not (path / "pom.xml").exists():
        raise ValueError(t("err.no_pom", locale, path=project_path))
    return path


@mcp.tool()
def scan_project_tool(project_path: str, locale: str = "zh") -> str:
    """扫描 Java/Maven 项目结构，返回模块、框架、文件数量等概览信息。

    Args:
        project_path: Java/Maven 项目根目录路径（须包含 pom.xml）
        locale: 输出语言 zh|en，默认 zh
    """
    path = _validate_project_path(project_path, locale)

    project = scan_project(path)
    project = analyze_modules(project)

    summary = {
        "project_name": project.name,
        "modules_count": len(project.modules),
        "total_java_files": project.total_files,
        "frameworks": project.frameworks,
        "modules": [
            {
                "name": m.name,
                "controllers": len(m.controllers),
                "services": len(m.services),
                "repositories": len(m.repositories),
                "entities": len(m.entities),
            }
            for m in project.modules
        ],
    }
    return json.dumps(summary, ensure_ascii=False, indent=2)


@mcp.tool()
def generate_app_architecture_tool(project_path: str, output_dir: str = "", locale: str = "zh") -> str:
    """扫描 Java 项目并生成应用架构全套制品（AA-01~AA-08）。

    生成 Excel（含 AA-01 至 AA-05 五个工作表）和两个 PPTX 架构图。

    Args:
        project_path: Java/Maven 项目根目录路径（须包含 pom.xml）
        output_dir: 制品输出目录，默认为项目路径下的 arch-output/
        locale: 输出语言 zh|en，默认 zh
    """
    path = _validate_project_path(project_path, locale)

    out = Path(output_dir) if output_dir else path / "arch-output"
    out.mkdir(parents=True, exist_ok=True)

    project = scan_project(path)
    project = analyze_modules(project)
    endpoints = analyze_apis(project)
    integrations = analyze_integrations(project)

    excel_path = generate_app_architecture(project, endpoints, integrations, out, locale=locale)
    aa07_path = generate_aa07(project, out, locale=locale)
    aa08_path = generate_aa08(project, integrations, out, locale=locale)

    result = {
        "success": True,
        "summary": {
            "modules": len(project.modules),
            "api_endpoints": len(endpoints),
            "integrations": len(integrations),
        },
        "artifacts": [
            {"name": excel_path.name, "path": str(excel_path)},
            {"name": aa07_path.name, "path": str(aa07_path)},
            {"name": aa08_path.name, "path": str(aa08_path)},
        ],
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def export_intermediate_data(project_path: str, output_path: str = "", locale: str = "zh") -> str:
    """将项目扫描和分析结果导出为 JSON 文件，供架构顾问导入做进一步分析。

    导出内容为结构化元数据（模块、API、集成关系），不含源码原文。

    Args:
        project_path: Java/Maven 项目根目录路径（须包含 pom.xml）
        output_path: JSON 文件输出路径，默认为项目路径下的 arch-output/intermediate-data.json
        locale: 输出语言 zh|en，默认 zh
    """
    path = _validate_project_path(project_path, locale)

    project = scan_project(path)
    project = analyze_modules(project)
    endpoints = analyze_apis(project)
    integrations = analyze_integrations(project)

    data = project_to_dict(project, endpoints, integrations)

    if not output_path:
        out_dir = path / "arch-output"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(out_dir / "intermediate-data.json")

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    result = {
        "success": True,
        "output_path": str(out_file),
        "size_bytes": out_file.stat().st_size,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def generate_data_architecture_tool(project_path: str, output_dir: str = "", locale: str = "zh") -> str:
    """扫描 Java 项目并生成数据架构全套制品（DA-01~DA-07）。

    生成 7 个独立 Excel 文件（DA-01 至 DA-07）及一个合并多 Sheet 工作簿。

    Args:
        project_path: Java/Maven 项目根目录路径（须包含 pom.xml）
        output_dir: 制品输出目录，默认为项目路径下的 arch-output/
        locale: 输出语言 zh|en，默认 zh
    """
    path = _validate_project_path(project_path, locale)

    out = Path(output_dir) if output_dir else path / "arch-output"
    out.mkdir(parents=True, exist_ok=True)

    project = scan_project(path)
    project = analyze_modules(project)

    outputs = generate_all_da(project, out, locale=locale)

    result = {
        "success": True,
        "summary": {
            "total_files": len(outputs),
        },
        "artifacts": [
            {"name": p.name, "path": str(p)} for p in outputs
        ],
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def generate_tech_architecture(project_path: str, output_dir: str = "", locale: str = "zh") -> str:
    """生成技术架构（TA 系列）制品。

    Args:
        project_path: Java/Maven 项目根目录路径
        output_dir: 制品输出目录
        locale: 输出语言 zh|en，默认 zh
    """
    return json.dumps({
        "success": False,
        "message": t("msg.ta_not_supported", locale),
    }, ensure_ascii=False)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
