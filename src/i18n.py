"""Internationalization support via locale-keyed dictionary lookup."""

TRANSLATIONS: dict[str, dict[str, str]] = {
    # --- Sheet names ---
    "sheet.aa01": {"zh": "AA-01 应用系统模块清单", "en": "AA-01 Module Inventory"},
    "sheet.aa02": {"zh": "AA-02 功能项清单", "en": "AA-02 Function Inventory"},
    "sheet.aa03": {"zh": "AA-03 功能子项清单", "en": "AA-03 Sub-function Inventory"},
    "sheet.aa04": {"zh": "AA-04 功能项分布清单", "en": "AA-04 Function Distribution"},
    "sheet.aa05": {"zh": "AA-05 应用集成清单", "en": "AA-05 Integration Inventory"},

    # --- Filenames ---
    "file.aa07": {"zh": "AA-07_应用架构图.pptx", "en": "AA-07_Application_Architecture.pptx"},
    "file.aa08": {"zh": "AA-08_应用集成图.pptx", "en": "AA-08_Application_Integration.pptx"},
    "file.combined": {"zh": "application-architecture.xlsx", "en": "application-architecture.xlsx"},

    # --- AA-01 Headers ---
    "h.aa01.domain_id": {"zh": "应用域编号", "en": "Domain ID"},
    "h.aa01.domain_name": {"zh": "应用域名称", "en": "Domain Name"},
    "h.aa01.group_id": {"zh": "应用组编号", "en": "App Group ID"},
    "h.aa01.group_name": {"zh": "应用组名称", "en": "App Group Name"},
    "h.aa01.l1_module_id": {"zh": "一级应用模块编号", "en": "L1 Module ID"},
    "h.aa01.l1_module_name": {"zh": "一级应用模块名称", "en": "L1 Module Name"},
    "h.aa01.l2_module_id": {"zh": "二级应用模块编号", "en": "L2 Module ID"},
    "h.aa01.l2_module_name": {"zh": "二级应用模块名称", "en": "L2 Module Name"},
    "h.aa01.status": {"zh": "建设现状", "en": "Build Status"},

    # --- AA-02 Headers ---
    "h.aa02.func_id": {"zh": "功能项编号", "en": "Function ID"},
    "h.aa02.func_name": {"zh": "功能项名称", "en": "Function Name"},
    "h.aa02.func_desc": {"zh": "功能项说明", "en": "Description"},
    "h.aa02.module": {"zh": "所属应用模块", "en": "Module"},
    "h.aa02.http_method": {"zh": "HTTP方法", "en": "HTTP Method"},
    "h.aa02.api_path": {"zh": "API路径", "en": "API Path"},

    # --- AA-03 Headers ---
    "h.aa03.sub_id": {"zh": "功能子项编号", "en": "Sub-function ID"},
    "h.aa03.sub_name": {"zh": "功能子项名称", "en": "Sub-function Name"},
    "h.aa03.sub_desc": {"zh": "功能子项说明", "en": "Description"},
    "h.aa03.parent_id": {"zh": "所属功能项编号", "en": "Parent Function ID"},
    "h.aa03.module": {"zh": "所属应用模块", "en": "Module"},

    # --- AA-04 Headers ---
    "h.aa04.func_id": {"zh": "功能项编号", "en": "Function ID"},
    "h.aa04.func_name": {"zh": "功能项名称", "en": "Function Name"},
    "h.aa04.system": {"zh": "所属应用系统", "en": "Application System"},
    "h.aa04.category": {"zh": "应用系统分类", "en": "System Category"},
    "h.aa04.microservice": {"zh": "所属微服务", "en": "Microservice"},
    "h.aa04.module": {"zh": "所属应用模块", "en": "Module"},

    # --- AA-05 Headers ---
    "h.aa05.integ_id": {"zh": "集成编号", "en": "Integration ID"},
    "h.aa05.input_module": {"zh": "输入应用模块", "en": "Source Module"},
    "h.aa05.output_module": {"zh": "输出应用模块", "en": "Target Module"},
    "h.aa05.integ_type": {"zh": "集成类型", "en": "Integration Type"},
    "h.aa05.interface": {"zh": "接口名称", "en": "Interface Name"},
    "h.aa05.methods": {"zh": "方法列表", "en": "Methods"},
    "h.aa05.entities": {"zh": "数据实体", "en": "Data Entities"},
    "h.aa05.cross_domain": {"zh": "是否跨业务领域", "en": "Cross-Domain"},

    # --- Cell values ---
    "val.built": {"zh": "已建", "en": "Built"},
    "val.yes": {"zh": "是", "en": "Yes"},
    "val.no": {"zh": "否", "en": "No"},
    "val.microservice_app": {"zh": "微服务应用", "en": "Microservice Application"},
    "val.param": {"zh": "参数: {param}", "en": "Parameter: {param}"},

    # --- Layer names ---
    "layer.api": {"zh": "接口服务", "en": "API Service"},
    "layer.business": {"zh": "业务逻辑", "en": "Business Logic"},
    "layer.data_access": {"zh": "数据访问", "en": "Data Access"},
    "layer.entity": {"zh": "数据实体", "en": "Data Entity"},

    # --- PPTX titles ---
    "pptx.arch_diagram": {"zh": "应用架构图 - {name}", "en": "Application Architecture - {name}"},
    "pptx.integration_diagram": {"zh": "应用集成图 - {name}", "en": "Application Integration - {name}"},
    "pptx.domain_label": {"zh": "应用域: {name}", "en": "Domain: {name}"},

    # --- Font ---
    "font.name": {"zh": "微软雅黑", "en": "Calibri"},

    # --- MCP error messages ---
    "err.path_not_found": {"zh": "路径不存在: {path}", "en": "Path does not exist: {path}"},
    "err.no_pom": {"zh": "未找到 pom.xml，请确认是 Maven 项目: {path}", "en": "pom.xml not found, please confirm Maven project: {path}"},
    "msg.da_not_supported": {"zh": "数据架构（DA）制品生成尚未支持，敬请期待下一版本。", "en": "Data Architecture (DA) generation is not yet supported."},
    "msg.ta_not_supported": {"zh": "技术架构（TA）制品生成尚未支持，敬请期待下一版本。", "en": "Tech Architecture (TA) generation is not yet supported."},

    # --- LLM prompts ---
    "llm.enhance_endpoint": {
        "zh": "将以下Java方法名翻译为简短的中文业务功能名称（只返回中文名称，不要解释）：{method_name}",
        "en": "Translate the following Java method name into a short English business function name (return only the name, no explanation): {method_name}",
    },
    "llm.enhance_module": {
        "zh": "根据以下Java模块的类名列表，用一句中文描述该模块的业务职责（20字以内）：\n模块名：{module_name}\n类：{classes}",
        "en": "Based on the following Java module class list, describe the module's responsibility in one English sentence (under 20 words):\nModule: {module_name}\nClasses: {classes}",
    },
    "llm.enhance_integration": {
        "zh": "用一句中文描述以下应用集成关系（20字以内）：\n调用方：{source}\n被调用方：{target}\n方式：{type}\n接口：{interface}\n方法：{methods}",
        "en": "Describe the following integration in one English sentence (under 20 words):\nCaller: {source}\nCallee: {target}\nMethod: {type}\nInterface: {interface}\nMethods: {methods}",
    },
    "llm.fallback_module_desc": {
        "zh": "管理{name}相关业务",
        "en": "Manages {name} related business",
    },
    "llm.fallback_integration_desc": {
        "zh": "{source} 通过 {type} 调用 {target}",
        "en": "{source} calls {target} via {type}",
    },
}


