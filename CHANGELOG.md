# Changelog

All notable changes to this project will be documented in this file.

## [0.5.0] - 2026-08-04

### Added
- **Data Lineage (DA-08/DA-09/DA-LINEAGE/DA-IMPACT)**
  - Field-level lineage detection: MapStruct `@Mapping`, setter/getter chains, BeanUtils.copyProperties, SQL INSERT...SELECT
  - Cross-system data flow detection: MQ producers (KafkaTemplate, RabbitTemplate, @SendTo), @Scheduled ETL tasks
  - NetworkX-based lineage graph engine with forward/backward tracing and impact analysis
  - DA-08 Field-Level Lineage Inventory (Excel)
  - DA-09 Data Flow Inventory (Excel)
  - DA-LINEAGE Data Lineage Diagram (PPTX) with smart compact layout
  - DA-IMPACT Impact Analysis Report (Excel, per field)
  - MCP tool `generate_data_lineage_tool`: full lineage pipeline
  - MCP tool `analyze_field_impact`: field-level impact analysis with optional Excel export

### Changed
- PPTX lineage diagram uses smart partitioning (large systems get own slide, small systems merge)
- Multi-column grid layout for compact entity display
- Deterministic color assignment (stable across runs)
- Arrowheads on connectors to indicate data flow direction
- Legend filtered to show only mapping types present on each slide

### Dependencies
- Added `networkx>=3.0`
- Added `sqlparse>=0.5.0`

## [0.4.0] - 2025-06-15

### Added
- **Data Architecture (DA-01 to DA-07 + diagrams)**
  - DA-01 Conceptual Entity List
  - DA-02 Logical Entity List
  - DA-03 Physical Entity List
  - DA-04 Database Table List
  - DA-05 Data Source List
  - DA-06 Table-Function Relationship
  - DA-07 Data Dictionary (Enum)
  - DA-CDM Conceptual Data Model Diagram (PPTX)
  - DA-LDM Logical Data Model Diagram (PPTX)
  - DA-Flow Data Flow Diagram (PPTX)
  - MCP tool `generate_data_architecture`
- JPA entity detection (@Entity, @Table, @Column)
- MyBatis mapper XML parsing
- Enum scanning and data dictionary generation
- CRUD analysis (entity-to-function relationship)

## [0.3.0] - 2025-05-01

### Added
- **Application Architecture (AA-01 to AA-08)**
  - AA-01 Application Module Inventory
  - AA-02 Function Item Inventory
  - AA-03 Sub-function Inventory
  - AA-04 Function Distribution Matrix
  - AA-05 Integration Inventory
  - AA-07 Application Architecture Diagram (PPTX)
  - AA-08 Application Integration Diagram (PPTX)
  - MCP tools: `scan_project_tool`, `generate_app_architecture_tool`, `export_intermediate_data`
- Java/Maven project scanning with multi-module support
- Spring Boot annotation parsing (REST controllers, Feign clients)
- Internationalization (Chinese/English) for all artifacts
- MCP server over stdio
