from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI(title="Smart Home Central Server")
db_devices: Dict[str, dict] = {}

class TelemetryPayload(BaseModel):
    name: str
    nominal_power: float
    current_consumption: float

class StateUpdatePayload(BaseModel):
    is_running: bool

class DeviceAddPayload(BaseModel):
    name: str
    nominal_power: float
    is_active: bool
    standby_chance: float

