# Architecture Discovery Engine

Auto-discover enterprise architecture artifacts from Java/Maven source code. Scan your project and generate TOGAF-standard application architecture deliverables in seconds.

## What It Does

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

All generated from static analysis — no runtime required, no code leaves your machine.

## Install

```bash
pip install architecture-discovery-mcp
```

Requires Python 3.11+.

## Usage

### As an MCP Server (recommended)

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

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `scan_project_tool` | Scan project structure, return modules/frameworks overview |
| `generate_app_architecture_tool` | Generate full AA artifact set (Excel + PPTX) |
| `export_intermediate_data` | Export structured analysis as JSON |
| `generate_data_architecture` | Generate full DA artifact set (Excel + PPTX) |
| `generate_tech_architecture` | TA artifacts (coming soon) |

All tools accept an optional `locale` parameter (`"zh"` or `"en"`, default `"zh"`).

### As a Python Library

```python
from pathlib import Path
from src.scanner.project_scanner import scan_project
from src.analyzers.module_analyzer import analyze_modules
from src.analyzers.api_analyzer import analyze_apis
from src.analyzers.integration_analyzer import analyze_integrations
from src.generators.app_architecture_generator import generate_app_architecture
from src.generators.aa07_generator import generate_aa07
from src.generators.aa08_generator import generate_aa08

project = scan_project(Path("your-java-project"))
project = analyze_modules(project)
endpoints = analyze_apis(project)
integrations = analyze_integrations(project)

out = Path("output")
generate_app_architecture(project, endpoints, integrations, out, locale="en")
generate_aa07(project, out, locale="en")
generate_aa08(project, integrations, out, locale="en")
```

### Data Architecture Generation

```python
from src.analyzers.data_entity_analyzer import analyze_data_entities
from src.analyzers.enum_analyzer import analyze_enums
from src.analyzers.crud_analyzer import analyze_crud
from src.generators.da_combined_generator import generate_all_da

project = scan_project(Path("your-java-project"))
project = analyze_modules(project)
endpoints = analyze_apis(project)

entities = analyze_data_entities(project)
enums = analyze_enums(project)
crud_records = analyze_crud(entities, endpoints)

generate_all_da(project, entities, enums, crud_records, out, locale="en")
```

## Supported Projects

- Java/Maven projects (must have `pom.xml`)
- Spring Boot / Spring Cloud microservices
- Feign client integration detection
- JPA entity detection (@Entity, @Table, @Column)
- MyBatis mapper XML parsing
- Enum scanning and data dictionary generation
- Nested multi-module projects (e.g. RuoYi-Cloud style)

## Internationalization

Artifacts can be generated in Chinese (`locale="zh"`, default) or English (`locale="en"`). This controls:

- Excel column headers and sheet names
- Cell values (layer names, status labels)
- PPTX slide titles and diagram labels
- Font selection (Microsoft YaHei for Chinese, Calibri for English)

## Security

- Runs locally via stdio — no network exposure
- Source code never leaves your machine
- Exported JSON contains only structural metadata (class names, API paths, annotations), not source code

## Development

```bash
git clone <repo-url>
cd architecture-discovery-engine
pip install -e ".[dev]"
pytest tests/ -v
```

## License

MIT
