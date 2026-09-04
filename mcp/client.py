import logging
from typing import Any

from mcp.alert_server.server import AlertMCPServer
from mcp.base import MCPServerBase
from mcp.database_server.server import DatabaseMCPServer
from mcp.knowledge_server.server import KnowledgeMCPServer
from mcp.maintenance_server.server import MaintenanceMCPServer
from mcp.sensor_server.server import SensorMCPServer

logger = logging.getLogger("PredictX.MCP.Client")


class MCPClient:
    """
    Unified MCP Client for autonomous AI agent tool execution.
    Manages connections across the PredictX MCP tool server suite.
    """

    def __init__(self, auto_mount_default_servers: bool = True):
        self.servers: dict[str, MCPServerBase] = {}
        self.tool_to_server_map: dict[str, str] = {}

        if auto_mount_default_servers:
            self.mount_server("sensor", SensorMCPServer())
            self.mount_server("database", DatabaseMCPServer())
            self.mount_server("knowledge", KnowledgeMCPServer())
            self.mount_server("maintenance", MaintenanceMCPServer())
            self.mount_server("alert", AlertMCPServer())

    def mount_server(self, server_id: str, server: MCPServerBase):
        """Mounts an MCP server into the client router."""
        self.servers[server_id] = server
        for tool_name in server.tools.keys():
            self.tool_to_server_map[tool_name] = server_id
        logger.info(f"Mounted MCP server '{server_id}' with {len(server.tools)} tools.")

    def list_all_tools(self) -> list[dict[str, Any]]:
        """Aggregates all tool schemas across all mounted servers."""
        all_tools = []
        for server_id, srv in self.servers.items():
            for t in srv.list_tools():
                tool_def = dict(t)
                tool_def["server_id"] = server_id
                all_tools.append(tool_def)
        return all_tools

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Routes and executes a tool call to the matching MCP server.
        """
        if tool_name not in self.tool_to_server_map:
            return {
                "content": [{"type": "text", "text": f"Tool '{tool_name}' not registered on any mounted MCP server."}],
                "isError": True,
            }

        server_id = self.tool_to_server_map[tool_name]
        server = self.servers[server_id]

        response = server.handle_json_rpc({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        })

        if "error" in response:
            return {
                "content": [{"type": "text", "text": response["error"]["message"]}],
                "isError": True,
            }

        return response.get("result", {})
