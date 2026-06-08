import time
import os
import requests
import devices

SERVER_URL = "http://127.0.0.1:8000/api/telemetry"

PREDEFINED_DEVICES = [
    ("Telewizor OLED", 150.0, True, 0.01),
    ("Ładowarka Telefonu", 65.0, True, 0.02),
    ("Czajnik Elektryczny", 2200.0, True, 0.04),
    ("Konsola do gier", 200.0, True, 0.01),
    ("Komputer Stacjonarny", 400.0, True, 0.03),
    ("Pralka", 500.0, True, 0.02),
    ("Kuchenka Mikrofalowa", 1200.0, True, 0.03),
    ("Monitor", 45.0, True, 0.04),
    ("Zmywarka", 1800.0, True, 0.01),
    ("Ekspres do kawy", 1450.0, True, 0.10)
]

# Tworzenie obiektów klasy Device z predefiniowanej listy (jako słownik)
devices_pool = {}
for name, power, active, chance in PREDEFINED_DEVICES:
    devices_pool[name] = devices.Device(name, power, active, chance)

def sync_devices_from_server():
    """Pobiera urządzenia z API i w razie potrzeby tworzy nowe obiekty w symulatorze lub aktualizuje ich stan"""
    try:
        # Odpytujemy serwer o aktualny stan wszystkich zarejestrowanych urządzeń
        res = requests.get("http://127.0.0.1:8000/api/dashboard", timeout=2)
        if res.status_code == 200:
            server_devices = res.json().get("devices", [])
            
            for s_dev in server_devices:
                name = s_dev["name"]
                
                # PROBLEM 1 NAPRAWIONY: Jeśli wykryto urządzenie z CLI/GUI, którego nie ma w symulatorze:
                if name not in devices_pool:
                    chance = s_dev.get("standby_chance", 0.05)
                    # Sprawdzamy czy użytkownik chciał, by było od startu włączone
                    is_active_init = s_dev.get("is_running", True)
                    
                    # Tworzymy obiekt klasy Device w locie
                    devices_pool[name] = devices.Device(name, s_dev["nominal_power"], is_active_init, chance)
                    print(f" -> [REJESTRACJA] Dodano nowe dynamiczne urządzenie z API: {name}")
                
                # Synchronizacja stanów: jeśli użytkownik kliknął OFF w CLI, gasimy symulator
                else:
                    if s_dev.get("status") == "MANUALLY_OFF":
                        devices_pool[name].is_active = False
    except Exception:
        pass

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    print("Uruchomiono obiektowy symulator gniazdek IoT [Wysyłanie danych co 1s]...")

    while True:
        # Wywołujemy synchronizację na początku każdej sekundy
        sync_devices_from_server()
        
        clear_screen()
        print(f"\n--- [DEBUG Z ZAPYTANIA HARDWARE] Godzina: {time.strftime('%X')} ---")
        
        # Iterujemy po słowniku (używamy list(), aby uniknąć błędów modyfikacji słownika w locie)
        for name, dev in list(devices_pool.items()):
            # Generujemy zużycie (zwróci 0W jeśli dev.is_active == False)
            current_w = dev.generate_consumption()

            payload = {
                "name": dev.name,
                "nominal_power": dev.nominal_power,
                "current_consumption": current_w
            }

            try:
                res = requests.post(SERVER_URL, json=payload)
                if res.status_code == 200:
                    data_back = res.json()
                    command = data_back.get("action")
                    msg = data_back.get("message", "")
                    
                    if command == "STOP":
                        dev.is_active = False
                    elif command == "CONTINUE":
                        # Logika komunikatów wybudzania
                        if not dev.is_active:
                            if "ręcznie" in msg or "CLI" in msg:
                                print(f" -> [RĘCZNE URUCHOMIENIE] {dev.name} zostało włączone przez użytkownika!")
                            else:
                                print(f" -> [AUTOMATYCZNE WYBUDZENIE] {dev.name} samoczynnie wznowił pracę ze standby!")
                        dev.is_active = True
                        
                    status_fizyczny = 'WŁĄCZONE' if dev.is_active else 'WYŁĄCZONE (STANDBY/OFF)'
                    print(f"Gniazdko {dev.name.ljust(22)} | Pobór: {dev.current_consumption} W | Status fizyczny: {status_fizyczny}")
                    
            except requests.exceptions.ConnectionError:
                print("[BŁĄD] Brak połączenia z serwerem FastAPI, ponowienie za 5 sekund...")
                time.sleep(5)
                break
        print(f"-" * 54)
        time.sleep(1)