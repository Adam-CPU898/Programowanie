import os
import requests
import time
import threading
from InquirerPy import inquirer
from InquirerPy.base import Choice
from InquirerPy.validator import NumberValidator
from zapytania_hardware import PREDEFINED_DEVICES

SERVER_URL = "http://127.0.0.1:8000/api"

# Zmienne globalne współdzielone między wątkiem a głównym menu
global_data = {"total_house_consumption_W": 0.0, "devices": [], "last_update": 0}
data_lock = threading.Lock()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def fetch_data_worker():
    """Wątek działający w tle, który co 3 sekundy pobiera świeże dane z serwera"""
    while True:
        try:
            res = requests.get(f"{SERVER_URL}/dashboard", timeout=2)
            if res.status_code == 200:
                json_data = res.json()
                with data_lock:
                    global_data["total_house_consumption_W"] = json_data.get("total_house_consumption_W", 0.0)
                    global_data["devices"] = json_data.get("devices", [])
                    global_data["last_update"] = time.time()
        except Exception:
            # W razie braku połączenia z API, wątek bezpiecznie czeka dalej
            pass
        time.sleep(3)

def print_header(current_power):
    """Generuje ładny, stały nagłówek panelu"""
    print("#" * 55)
    print("      PANEL CLI - ZARZĄDZANIE INTELIGENTNYM DOMEM                  ")
    print("#" * 55)

def main():
    # Uruchomienie wątku pobierającego dane w tle
    threading.Thread(target=fetch_data_worker, daemon=True).start()
    
    # Poczekaj chwilę na pierwsze dane z wątku
    time.sleep(0.5)

    while True:
        clear_screen()
        
        with data_lock:
            current_power = global_data["total_house_consumption_W"]
            cached_devices = global_data["devices"]

        print_header(current_power)

        menu = [
            Choice(value="toggle", name="1. Przełącz stan pojedynczego urządzenia (ON/OFF)"),
            Choice(value="show_all", name="2. Wyświetl stan wszystkich gniazdek (NA ŻYWO)"),
            Choice(value="add_device", name="3. Dodaj nowe urządzenie do systemu +"),
            Choice(value="exit", name="4. Wyjście")
        ]

        try:
            wybor = inquirer.select(
                message="Wybierz opcję z menu:",
                choices=menu,
                pointer="-->"
            ).execute()
        except KeyboardInterrupt:
            print("\nZamykanie panelu CLI...")
            break

        if wybor == "exit":
            break

        if wybor == "toggle":
            if not cached_devices:
                input("\nBrak urządzeń w bazie danych lub serwer OFF. [Enter]")
                continue
                
            options_devices = []
            for d in cached_devices:
                status_icon = "🟢 WORKING" if d['is_running'] else f"🔴 OFF ({d['status']})"
                options_devices.append(
                    Choice(value=d, name=f"{d['name'].ljust(22)} | {str(d['current_consumption']).rjust(6)}W | {status_icon}")
                )
            options_devices.append(Choice(value="back", name="[ Powrót ]"))
            
            # PROBLEM 2 NAPRAWIONY: Ctrl+C podczas wyboru urządzenia wraca do menu głównego
            try:
                selected_device = inquirer.select(
                    message="Wybierz gniazdko do przełączenia (Ctrl+C przerywa):",
                    choices=options_devices,
                    pointer="👉"
                ).execute()
            except KeyboardInterrupt:
                continue
            
            if selected_device != "back":
                    new_state = not selected_device["is_running"]
                    try:
                        res = requests.put(
                            f"{SERVER_URL}/device/{selected_device['name']}/state", 
                            json={"is_running": new_state}
                        )
                        if res.status_code == 200:
                            print(f"\n[API] Zmieniono stan dla {selected_device['name']}.")
                            
                            # --- WYMUSZENIE NATYCHMIASTOWEJ AKTUALIZACJI W CLI ---
                            print("Pobieranie aktualnych danych...")
                            time.sleep(0.5)
                            fresh_res = requests.get(f"{SERVER_URL}/dashboard", timeout=2)
                            if fresh_res.status_code == 200:
                                json_data = fresh_res.json()
                                with data_lock:
                                    global_data["total_house_consumption_W"] = json_data.get("total_house_consumption_W", 0.0)
                                    global_data["devices"] = json_data.get("devices", [])
                                    global_data["last_update"] = time.time()
                            # -----------------------------------------------------
                            
                        else:
                            print(f"\n[BŁĄD SERWERA] Nie udało się zmienić stanu.")
                        time.sleep(1)
                    except Exception:
                        print("\n[BŁĄD] Nie udało się wysłać żądania.")
                        time.sleep(1)
        elif wybor == "show_all":
            try:
                while True:
                    clear_screen()
                    with data_lock:
                        pwr = global_data["total_house_consumption_W"]
                        devs = global_data["devices"]
                    print("=" * 70)
                    print(f"  PODGLĄD STANU URZĄDZEŃ NA ŻYWO (Ctrl+C przerywa) | Suma: {pwr}W")
                    print("=" * 70)
                    if devs:
                        print(f"{'Nazwa Urządzenia'.ljust(22)} | {'Moc znam.'.rjust(10)} | {'Aktualna'.rjust(9)} | {'Status gniazdka'}")
                        print("-" * 70)
                        for d in devs:
                            status_str = "Działa (WORKING)" if d['status'] == "WORKING" else d['status']
                            print(f"{d['name'].ljust(22)} | {str(d['nominal_power']).rjust(8)} W | {str(d['current_consumption']).rjust(7)} W | {status_str}")
                    else:
                        print(" Brak danych o urządzeniach.")
                    time.sleep(1)
            except KeyboardInterrupt:
                continue
        

if __name__ == "__main__":
    main()