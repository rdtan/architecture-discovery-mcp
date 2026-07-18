# src/serializers.py
from datetime import datetime
from pathlib import Path

from src.models.project import (
    ProjectInfo, Module, ApiEndpoint, Integration, IntegrationType, DataEntity,
)


def project_to_dict(
    project: ProjectInfo,
    endpoints: list[ApiEndpoint],
    integrations: list[Integration],
) -> dict:
    return {
        "version": "1.0",
        "exported_at": datetime.now().isoformat(timespec="seconds"),
        "project": {
            "name": project.name,
            "path": str(project.path),
            "frameworks": project.frameworks,
            "total_files": project.total_files,
            "modules": [
                {
                    "name": m.name,
                    "path": str(m.path),
                    "group_id": m.group_id,
                    "artifact_id": m.artifact_id,
                    "package_name": m.package_name,
                    "controllers": m.controllers,
                    "services": m.services,
                    "repositories": m.repositories,
                    "entities": m.entities,
                }
                for m in project.modules
            ],
        },
        "api_endpoints": [
            {
                "module_name": ep.module_name,
                "class_name": ep.class_name,
                "method_name": ep.method_name,
                "http_method": ep.http_method,
                "path": ep.path,
                "description": ep.description,
                "parameters": ep.parameters,
                "return_type": ep.return_type,
            }
            for ep in endpoints
        ],
        "integrations": [
            {
                "source_module": intg.source_module,
                "target_module": intg.target_module,
                "integration_type": intg.integration_type.value,
                "interface_name": intg.interface_name,
                "methods": intg.methods,
                "data_entities": intg.data_entities,
            }
            for intg in integrations
        ],
    }


def project_from_dict(data: dict) -> tuple[ProjectInfo, list[ApiEndpoint], list[Integration]]:
    proj_data = data["project"]
    modules = [
        Module(
            name=m["name"],
            path=Path(m["path"]),
            group_id=m["group_id"],
            artifact_id=m["artifact_id"],
            package_name=m["package_name"],
            controllers=m["controllers"],
            services=m["services"],
            repositories=m["repositories"],
            entities=m["entities"],
        )
        for m in proj_data["modules"]
    ]
    project = ProjectInfo(
        name=proj_data["name"],
        path=Path(proj_data["path"]),
        modules=modules,
        frameworks=proj_data["frameworks"],
        total_files=proj_data["total_files"],
    )

    endpoints = [
        ApiEndpoint(
            module_name=ep["module_name"],
            class_name=ep["class_name"],
            method_name=ep["method_name"],
            http_method=ep["http_method"],
            path=ep["path"],
            description=ep.get("description", ""),
            parameters=ep.get("parameters", []),
            return_type=ep.get("return_type", ""),
        )
        for ep in data["api_endpoints"]
    ]

    integrations = [
        Integration(
            source_module=intg["source_module"],
            target_module=intg["target_module"],
            integration_type=IntegrationType(intg["integration_type"]),
            interface_name=intg["interface_name"],
            methods=intg.get("methods", []),
            data_entities=intg.get("data_entities", []),
        )
        for intg in data["integrations"]
    ]

    return project, endpoints, integrations
