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

@app.post("/api/telemetry")
def receive_telemetry(data: TelemetryPayload):
    """Endpoint dla gniazdek - wysyłają tu moc co sekundę"""
    if data.name not in db_devices:
        db_devices[data.name] = {
            "name": data.name,
            "nominal_power": data.nominal_power,
            "current_consumption": data.current_consumption,
            "is_running": True,
            "status": "WORKING",
            "standby_chance": 0.05  # Domyślna szansa, jeśli nie została ustawiona
        }
    
    device = db_devices[data.name]
    
    # Jeśli użytkownik wyłączył gniazdko z poziomu CLI, informujemy symulator
    if not device["is_running"]:
        return {"action": "STOP", "message": "Gniazdko odcięte z poziomu CLI."}

    # --- OCHRONA IMPULSU STARTOWEGO (WARIANT B) ---
    # Jeśli urządzenie ma pracować, ale symulator przysłał 0.0W (start lub błąd), 
    # ignorujemy to zero, aby automat standby nie wyłączył urządzenia przed startem.
    if device["status"] == "WORKING" and data.current_consumption <= 0.1:
        # Pozostawiamy poprzednią wartość w bazie, nie nadpisujemy zerem
        pass
    else:
        # W każdym innym przypadku aktualizujemy zużycie w bazie
        device["current_consumption"] = data.current_consumption

    # --- LOGIKA AUTOMATU STANDBY ---
    standby_threshold = data.nominal_power * 0.04  # Próg 4%

    # 1. Wykrycie wpadnięcia w tryb standby
    if data.current_consumption > 0.1 and data.current_consumption <= standby_threshold:
        device["is_running"] = False
        device["current_consumption"] = 0.0
        device["status"] = "DISCONNECTED_STANDBY"
        print(f"[AUTOMAT] Wykryto tryb standby dla {data.name}. Odcinam!")
        return {"action": "STOP", "message": "Automatyczne odcięcie - tryb standby."}
    
    # 2. Automatyczne wybudzenie ze standby
    if device["status"] == "DISCONNECTED_STANDBY" and data.current_consumption > standby_threshold:
        device["is_running"] = True
        device["status"] = "WORKING"
        print(f"[AUTOMAT] Urządzenie {data.name} wybudziło się automatycznie!")

    # 3. Potwierdzenie pracy + przekazanie parametrów do symulatora
    device["status"] = "WORKING"
    return {
        "action": "CONTINUE", 
        "message": "Zasilanie aktywne.",
        "standby_chance": device.get("standby_chance", 0.05)
    }

@app.get("/api/dashboard")
def get_dashboard():
    total_power = sum(d["current_consumption"] for d in db_devices.values())
    return {
        "total_house_consumption_W": round(total_power, 2),
        "devices": list(db_devices.values())
    }

@app.post("/api/device/add")
def add_new_device(payload: DeviceAddPayload):
    if payload.name in db_devices:
        raise HTTPException(status_code=400, detail="Urządzenie o tej nazwie już istnieje!")
    
    db_devices[payload.name] = {
        "name": payload.name,
        "nominal_power": payload.nominal_power,
        "current_consumption": 0.0,
        "is_running": payload.is_active,
        # Dodatkowe parametry dla symulatora przekażemy w dashboardzie
        "standby_chance": payload.standby_chance, 
        "status": "WORKING" if payload.is_active else "MANUALLY_OFF"
    }
    print(f"[SERWER] Zarejestrowano nowe gniazdko: {payload.name}")
    return {"message": f"Dodano urządzenie {payload.name}"}

@app.put("/api/device/{name}/state")
def change_device_state(name: str, payload: StateUpdatePayload):
    if name not in db_devices:
        raise HTTPException(status_code=404, detail="Urządzenie nie istnieje")
    
    db_devices[name]["is_running"] = payload.is_running
    if not payload.is_running:
        db_devices[name]["current_consumption"] = 0.0
        db_devices[name]["status"] = "MANUALLY_OFF"
    else:
        db_devices[name]["status"] = "WORKING"
        # Dajemy mały impuls startowy, żeby automat od razu nie odciął zasilania
        db_devices[name]["current_consumption"] = db_devices[name]["nominal_power"]
    
    return {"message": f"Zmieniono stan gniazdka {name} na {payload.is_running}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)