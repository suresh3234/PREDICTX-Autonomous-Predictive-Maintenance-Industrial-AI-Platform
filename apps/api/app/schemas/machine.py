import uuid
from datetime import datetime

from pydantic import BaseModel


class MachineBase(BaseModel):
    machine_code: str
    machine_type: str


class MachineCreate(MachineBase):
    pass


class Machine(MachineBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
