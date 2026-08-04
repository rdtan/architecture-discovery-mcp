"""Cross-system data flow analyzer.

Detects data flows between systems by:
1. Converting existing Integration records to DataFlow format
2. Detecting MQ Producers (KafkaTemplate.send, RabbitTemplate.convertAndSend, @SendTo)
3. Detecting @Scheduled ETL tasks
"""

import logging
from pathlib import Path

from src.models.project import ProjectInfo, DataFlow, Integration, IntegrationType
from src.parsers.java_parser import parse_java_file
from src.utils.naming import generate_encoding

logger = logging.getLogger(__name__)

# MQ send patterns: (qualifier suffix, method names)
_MQ_SEND_PATTERNS = [
    ("KafkaTemplate", ("send", "sendDefault")),
    ("RabbitTemplate", ("convertAndSend", "convertSendAndReceive", "send")),
    ("JmsTemplate", ("convertAndSend", "send")),
]

_TRANSPORT_TYPE_MAP = {
    IntegrationType.HTTP: "API",
    IntegrationType.RPC: "RPC",
    IntegrationType.MQ: "MQ",
}


def analyze_dataflows(project: ProjectInfo) -> list[DataFlow]:
    """Analyze project for cross-system data flows.

    Strategy:
    1. Convert existing project.integrations to DataFlow records
    2. Scan for MQ producer patterns (KafkaTemplate.send, etc.)
    3. Scan for @Scheduled annotations indicating ETL tasks

    Returns list of DataFlow records.
    """
    flows: list[DataFlow] = []
    counter = 0

    # Step 1: Convert existing integrations to DataFlow
    for integration in project.integrations:
        counter += 1
        flow = DataFlow(
            flow_id=generate_encoding("DF", counter),
            source_system=project.name,
            source_module=integration.source_module,
            target_system=project.name,
            target_module=integration.target_module,
            transport_type=_TRANSPORT_TYPE_MAP.get(integration.integration_type, "API"),
            data_objects=list(integration.data_entities),
            frequency="realtime",
        )
        flows.append(flow)

    # Step 2 & 3: Scan Java files for MQ producers and @Scheduled tasks
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

            # Scan methods for MQ producers and @Scheduled
            for method in java_class.methods:
                # Step 2a: Check @SendTo annotation
                for ann in method.annotations:
                    if ann["name"] == "SendTo":
                        counter += 1
                        topic = ann.get("value", "unknown-topic")
                        flows.append(DataFlow(
                            flow_id=generate_encoding("DF", counter),
                            source_system=project.name,
                            source_module=module.name,
                            target_system=project.name,
                            target_module=f"mq:{topic}",
                            transport_type="MQ",
                            data_objects=[],
                            frequency="realtime",
                        ))

                # Step 2b: Check method body for template.send() invocations
                if method.body is not None:
                    invocations = method.body.get("invocations", [])
                    local_vars = method.body.get("local_variables", [])

                    # Build a type map from local variables and fields
                    type_map = {}
                    for var in local_vars:
                        type_map[var["name"]] = var["type_name"]
                    for field_info in java_class.fields:
                        type_map[field_info["name"]] = field_info.get("type", "")

                    for invocation in invocations:
                        qualifier = invocation.get("qualifier", "")
                        method_name = invocation.get("method_name", "")
                        arguments = invocation.get("arguments", [])

                        if not qualifier:
                            continue

                        # Resolve type from qualifier name
                        resolved_type = type_map.get(qualifier, qualifier)

                        for type_suffix, send_methods in _MQ_SEND_PATTERNS:
                            if (resolved_type.endswith(type_suffix) or qualifier.endswith(type_suffix.lower()) or qualifier.endswith("Template")) and method_name in send_methods:
                                counter += 1
                                topic = _extract_topic_from_args(arguments)
                                flows.append(DataFlow(
                                    flow_id=generate_encoding("DF", counter),
                                    source_system=project.name,
                                    source_module=module.name,
                                    target_system=project.name,
                                    target_module=f"mq:{topic}",
                                    transport_type="MQ",
                                    data_objects=[],
                                    frequency="realtime",
                                ))
                                break

                # Step 3: Check for @Scheduled annotation
                for ann in method.annotations:
                    if ann["name"] == "Scheduled":
                        counter += 1
                        frequency = _extract_scheduled_frequency(ann)
                        flows.append(DataFlow(
                            flow_id=generate_encoding("DF", counter),
                            source_system=project.name,
                            source_module=module.name,
                            target_system=project.name,
                            target_module="scheduled-task",
                            transport_type="ETL",
                            data_objects=[],
                            frequency=frequency,
                        ))

    logger.info("Detected %d data flows for project '%s'", len(flows), project.name)
    return flows


def _extract_topic_from_args(arguments: list[str]) -> str:
    """Try to extract a topic/queue name from send method arguments.

    The first argument to send() is typically the topic name.
    Returns 'unknown-topic' if extraction fails.
    """
    if not arguments:
        return "unknown-topic"

    first_arg = arguments[0]
    # Strip quotes if it's a string literal
    cleaned = first_arg.strip('"').strip("'")
    if cleaned and not cleaned.startswith("(") and len(cleaned) < 100:
        return cleaned
    return "unknown-topic"


def _extract_scheduled_frequency(annotation: dict) -> str:
    """Extract frequency info from a @Scheduled annotation.

    Looks for fixedRate, fixedDelay, or cron parameters.
    Returns a human-readable frequency string.
    """
    params = annotation.get("params", {})
    if not params:
        return "scheduled"

    if "cron" in params:
        return f"cron({params['cron']})"
    if "fixedRate" in params:
        return f"every {params['fixedRate']}ms"
    if "fixedDelay" in params:
        return f"every {params['fixedDelay']}ms (delayed)"

    return "scheduled"
