from pathlib import Path

from src.models.project import ProjectInfo, Integration, IntegrationType
from src.parsers.java_parser import parse_java_file
from src.parsers.spring_parser import extract_spring_metadata


def analyze_integrations(project: ProjectInfo) -> list[Integration]:
    """Analyze a project for inter-module integrations (Feign/Dubbo/MQ).

    Scans all Java source files in each module looking for:
    - @FeignClient annotations (HTTP integrations)
    - @DubboReference / @Reference annotations (RPC integrations)
    - @KafkaListener / @RabbitListener annotations (MQ integrations)

    Returns a list of Integration objects describing discovered dependencies.
    Single file parse failures are skipped gracefully.
    """
    integrations: list[Integration] = []

    for module in project.modules:
        java_src = module.path / "src" / "main" / "java"
        if not java_src.exists():
            continue

        for java_file in java_src.rglob("*.java"):
            try:
                java_class = parse_java_file(java_file)
            except Exception:
                continue

            if java_class is None:
                continue

            metadata = extract_spring_metadata(java_class)

            # Feign client detection (HTTP)
            if metadata.is_feign_client:
                target_module = metadata.feign_name or _infer_module_from_class(
                    java_class.class_name
                )
                methods = [ep["method_name"] for ep in metadata.endpoints]
                data_entities = _extract_data_entities(java_class)

                integrations.append(
                    Integration(
                        source_module=module.name,
                        target_module=target_module,
                        integration_type=IntegrationType.HTTP,
                        interface_name=java_class.class_name,
                        methods=methods,
                        data_entities=data_entities,
                    )
                )

            # Dubbo reference detection (RPC)
            if _has_dubbo_reference(java_class):
                dubbo_integrations = _extract_dubbo_integrations(
                    java_class, module.name
                )
                integrations.extend(dubbo_integrations)

            # Message queue listener detection (MQ)
            if _has_mq_listener(java_class):
                mq_integrations = _extract_mq_integrations(java_class, module.name)
                integrations.extend(mq_integrations)

    return integrations


def _infer_module_from_class(class_name: str) -> str:
    """Infer a module name from a class name like 'PaymentClient' -> 'payment-service'."""
    name = class_name.replace("Client", "").replace("Feign", "")
    parts: list[str] = []
    current = ""
    for char in name:
        if char.isupper() and current:
            parts.append(current.lower())
            current = char
        else:
            current += char
    if current:
        parts.append(current.lower())
    return "-".join(parts) + "-service" if parts else class_name


def _extract_data_entities(java_class) -> list[str]:
    """Extract data entity types from method signatures."""
    primitive_types = {"void", "String", "int", "long", "boolean", "Long", "Double", "Integer", "Boolean"}
    entities: set[str] = set()

    for method in java_class.methods:
        if method.return_type and method.return_type not in primitive_types:
            entities.add(method.return_type)
        for param in method.parameters:
            ptype = param.get("type", "")
            if ptype and ptype not in primitive_types:
                entities.add(ptype)

    return sorted(entities)


def _has_dubbo_reference(java_class) -> bool:
    """Check if any field has a @DubboReference or @Reference annotation."""
    for field_info in java_class.fields:
        annotations = field_info.get("annotations", [])
        if any(a in ("DubboReference", "Reference") for a in annotations):
            return True
    return False


def _extract_dubbo_integrations(java_class, source_module: str) -> list[Integration]:
    """Extract RPC integrations from @DubboReference fields."""
    integrations: list[Integration] = []
    for field_info in java_class.fields:
        annotations = field_info.get("annotations", [])
        if any(a in ("DubboReference", "Reference") for a in annotations):
            target = field_info.get("type", "unknown")
            integrations.append(
                Integration(
                    source_module=source_module,
                    target_module=_infer_module_from_class(target),
                    integration_type=IntegrationType.RPC,
                    interface_name=target,
                    methods=[],
                    data_entities=[],
                )
            )
    return integrations


def _has_mq_listener(java_class) -> bool:
    """Check if any method has a @KafkaListener or @RabbitListener annotation."""
    for method in java_class.methods:
        for ann in method.annotations:
            if ann["name"] in ("KafkaListener", "RabbitListener"):
                return True
    return False


def _extract_mq_integrations(java_class, source_module: str) -> list[Integration]:
    """Extract MQ integrations from @KafkaListener/@RabbitListener methods."""
    integrations: list[Integration] = []
    for method in java_class.methods:
        for ann in method.annotations:
            if ann["name"] in ("KafkaListener", "RabbitListener"):
                topic = ann.get("value", "") or ann.get("params", {}).get("topics", "")
                integrations.append(
                    Integration(
                        source_module=source_module,
                        target_module=f"mq:{topic}" if topic else "message-queue",
                        integration_type=IntegrationType.MQ,
                        interface_name=java_class.class_name,
                        methods=[method.name],
                        data_entities=[],
                    )
                )
    return integrations
