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

    # --- DA Sheet names ---
    "sheet.da01": {"zh": "DA-01 概念实体清单", "en": "DA-01 Conceptual Entity List"},
    "sheet.da02": {"zh": "DA-02 逻辑实体清单", "en": "DA-02 Logical Entity List"},
    "sheet.da03": {"zh": "DA-03 物理实体清单", "en": "DA-03 Physical Entity List"},
    "sheet.da04": {"zh": "DA-04 库表清单", "en": "DA-04 Database Table List"},
    "sheet.da05": {"zh": "DA-05 数据源清单", "en": "DA-05 Data Source List"},
    "sheet.da06": {"zh": "DA-06 库表-功能子项关系", "en": "DA-06 Table-Function Relationship"},
    "sheet.da07": {"zh": "DA-07 数据字典表", "en": "DA-07 Data Dictionary"},

    # --- DA-01 Headers (概念实体清单) ---
    "h.da01.data_domain_id": {"zh": "数据域编号", "en": "Data Domain ID"},
    "h.da01.data_domain_name": {"zh": "数据域名称", "en": "Data Domain Name"},
    "h.da01.entity_id": {"zh": "概念实体编号", "en": "Conceptual Entity ID"},
    "h.da01.entity_name": {"zh": "概念实体名称", "en": "Conceptual Entity Name"},
    "h.da01.business_object": {"zh": "关联业务对象", "en": "Related Business Object"},
    "h.da01.is_core": {"zh": "是否核心实体", "en": "Is Core Entity"},
    "h.da01.data_category": {"zh": "数据分类", "en": "Data Category"},
    "h.da01.data_owner": {"zh": "数据Owner", "en": "Data Owner"},

    # --- DA-02 Headers (逻辑实体清单) ---
    "h.da02.data_domain": {"zh": "数据域", "en": "Data Domain"},
    "h.da02.concept_entity_id": {"zh": "概念实体编号", "en": "Conceptual Entity ID"},
    "h.da02.concept_entity_name": {"zh": "概念实体名称", "en": "Conceptual Entity Name"},
    "h.da02.logical_entity_id": {"zh": "逻辑实体编码", "en": "Logical Entity ID"},
    "h.da02.logical_entity_name": {"zh": "逻辑实体名称", "en": "Logical Entity Name"},
    "h.da02.attr_name": {"zh": "属性名", "en": "Attribute Name"},
    "h.da02.attr_code": {"zh": "属性代码", "en": "Attribute Code"},
    "h.da02.data_type": {"zh": "数据类型", "en": "Data Type"},
    "h.da02.is_pk": {"zh": "是否主键", "en": "Is Primary Key"},
    "h.da02.is_fk": {"zh": "是否外键", "en": "Is Foreign Key"},
    "h.da02.is_not_null": {"zh": "是否非空", "en": "Is Not Null"},

    # --- DA-03 Headers (物理实体清单) ---
    "h.da03.data_domain": {"zh": "数据域", "en": "Data Domain"},
    "h.da03.logical_entity_id": {"zh": "逻辑实体编码", "en": "Logical Entity ID"},
    "h.da03.logical_entity_name": {"zh": "逻辑实体名称", "en": "Logical Entity Name"},
    "h.da03.physical_entity_id": {"zh": "物理实体编码", "en": "Physical Entity ID"},
    "h.da03.physical_entity_name": {"zh": "物理实体名称", "en": "Physical Entity Name"},
    "h.da03.field_name": {"zh": "字段名称", "en": "Field Name"},
    "h.da03.field_code": {"zh": "字段代码", "en": "Field Code"},
    "h.da03.data_type": {"zh": "数据类型", "en": "Data Type"},

    # --- DA-04 Headers (库表清单) ---
    "h.da04.data_domain": {"zh": "数据域", "en": "Data Domain"},
    "h.da04.physical_entity_id": {"zh": "物理实体编码", "en": "Physical Entity ID"},
    "h.da04.physical_entity_name": {"zh": "物理实体名称", "en": "Physical Entity Name"},
    "h.da04.table_id": {"zh": "库表编码", "en": "Table ID"},
    "h.da04.table_name": {"zh": "库表名称", "en": "Table Name"},
    "h.da04.field_name": {"zh": "字段名称", "en": "Field Name"},
    "h.da04.field_code": {"zh": "字段代码", "en": "Field Code"},
    "h.da04.system_name": {"zh": "系统名称", "en": "System Name"},
    "h.da04.db_type": {"zh": "数据库类型", "en": "Database Type"},

    # --- DA-05 Headers (数据源清单) ---
    "h.da05.data_domain": {"zh": "数据域", "en": "Data Domain"},
    "h.da05.concept_entity_id": {"zh": "概念实体编号", "en": "Conceptual Entity ID"},
    "h.da05.concept_entity_name": {"zh": "概念实体名称", "en": "Conceptual Entity Name"},
    "h.da05.logical_entity_id": {"zh": "逻辑实体编码", "en": "Logical Entity ID"},
    "h.da05.logical_entity_name": {"zh": "逻辑实体名称", "en": "Logical Entity Name"},
    "h.da05.operation_type": {"zh": "操作类型", "en": "Operation Type"},
    "h.da05.app_name": {"zh": "应用名称", "en": "Application Name"},
    "h.da05.function_module": {"zh": "功能模块", "en": "Function Module"},
    "h.da05.function_item": {"zh": "功能子项", "en": "Function Item"},

    # --- DA-06 Headers (库表-功能子项关系) ---
    "h.da06.source_system": {"zh": "来源系统", "en": "Source System"},
    "h.da06.table_id": {"zh": "库表编码", "en": "Table ID"},
    "h.da06.table_name": {"zh": "库表名称", "en": "Table Name"},
    "h.da06.operation_type": {"zh": "操作类型", "en": "Operation Type"},
    "h.da06.app_name": {"zh": "应用名称", "en": "Application Name"},
    "h.da06.function_module": {"zh": "功能模块", "en": "Function Module"},
    "h.da06.function_item": {"zh": "功能子项", "en": "Function Item"},

    # --- DA-07 Headers (数据字典表) ---
    "h.da07.enum_type_id": {"zh": "枚举类型ID", "en": "Enum Type ID"},
    "h.da07.enum_type_name": {"zh": "枚举类型名称", "en": "Enum Type Name"},
    "h.da07.enum_cn_name": {"zh": "枚举中文名称", "en": "Enum Chinese Name"},
    "h.da07.enum_value": {"zh": "枚举值", "en": "Enum Value"},
    "h.da07.enum_en_name": {"zh": "枚举英文名称", "en": "Enum English Name"},
    "h.da07.status": {"zh": "启用状态", "en": "Status"},
    "h.da07.related_attr": {"zh": "关联属性代码", "en": "Related Attribute Code"},

    # --- DA cell values ---
    "val.master_data": {"zh": "主数据", "en": "Master Data"},
    "val.transaction_data": {"zh": "事务数据", "en": "Transaction Data"},
    "val.enabled": {"zh": "启用", "en": "Enabled"},
    "val.create": {"zh": "创建", "en": "Create"},
    "val.read": {"zh": "读取", "en": "Read"},
    "val.update": {"zh": "修改", "en": "Update"},
    "val.delete": {"zh": "删除", "en": "Delete"},

    # --- DA PPTX titles ---
    "pptx.cdm_diagram": {"zh": "概念数据模型 - {name}", "en": "Conceptual Data Model - {name}"},
    "pptx.ldm_diagram": {"zh": "逻辑数据模型 - {name}", "en": "Logical Data Model - {name}"},
    "pptx.data_flow_diagram": {"zh": "数据源图 - {name}", "en": "Data Flow Diagram - {name}"},

    # --- DA filenames ---
    "file.da_combined": {"zh": "data-architecture.xlsx", "en": "data-architecture.xlsx"},
    "file.da_cdm": {"zh": "DA-CDM_概念数据模型.pptx", "en": "DA-CDM_Conceptual_Data_Model.pptx"},
    "file.da_ldm": {"zh": "DA-LDM_逻辑数据模型.pptx", "en": "DA-LDM_Logical_Data_Model.pptx"},
    "file.da_flow": {"zh": "DA-FLOW_数据源图.pptx", "en": "DA-FLOW_Data_Flow_Diagram.pptx"},

    # --- DA PPTX labels ---
    "pptx.domain_group": {"zh": "数据域: {name}", "en": "Data Domain: {name}"},
    "pptx.legend_relationship": {"zh": "关系类型", "en": "Relationship Type"},
    "pptx.legend_crud": {"zh": "操作类型", "en": "Operation Type"},

    # --- DA Combined Excel ---
    "sheet.da_guide": {"zh": "说明", "en": "Guide"},
    "da.guide_title": {"zh": "数据架构制品说明", "en": "Data Architecture Artifacts Guide"},
    "da.guide_project": {"zh": "项目名称", "en": "Project Name"},
    "da.guide_generated": {"zh": "生成日期", "en": "Generated Date"},
    "da.guide_sheet_col": {"zh": "页签", "en": "Sheet"},
    "da.guide_desc_col": {"zh": "说明", "en": "Description"},
    "da.guide_ref_col": {"zh": "关联页签", "en": "Related Sheets"},
    "da.guide_da01_desc": {"zh": "按数据域列出所有概念实体，标注核心实体和数据分类", "en": "Lists all conceptual entities by data domain, marks core entities and data categories"},
    "da.guide_da02_desc": {"zh": "展开每个逻辑实体的属性明细（名称、代码、类型、主键/外键）", "en": "Expands each logical entity's attribute details (name, code, type, PK/FK)"},
    "da.guide_da03_desc": {"zh": "展开物理实体的字段明细（字段名、字段代码、数据类型）", "en": "Expands physical entity field details (field name, field code, data type)"},
    "da.guide_da04_desc": {"zh": "列出数据库库表及其字段，关联物理实体", "en": "Lists database tables and their fields, linked to physical entities"},
    "da.guide_da05_desc": {"zh": "记录每个实体被哪些应用功能执行了CRUD操作", "en": "Records which app functions perform CRUD operations on each entity"},
    "da.guide_da06_desc": {"zh": "记录每张库表被哪些功能子项执行了CRUD操作", "en": "Records which function sub-items perform CRUD on each table"},
    "da.guide_da07_desc": {"zh": "提取所有枚举类型定义及其枚举值", "en": "Extracts all enum type definitions and their values"},
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
    "da01": [
        "h.da01.data_domain_id", "h.da01.data_domain_name",
        "h.da01.entity_id", "h.da01.entity_name",
        "h.da01.business_object", "h.da01.is_core",
        "h.da01.data_category", "h.da01.data_owner",
    ],
    "da02": [
        "h.da02.data_domain", "h.da02.concept_entity_id", "h.da02.concept_entity_name",
        "h.da02.logical_entity_id", "h.da02.logical_entity_name",
        "h.da02.attr_name", "h.da02.attr_code", "h.da02.data_type",
        "h.da02.is_pk", "h.da02.is_fk", "h.da02.is_not_null",
    ],
    "da03": [
        "h.da03.data_domain", "h.da03.logical_entity_id", "h.da03.logical_entity_name",
        "h.da03.physical_entity_id", "h.da03.physical_entity_name",
        "h.da03.field_name", "h.da03.field_code", "h.da03.data_type",
    ],
    "da04": [
        "h.da04.data_domain", "h.da04.physical_entity_id", "h.da04.physical_entity_name",
        "h.da04.table_id", "h.da04.table_name",
        "h.da04.field_name", "h.da04.field_code",
        "h.da04.system_name", "h.da04.db_type",
    ],
    "da05": [
        "h.da05.data_domain", "h.da05.concept_entity_id", "h.da05.concept_entity_name",
        "h.da05.logical_entity_id", "h.da05.logical_entity_name",
        "h.da05.operation_type", "h.da05.app_name",
        "h.da05.function_module", "h.da05.function_item",
    ],
    "da06": [
        "h.da06.source_system", "h.da06.table_id", "h.da06.table_name",
        "h.da06.operation_type", "h.da06.app_name",
        "h.da06.function_module", "h.da06.function_item",
    ],
    "da07": [
        "h.da07.enum_type_id", "h.da07.enum_type_name", "h.da07.enum_cn_name",
        "h.da07.enum_value", "h.da07.enum_en_name",
        "h.da07.status", "h.da07.related_attr",
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
