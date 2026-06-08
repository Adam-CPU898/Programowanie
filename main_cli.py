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