HEADER_KEYS: dict[str, list[str]] = {
    "aa01": [
        "h.aa01.domain_id", "h.aa01.domain_name",
        "h.aa01.group_id", "h.aa01.group_name",
        "h.aa01.l1_module_id", "h.aa01.l1_module_name",
        "h.aa01.l2_module_id", "h.aa01.l2_module_name",
        "h.aa01.status",
    ],
    "aa02": [
        "h.aa02.func_id", "h.aa02.func_name", "h.aa02.func_desc",
        "h.aa02.module", "h.aa02.http_method", "h.aa02.api_path",
    ],
    "aa03": [
        "h.aa03.sub_id", "h.aa03.sub_name", "h.aa03.sub_desc",
        "h.aa03.parent_id", "h.aa03.module",
    ],
    "aa04": [
        "h.aa04.func_id", "h.aa04.func_name",
        "h.aa04.system", "h.aa04.category",
        "h.aa04.microservice", "h.aa04.module",
    ],
    "aa05": [
        "h.aa05.integ_id", "h.aa05.input_module", "h.aa05.output_module",
        "h.aa05.integ_type", "h.aa05.interface", "h.aa05.methods",
        "h.aa05.entities", "h.aa05.cross_domain",
    ],
}


def t(key: str, locale: str = "zh", **kwargs) -> str:
    """Look up a translated string by key and locale, with optional format args."""
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    text = entry.get(locale, entry.get("zh", key))
    if kwargs:
        return text.format(**kwargs)
    return text


def get_headers(sheet_id: str, locale: str = "zh") -> list[str]:
    """Return the ordered headers list for a given sheet, respecting locale."""
    header_keys = HEADER_KEYS.get(sheet_id, [])
    return [t(k, locale) for k in header_keys]
