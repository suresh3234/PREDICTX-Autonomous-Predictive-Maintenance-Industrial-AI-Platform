from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Machine
from app.db.session import SessionLocal
from mcp.base import MCPServerBase


class DatabaseMCPServer(MCPServerBase):
    """
    MCP Server for Relational Equipment and Telemetry Database Operations.
    """

    def __init__(self, session_factory=SessionLocal):
        super().__init__(name="predictx-database-server", version="1.0.0")
        self.session_factory = session_factory
        self._register_database_tools()

    def _register_database_tools(self):
        @self.tool(
            name="list_machines",
            description="Lists all industrial machines registered in the factory database."
        )
        def list_machines() -> list[dict[str, Any]]:
            db: Session = self.session_factory()
            try:
                machines = db.scalars(select(Machine)).all()
                return [
                    {
                        "id": str(m.id),
                        "machine_code": m.machine_code,
                        "machine_type": m.machine_type,
                        "created_at": m.created_at.isoformat() if m.created_at else None,
                    }
                    for m in machines
                ]
            finally:
                db.close()

        @self.tool(
            name="get_machine_details",
            description="Retrieves metadata for a specific machine code (e.g. M1000)."
        )
        def get_machine_details(machine_code: str) -> dict[str, Any]:
            db: Session = self.session_factory()
            try:
                machine = db.scalar(select(Machine).where(Machine.machine_code == machine_code))
                if not machine:
                    return {"error": f"Machine with code '{machine_code}' not found."}
                return {
                    "id": str(machine.id),
                    "machine_code": machine.machine_code,
                    "machine_type": machine.machine_type,
                    "created_at": machine.created_at.isoformat() if machine.created_at else None,
                }
            finally:
                db.close()
