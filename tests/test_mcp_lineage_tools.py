"""Tests for MCP server lineage tools: generate_data_lineage_tool and analyze_field_impact."""

import pytest
import json
from pathlib import Path
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


@pytest.fixture
def sample_project_path():
    return str(Path(__file__).parent / "fixtures" / "sample-java-project")


@pytest.fixture
def server_params():
    return StdioServerParameters(
        command="python",
        args=["-m", "src.mcp_server"],
    )


@pytest.mark.asyncio
async def test_generate_data_lineage_tool(server_params, sample_project_path, tmp_path):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            assert "generate_data_lineage_tool" in tool_names

            result = await session.call_tool(
                "generate_data_lineage_tool",
                {"project_path": sample_project_path, "output_dir": str(tmp_path), "locale": "zh"},
            )
            assert not result.isError

            content = result.content[0].text
            data = json.loads(content)
            assert data["success"] is True
            assert "stats" in data
            assert data["stats"]["total_lineages"] >= 0
            assert "artifacts" in data
            assert len(data["artifacts"]) >= 2


@pytest.mark.asyncio
async def test_generate_data_lineage_tool_en(server_params, sample_project_path, tmp_path):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "generate_data_lineage_tool",
                {"project_path": sample_project_path, "output_dir": str(tmp_path), "locale": "en"},
            )
            assert not result.isError

            data = json.loads(result.content[0].text)
            assert data["success"] is True
            filenames = [a["name"] for a in data["artifacts"]]
            assert any("Field_Level_Lineage" in n for n in filenames)
            assert any("Data_Flow_Inventory" in n for n in filenames)


@pytest.mark.asyncio
async def test_generate_data_lineage_tool_invalid_path(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "generate_data_lineage_tool",
                {"project_path": "/nonexistent/path"},
            )
            assert result.isError


@pytest.mark.asyncio
async def test_analyze_field_impact(server_params, sample_project_path):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            assert "analyze_field_impact" in tool_names

            result = await session.call_tool(
                "analyze_field_impact",
                {"project_path": sample_project_path, "field": "order-service.Order.id"},
            )
            assert not result.isError

            data = json.loads(result.content[0].text)
            assert "field" in data
            assert data["field"] == "order-service.Order.id"
            assert "total_affected" in data
            assert "downstream_fields" in data
            assert "paths" in data
            assert isinstance(data["downstream_fields"], list)
            assert isinstance(data["paths"], list)


@pytest.mark.asyncio
async def test_analyze_field_impact_nonexistent_field(server_params, sample_project_path):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "analyze_field_impact",
                {"project_path": sample_project_path, "field": "nonexistent.Entity.field"},
            )
            assert not result.isError

            data = json.loads(result.content[0].text)
            assert data["total_affected"] == 0
            assert data["downstream_fields"] == []
            assert data["paths"] == []


@pytest.mark.asyncio
async def test_analyze_field_impact_invalid_path(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "analyze_field_impact",
                {"project_path": "/nonexistent/path", "field": "x.y.z"},
            )
            assert result.isError
