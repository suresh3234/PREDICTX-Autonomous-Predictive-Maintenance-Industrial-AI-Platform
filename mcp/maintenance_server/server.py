import uuid
from datetime import datetime
from typing import Any, Optional
from mcp.base import MCPServerBase


class MaintenanceMCPServer(MCPServerBase):
    """
    MCP Server for Maintenance Planning, Work Orders, and Spare Parts Inventory.
    """

    # Simulated warehouse inventory database
    INVENTORY = {
        "SKF-6205-2RSH": {"desc": "Deep Groove Ball Bearing", "stock": 14, "location": "Bin A-12", "unit_cost": "$32.50"},
        "MOBILUX-EP2": {"desc": "Lithium Complex Industrial Grease", "stock": 25, "location": "Aisle 4 Shelf 2", "unit_cost": "$12.00"},
        "COOLANT-SYN-50": {"desc": "Synthetic Glycol Coolant (5L)", "stock": 8, "location": "Chemical Storage C-1", "unit_cost": "$45.00"},
        "FLT-RAD-04": {"desc": "Radiator Intake Air Filter", "stock": 20, "location": "Bin F-03", "unit_cost": "$18.00"},
        "VITON-ORING-SET": {"desc": "High-Pressure Viton O-Ring Set", "stock": 12, "location": "Bin O-09", "unit_cost": "$24.00"},
        "HYD-OIL-ISO46": {"desc": "Anti-Wear Hydraulic Fluid (10L)", "stock": 15, "location": "Bulk Drum Zone", "unit_cost": "$60.00"},
    }

    def __init__(self):
        super().__init__(name="predictx-maintenance-server", version="1.0.0")
        self.work_orders: list[dict[str, Any]] = []
        self._register_maintenance_tools()

    def _register_maintenance_tools(self):
        @self.tool(
            name="check_spare_parts_inventory",
            description="Queries the warehouse stock availability and location for an industrial replacement part."
        )
        def check_spare_parts_inventory(part_no: str) -> dict[str, Any]:
            clean_part = part_no.strip().upper()
            if clean_part in self.INVENTORY:
                info = self.INVENTORY[clean_part]
                return {
                    "part_no": clean_part,
                    "description": info["desc"],
                    "in_stock": info["stock"],
                    "warehouse_location": info["location"],
                    "available": info["stock"] > 0,
                }
            return {
                "part_no": part_no,
                "error": f"Part number '{part_no}' not found in catalog.",
                "available": False,
            }

        @self.tool(
            name="create_work_order",
            description="Generates an official maintenance work order with assigned machine, priority, and steps."
        )
        def create_work_order(
            machine_id: str,
            title: str,
            priority: str = "HIGH",
            estimated_hours: float = 2.0,
        ) -> dict[str, Any]:
            wo_id = f"WO-{machine_id}-{uuid.uuid4().hex[:6].upper()}"
            wo = {
                "work_order_id": wo_id,
                "machine_id": machine_id,
                "title": title,
                "priority": priority,
                "estimated_hours": estimated_hours,
                "status": "OPEN_SCHEDULED",
                "created_at": datetime.utcnow().isoformat() + "Z",
            }
            self.work_orders.append(wo)
            return wo
