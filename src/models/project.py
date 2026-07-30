from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class AnalysisDepth(Enum):
    MODULE = "module"
    METHOD = "method"


class IntegrationType(Enum):
    HTTP = "HTTP"
    RPC = "RPC"
    MQ = "MQ"


@dataclass
class ApiEndpoint:
    module_name: str
    class_name: str
    method_name: str
    http_method: str
    path: str
    description: str = ""
    parameters: list[str] = field(default_factory=list)
    return_type: str = ""


@dataclass
class Integration:
    source_module: str
    target_module: str
    integration_type: IntegrationType
    interface_name: str
    methods: list[str] = field(default_factory=list)
    data_entities: list[str] = field(default_factory=list)


@dataclass
class EntityField:
    name: str
    java_type: str
    column_name: str = ""
    is_primary_key: bool = False
    is_nullable: bool = True
    is_foreign_key: bool = False
    fk_target_entity: str = ""
    comment: str = ""


@dataclass
class DataEntity:
    module_name: str
    class_name: str
    table_name: str = ""
    fields: list[EntityField] = field(default_factory=list)
    data_domain: str = ""
    data_category: str = ""


@dataclass
class DataRelationship:
    source_entity: str
    target_entity: str
    relationship_type: str
    fk_field: str = ""
    join_table: str = ""


@dataclass
class EnumDefinition:
    module_name: str
    class_name: str
    values: list[dict] = field(default_factory=list)


@dataclass
class Module:
    name: str
    path: Path
    group_id: str = ""
    artifact_id: str = ""
    package_name: str = ""
    controllers: list[str] = field(default_factory=list)
    services: list[str] = field(default_factory=list)
    repositories: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)


@dataclass
class ProjectInfo:
    name: str
    path: Path
    modules: list[Module] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    total_files: int = 0
    api_endpoints: list[ApiEndpoint] = field(default_factory=list)
    integrations: list[Integration] = field(default_factory=list)
    data_entities: list[DataEntity] = field(default_factory=list)
