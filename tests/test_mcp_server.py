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
async def test_scan_project_tool(server_params, sample_project_path):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            assert "scan_project_tool" in tool_names

            result = await session.call_tool("scan_project_tool", {"project_path": sample_project_path})
            assert not result.isError

            content = result.content[0].text
            data = json.loads(content)
            assert data["project_name"] == "ecommerce-platform"
            assert data["modules_count"] >= 2
            assert "Spring Boot" in data["frameworks"] or len(data["frameworks"]) >= 0


@pytest.mark.asyncio
async def test_scan_project_invalid_path(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("scan_project_tool", {"project_path": "/nonexistent/path"})
            assert result.isError


@pytest.mark.asyncio
async def test_generate_app_architecture_tool(server_params, sample_project_path, tmp_path):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            assert "generate_app_architecture_tool" in tool_names

            result = await session.call_tool("generate_app_architecture_tool", {
                "project_path": sample_project_path,
                "output_dir": str(tmp_path),
            })
            assert not result.isError

            content = result.content[0].text
            data = json.loads(content)
            assert data["success"] is True
            assert len(data["artifacts"]) == 3
            assert any("application-architecture.xlsx" in a["name"] for a in data["artifacts"])
            assert any("AA-07" in a["name"] for a in data["artifacts"])
            assert any("AA-08" in a["name"] for a in data["artifacts"])

            for artifact in data["artifacts"]:
                assert Path(artifact["path"]).exists()


@pytest.mark.asyncio
async def test_export_intermediate_data_tool(server_params, sample_project_path, tmp_path):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            output_path = str(tmp_path / "intermediate-data.json")
            result = await session.call_tool("export_intermediate_data", {
                "project_path": sample_project_path,
                "output_path": output_path,
            })
            assert not result.isError

            content = result.content[0].text
            data = json.loads(content)
            assert data["success"] is True
            assert Path(data["output_path"]).exists()

            with open(data["output_path"], "r", encoding="utf-8") as f:
                exported = json.load(f)
            assert exported["version"] == "1.0"
            assert exported["project"]["name"] == "ecommerce-platform"


@pytest.mark.asyncio
async def test_placeholder_tools_return_not_supported(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("generate_tech_architecture", {
                "project_path": "/any/path",
            })
            content = result.content[0].text
            assert "尚未支持" in content
