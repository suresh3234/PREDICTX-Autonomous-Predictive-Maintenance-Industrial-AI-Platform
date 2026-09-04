import inspect
import json
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger("PredictX.MCP.Base")


class MCPServerBase:
    """
    Model Context Protocol (MCP) Server Base.
    Implements standard JSON-RPC 2.0 tool registration, schema introspection (tools/list),
    and tool execution (tools/call).
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: dict[str, dict[str, Any]] = {}

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str,
        input_schema: dict[str, Any] | None = None,
    ):
        """
        Registers a tool function into the MCP server registry.
        """
        if input_schema is None:
            # Auto-generate schema from function signature
            sig = inspect.signature(func)
            properties = {}
            required = []
            for param_name, param in sig.parameters.items():
                if param_name in ["self", "cls"]:
                    continue
                param_type = "string"
                if param.annotation is int:
                    param_type = "integer"
                elif param.annotation is float:
                    param_type = "number"
                elif param.annotation is bool:
                    param_type = "boolean"
                elif param.annotation is list:
                    param_type = "array"
                elif param.annotation is dict:
                    param_type = "object"

                properties[param_name] = {"type": param_type}
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)

            input_schema = {
                "type": "object",
                "properties": properties,
                "required": required,
            }

        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema,
            "handler": func,
        }
        logger.info(f"Registered MCP tool: '{name}' on server '{self.name}'")

    def tool(self, name: str | None = None, description: str = "", input_schema: dict[str, Any] | None = None):
        """Decorator for registering an MCP tool."""
        def decorator(func: Callable):
            tool_name = name or func.__name__
            desc = description or (func.__doc__ or "").strip()
            self.register_tool(tool_name, func, desc, input_schema)
            return func
        return decorator

    def list_tools(self) -> list[dict[str, Any]]:
        """Returns the list of tool definitions for tools/list."""
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "inputSchema": t["inputSchema"],
            }
            for t in self.tools.values()
        ]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Executes a registered tool and formats the MCP response.
        """
        if name not in self.tools:
            return {
                "content": [{"type": "text", "text": f"Tool '{name}' not found on server '{self.name}'"}],
                "isError": True,
            }

        tool_info = self.tools[name]
        handler = tool_info["handler"]

        try:
            result = handler(**arguments)
            # Serialize result to JSON string if it is dict/list
            if isinstance(result, (dict, list)):
                result_text = json.dumps(result, indent=2, default=str)
            else:
                result_text = str(result)

            return {
                "content": [{"type": "text", "text": result_text}],
                "isError": False,
            }
        except Exception as e:
            logger.error(f"Error executing tool '{name}': {e}", exc_info=True)
            return {
                "content": [{"type": "text", "text": f"Execution error in '{name}': {str(e)}"}],
                "isError": True,
            }

    def handle_json_rpc(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Standard JSON-RPC 2.0 Request Dispatcher.
        """
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.list_tools()},
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            call_res = self.call_tool(tool_name, tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": call_res,
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"},
            }
