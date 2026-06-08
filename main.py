import os
from InquirerPy import inquirer

def clear_screen():
    # Czyszczenie terminala w zależności od systemu operacyjnego
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    while True:
        clear_screen()
        
        print("#####################################################################")
        print("      Command Line Interface - Manage your devices!                  ")
        print("#####################################################################\n")

        # Statyczna lista (docelowo z FastAPI)
        menu = [
            "0. Wyświetl pracujące urządzenia",
            "1. Dodaj urządzenie",
            "2. Uruchom urządzenie",
            "3. Zatrzymaj urządzenie",
            "4. Usuń urządzenie",
            "5. Wyjście z programu"
        ]

        # Wywołanie menu wybieranego strzałkami
        wybor = inquirer.select(
            message="Wybierz jedną z dostępnych opcji:",
            choices=menu,
            height=len(menu)+1,
            pointer="-->",
            border=True # Opcjonalnie: dodaje subtelną ramkę wokół menu w nowszych wersjach
        ).execute()

        # LOGIKA OBSŁUGI WYBORU (match/case)
        match wybor:
            case "1. Dodaj urządzenie":
                print("\n[Uruchamianie] Funkcja dodawania urządzenia...")
                # Tutaj wywołujesz np. funkcja_dodaj_urzadzenie()
                
            case "2. Uruchom urządzenie":
                print("\n[Uruchamianie] Funkcja startu urządzenia...")
                
            case "3. Zatrzymaj urządzenie":
                print("\n[Uruchamianie] Funkcja zatrzymania urządzenia...")
                
            case "4. Usuń urządzenie":
                print("\n[Uruchamianie] Funkcja usuwania urządzenia...")
                
            case "5. Wyjście z programu":
                print("\nZamykanie panelu CLI. Do zobaczenia!")
                return False # Przerywa pętlę while True
    
        
        # Krótka pauza, żeby użytkownik zdążył przeczytać komunikat przed odświeżeniem ekranu
        input("\nNaciśnij Enter, aby kontynuować...")

if __name__ == "__main__":
    main()