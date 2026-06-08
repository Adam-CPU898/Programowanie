Temat
3. System inteligentnych gniazd do ograniczania zużycia energii
Problem: Użytkownicy zostawiają urządzenia w trybie czuwania.
Zadanie:
•     analiza sygnatur poboru prądu (klasyfikacja urządzeń),
•     logika automatycznego odłączania zasilania,
•     API sterujące gniazdami (lokalne lub IoT).
•     Rezultat: system klasyfikacji + sterowania gniazdami.
•     Plan wdrożenia

*Smart Power Manager (SPM)*

System inteligentnego zarządzania energią, zaprojektowany w celu eliminacji strat energii powodowanych przez urządzenia pozostawione w trybie czuwania (standby).
System automatycznie klasyfikuje urządzenia na podstawie ich sygnatur poboru prądu i zarządza ich zasilaniem za pośrednictwem API.

*Kluczowe funkcjonalności:*
- Analiza sygnatur (klasyfikacja): System identyfikuje, czy urządzenie pracuje nominalnie, czy znajduje się w trybie czuwania.
- Automatyka: Inteligentna logika odcinania zasilania dla urządzeń, które przekroczyły próg standby.
- API sterujące: Centralny serwer (FastAPI) komunikujący się z gniazdkami (symulatorami) w czasie rzeczywistym.
- Interfejs CLI: Wygodna konsola do zarządzania infrastrukturą domu.
- Symulacja: Generator krzywej poboru energii pozwalający na testowanie systemu bez fizycznego sprzętu.

*Architektura systemu*
System składa się z trzech głównych komponentów:
Centralny Serwer (API): Odpowiada za logikę biznesową, przechowywanie stanu urządzeń oraz podejmowanie decyzji o odcięciu zasilania.
Symulator Gniazdek (Hardware): Wirtualne urządzenia wysyłające dane telemetryczne o poborze mocy do serwera.
CLI Panel: Interfejs użytkownika umożliwiający pełną kontrolę nad systemem.

*Instrukcja obsługi CLIInterfejs CLI*
pozwala na pełne zarządzanie Twoimi gniazdkami:
Przełącz stan (ON/OFF): Ręczne sterowanie zasilaniem wybranego urządzenia.
Podgląd na żywo: Monitorowanie całkowitego zużycia energii w domu oraz statusu każdego gniazdka.
Kreator urządzeń: Łatwe dodawanie nowych urządzeń przy użyciu gotowych szablonów lub własnych parametrów (moc nominalna, szansa na standby [emulacja]).

*Plan wdrożenia*
Etap 1: Faza analityczna - Definicja sygnatur poboru mocy dla różnych typów urządzeń (RTV, AGD, biurowe).
Etap 2: Implementacja silnika automatyki - Wdrożenie algorytmu wykrywania trybu czuwania (próg 4% mocy nominalnej).
Etap 3: Integracja API i CLI - Połączenie frontendu konsolowego z logiką serwerową.
Etap 4: Testy symulacyjne - Wykorzystanie generatora krzywej poboru prądu do weryfikacji poprawności odcinania zasilania.
Etap 5: Deployment - Uruchomienie serwera w środowisku lokalnym lub IoT.

*Szybki start*
Serwer: Uruchom server.py (FastAPI), który nasłuchuje na porcie 8000
Symulator: Uruchom skrypty symulujące pracę gniazdek (hardware_simulator.py).
Panel: Uruchom main_cli.py, aby zacząć zarządzać swoim inteligentnym domem.
TechnologiaBackend: Python, FastAPI, PydanticCLI: InquirerPy, prompt_toolkitKomunikacja: HTTP/JSON (Telemetria i API sterujące)

*Szybkie know-how*
Uruchomisz skrypty przy pomocy komendy: python3 <ścieżka_do_pliku>,
np. python3 C:\users\Adam\projekty\programowanie\server.py