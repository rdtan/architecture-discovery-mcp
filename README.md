# Architecture Discovery MCP

[English](#english) | [中文](#中文)

---

<a id="english"></a>

## English

Auto-discover enterprise architecture artifacts from Java/Maven source code. Scan your project and generate TOGAF-standard deliverables in seconds — application architecture, data architecture, and data lineage.

### What It Does

Point it at a Java/Maven project and get:

**Application Architecture (AA):**
- **AA-01** Application Module Inventory (Excel)
- **AA-02** Function Item Inventory (Excel)
- **AA-03** Sub-function Inventory (Excel)
- **AA-04** Function Distribution (Excel)
- **AA-05** Integration Inventory (Excel)
- **AA-07** Application Architecture Diagram (PPTX)
- **AA-08** Application Integration Diagram (PPTX)

**Data Architecture (DA):**
- **DA-01** Conceptual Entity List (Excel)
- **DA-02** Logical Entity List (Excel)
- **DA-03** Physical Entity List (Excel)
- **DA-04** Database Table List (Excel)
- **DA-05** Data Source List (Excel)
- **DA-06** Table-Function Relationship (Excel)
- **DA-07** Data Dictionary (Excel)
- **DA-CDM** Conceptual Data Model Diagram (PPTX)
- **DA-LDM** Logical Data Model Diagram (PPTX)
- **DA-Flow** Data Flow Diagram (PPTX)

**Data Lineage:**
- **DA-08** Field-Level Lineage Inventory (Excel)
- **DA-09** Data Flow Inventory (Excel)
- **DA-LINEAGE** Data Lineage Diagram (PPTX)
- **DA-IMPACT** Impact Analysis Report (Excel, per field)

All generated from static analysis — no runtime required, no code leaves your machine.

### Install

```bash
pip install architecture-discovery-mcp
```

Requires Python 3.11+.

### Usage

#### As an MCP Server (recommended)

The engine runs as an [MCP](https://modelcontextprotocol.io/) server over stdio. Configure it in your AI IDE:

**Claude Code** (`~/.claude.json`):
```json
{
  "mcpServers": {
    "architecture-discovery": {
      "command": "architecture-discovery-mcp"
    }
  }
}
```

**Cursor** (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "architecture-discovery": {
      "command": "architecture-discovery-mcp"
    }
  }
}
```

**VS Code** (`.vscode/settings.json`):
```json
{
  "mcp": {
    "servers": {
      "architecture-discovery": {
        "command": "architecture-discovery-mcp"
      }
    }
  }
}
```

Then ask your AI assistant naturally:

> "Scan D:/projects/my-java-app and generate the application architecture artifacts"

#### Available MCP Tools

| Tool | Description |
|------|-------------|
| `scan_project_tool` | Scan project structure, return modules/frameworks overview |
| `generate_app_architecture_tool` | Generate full AA artifact set (Excel + PPTX) |
| `generate_data_architecture` | Generate full DA artifact set (DA-01 to DA-07 + diagrams) |
| `generate_data_lineage_tool` | Generate data lineage artifacts (DA-08, DA-09, DA-LINEAGE) |
| `analyze_field_impact` | Analyze downstream impact of a field change, optionally export Excel |
| `export_intermediate_data` | Export structured analysis as JSON |
| `generate_tech_architecture` | TA artifacts (coming soon) |

All tools accept an optional `locale` parameter (`"zh"` or `"en"`, default `"zh"`).

#### As a Python Library

```python
from pathlib import Path
from src.scanner.project_scanner import scan_project
from src.analyzers.module_analyzer import analyze_modules
from src.analyzers.api_analyzer import analyze_apis
from src.analyzers.integration_analyzer import analyze_integrations
from src.generators.app_architecture_generator import generate_app_architecture

project = scan_project(Path("your-java-project"))
project = analyze_modules(project)
endpoints = analyze_apis(project)
integrations = analyze_integrations(project)

out = Path("output")
generate_app_architecture(project, endpoints, integrations, out, locale="en")
```

#### Data Lineage

```python
from src.generators.lineage_combined_generator import generate_data_lineage
from src.generators.da_impact_generator import generate_da_impact

project = scan_project(Path("your-java-project"))
project = analyze_modules(project)

result = generate_data_lineage(project, Path("output"), locale="en")
graph = result["graph"]

# Impact analysis for a specific field
impact_path = generate_da_impact(graph, "order-service.Order.id", Path("output"), locale="en")
```

### Supported Projects

- Java/Maven projects (must have `pom.xml`)
- Spring Boot / Spring Cloud microservices
- Feign client integration detection
- JPA entity detection (@Entity, @Table, @Column)
- MyBatis mapper XML parsing (including `<association>` / `<collection>`)
- MapStruct `@Mapping` annotation lineage
- Setter/getter chain detection (BeanUtils.copyProperties)
- SQL field source analysis (INSERT...SELECT via sqlparse)
- MQ producer detection (KafkaTemplate, RabbitTemplate, @SendTo)
- @Scheduled ETL task detection
- Enum scanning and data dictionary generation
- Nested multi-module projects

### Internationalization

Artifacts can be generated in Chinese (`locale="zh"`, default) or English (`locale="en"`). This controls:

- Excel column headers and sheet names
- Cell values (layer names, status labels)
- PPTX slide titles and diagram labels
- Font selection (Microsoft YaHei for Chinese, Calibri for English)

### Security

- Runs locally via stdio — no network exposure
- Source code never leaves your machine
- Exported JSON contains only structural metadata, not source code

### Development

```bash
git clone https://github.com/rdtan/architecture-discovery-mcp.git
cd architecture-discovery-mcp
pip install -e ".[dev]"
pytest tests/ -v
```

### License

MIT

---

<a id="中文"></a>

## 中文

从 Java/Maven 源码自动发现企业架构制品。扫描项目即可在数秒内生成符合 TOGAF 标准的交付物——应用架构、数据架构和数据血缘。

### 功能概览

指向一个 Java/Maven 项目即可获得：

**应用架构 (AA)：**
- **AA-01** 应用模块清单 (Excel)
- **AA-02** 功能项清单 (Excel)
- **AA-03** 子功能清单 (Excel)
- **AA-04** 功能分布矩阵 (Excel)
- **AA-05** 集成清单 (Excel)
- **AA-07** 应用架构图 (PPTX)
- **AA-08** 应用集成图 (PPTX)

**数据架构 (DA)：**
- **DA-01** 概念实体清单 (Excel)
- **DA-02** 逻辑实体清单 (Excel)
- **DA-03** 物理实体清单 (Excel)
- **DA-04** 数据库表清单 (Excel)
- **DA-05** 数据来源清单 (Excel)
- **DA-06** 表-功能关系 (Excel)
- **DA-07** 数据字典 (Excel)
- **DA-CDM** 概念数据模型图 (PPTX)
- **DA-LDM** 逻辑数据模型图 (PPTX)
- **DA-Flow** 数据流转图 (PPTX)

**数据血缘：**
- **DA-08** 字段级映射清单 (Excel)
- **DA-09** 数据流转清单 (Excel)
- **DA-LINEAGE** 数据血缘图 (PPTX)
- **DA-IMPACT** 影响分析报告 (Excel，按字段)

全部基于静态分析生成——无需运行时环境，代码不会离开你的机器。

### 安装

```bash
pip install architecture-discovery-mcp
```

需要 Python 3.11+。

### 使用方式

#### 作为 MCP Server（推荐）

本工具以 [MCP](https://modelcontextprotocol.io/) 协议通过 stdio 运行。在 AI IDE 中配置：

**Claude Code** (`~/.claude.json`):
```json
{
  "mcpServers": {
    "architecture-discovery": {
      "command": "architecture-discovery-mcp"
    }
  }
}
```

**Cursor** (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "architecture-discovery": {
      "command": "architecture-discovery-mcp"
    }
  }
}
```

**VS Code** (`.vscode/settings.json`):
```json
{
  "mcp": {
    "servers": {
      "architecture-discovery": {
        "command": "architecture-discovery-mcp"
      }
    }
  }
}
```

然后用自然语言对 AI 助手说：

> "扫描 D:/projects/my-java-app 并生成应用架构制品"

#### 可用 MCP 工具

| 工具 | 功能 |
|------|------|
| `scan_project_tool` | 扫描项目结构，返回模块/框架概览 |
| `generate_app_architecture_tool` | 生成完整 AA 制品集（Excel + PPTX） |
| `generate_data_architecture` | 生成完整 DA 制品集（DA-01 到 DA-07 + 图表） |
| `generate_data_lineage_tool` | 生成数据血缘制品（DA-08、DA-09、DA-LINEAGE） |
| `analyze_field_impact` | 分析字段变更的下游影响，可选导出 Excel 报告 |
| `export_intermediate_data` | 导出结构化分析数据为 JSON |
| `generate_tech_architecture` | TA 制品（开发中） |

所有工具支持可选参数 `locale`（`"zh"` 或 `"en"`，默认 `"zh"`）。

#### 作为 Python 库使用

```python
from pathlib import Path
from src.scanner.project_scanner import scan_project
from src.analyzers.module_analyzer import analyze_modules
from src.generators.lineage_combined_generator import generate_data_lineage
from src.generators.da_impact_generator import generate_da_impact

project = scan_project(Path("your-java-project"))
project = analyze_modules(project)

# 生成数据血缘制品
result = generate_data_lineage(project, Path("output"), locale="zh")
graph = result["graph"]

# 影响分析
impact_path = generate_da_impact(graph, "order-service.Order.id", Path("output"), locale="zh")
```

### 支持的项目类型

- Java/Maven 项目（需包含 `pom.xml`）
- Spring Boot / Spring Cloud 微服务
- Feign 客户端集成检测
- JPA 实体检测（@Entity、@Table、@Column）
- MyBatis Mapper XML 解析（含 `<association>` / `<collection>`）
- MapStruct `@Mapping` 注解血缘
- Setter/Getter 链检测（BeanUtils.copyProperties）
- SQL 字段来源分析（INSERT...SELECT，基于 sqlparse）
- MQ 生产者检测（KafkaTemplate、RabbitTemplate、@SendTo）
- @Scheduled ETL 任务检测
- 枚举扫描和数据字典生成
- 嵌套多模块项目

### 国际化

制品可以生成中文（`locale="zh"`，默认）或英文（`locale="en"`）版本，控制：

- Excel 列头和 Sheet 名
- 单元格内容（层级名称、状态标签）
- PPTX 幻灯片标题和图表标注
- 字体选择（中文用微软雅黑，英文用 Calibri）

### 安全性

- 本地通过 stdio 运行——无网络暴露
- 源代码不会离开你的机器
- 导出的 JSON 仅包含结构元数据，不含源代码

### 开发

```bash
git clone https://github.com/rdtan/architecture-discovery-mcp.git
cd architecture-discovery-mcp
pip install -e ".[dev]"
pytest tests/ -v
```

### 许可证

MIT
