import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base, Machine
from mcp.base import MCPServerBase
from mcp.sensor_server.server import SensorMCPServer
from mcp.database_server.server import DatabaseMCPServer
from mcp.knowledge_server.server import KnowledgeMCPServer
from mcp.maintenance_server.server import MaintenanceMCPServer
from mcp.alert_server.server import AlertMCPServer
from mcp.client import MCPClient


def test_mcp_base_tool_registration():
    server = MCPServerBase(name="test-server")

    @server.tool(name="calculate_power", description="Calculates power in kW from V and A")
    def calculate_power(voltage: float, current: float) -> float:
        return (voltage * current) / 1000.0

    tools = server.list_tools()
    assert len(tools) == 1
    assert tools[0]["name"] == "calculate_power"
    assert "voltage" in tools[0]["inputSchema"]["properties"]

    # Call tool via JSON-RPC
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "calculate_power", "arguments": {"voltage": 400.0, "current": 10.0}},
    }
    res = server.handle_json_rpc(req)
    assert res["jsonrpc"] == "2.0"
    assert float(res["result"]["content"][0]["text"]) == 4.0


def test_sensor_mcp_server(tmp_path):
    csv_file = tmp_path / "sensor_data.csv"
    csv_file.write_text(
        "machine_id,temperature,vibration,pressure,rpm,current,power\n"
        "M1000,68.0,1.2,100.0,1500,10.0,3.8\n"
        "M1001,82.0,4.1,75.0,1800,14.5,5.5\n"
    )

    sensor_server = SensorMCPServer(data_path=str(csv_file))
    
    # Test get_latest_telemetry
    res = sensor_server.call_tool("get_latest_telemetry", {"machine_id": "M1000"})
    data = json.loads(res["content"][0]["text"])
    assert data["temperature"] == 68.0

    # Test get_breached_sensors
    res_breach = sensor_server.call_tool("get_breached_sensors", {"machine_id": "M1001"})
    data_breach = json.loads(res_breach["content"][0]["text"])
    assert data_breach["is_anomalous"] is True
    assert len(data_breach["breaches"]) >= 2


def test_database_mcp_server():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    m1 = Machine(machine_code="M1000", machine_type="CNC Milling")
    session.add(m1)
    session.commit()

    db_server = DatabaseMCPServer(session_factory=Session)
    res = db_server.call_tool("list_machines", {})
    data = json.loads(res["content"][0]["text"])

    assert len(data) == 1
    assert data[0]["machine_code"] == "M1000"


def test_maintenance_mcp_server():
    maint_server = MaintenanceMCPServer()

    # Check spare parts inventory
    res_parts = maint_server.call_tool("check_spare_parts_inventory", {"part_no": "SKF-6205-2RSH"})
    data_parts = json.loads(res_parts["content"][0]["text"])
    assert data_parts["available"] is True
    assert data_parts["in_stock"] > 0

    # Create work order
    res_wo = maint_server.call_tool(
        "create_work_order",
        {"machine_id": "M1000", "title": "Bearing Replacement", "priority": "EMERGENCY"}
    )
    data_wo = json.loads(res_wo["content"][0]["text"])
    assert "WO-M1000" in data_wo["work_order_id"]
    assert data_wo["priority"] == "EMERGENCY"


def test_alert_mcp_server():
    alert_server = AlertMCPServer()

    # Dispatch alert
    res_disp = alert_server.call_tool(
        "dispatch_alert",
        {"machine_id": "M1000", "severity": "CRITICAL", "message": "High vibration", "trigger_sensor": "vibration"}
    )
    data_disp = json.loads(res_disp["content"][0]["text"])
    alert_id = data_disp["alert"]["alert_id"]
    assert data_disp["status"] == "DISPATCHED"

    # Get active alerts
    res_active = alert_server.call_tool("get_active_alerts", {})
    data_active = json.loads(res_active["content"][0]["text"])
    assert len(data_active) == 1

    # Acknowledge alert
    res_ack = alert_server.call_tool("acknowledge_alert", {"alert_id": alert_id})
    data_ack = json.loads(res_ack["content"][0]["text"])
    assert data_ack["status"] == "ACKNOWLEDGED"


def test_unified_mcp_client():
    client = MCPClient(auto_mount_default_servers=True)

    tools = client.list_all_tools()
    tool_names = [t["name"] for t in tools]

    assert "get_latest_telemetry" in tool_names
    assert "check_spare_parts_inventory" in tool_names
    assert "dispatch_alert" in tool_names
    assert "search_manuals" in tool_names

    # Test cross-server routing
    res = client.call_tool("check_spare_parts_inventory", {"part_no": "MOBILUX-EP2"})
    data = json.loads(res["content"][0]["text"])
    assert data["available"] is True
