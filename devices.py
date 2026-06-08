import random

class Device:
    def __init__(self, name: str, nominal_power: float, is_active: bool, standby_chance: float):
        self.name = name
        self.nominal_power = nominal_power
        self.is_active = is_active  # Informacja czy gniazdko przepuszcza prąd
        self.standby_chance = standby_chance
        self.current_consumption = 0.0

    def generate_consumption(self) -> float:
        """Symuluje aktualne zużycie energii w zależności od stanu urządzenia"""
        if not self.is_active:
            self.current_consumption = 0.0
            return self.current_consumption

        # Losowanie: czy urządzenie wpada w stan czuwania
        if random.random() < self.standby_chance:
            # Stan czuwania (ok. 2% mocy znamionowej + mały szum)
            self.current_consumption = round(self.nominal_power * 0.02 + random.uniform(-0.1, 0.1), 2)
        else:
            # Normalna praca (+/- 5% odchyłu od mocy nominalnej)
            self.current_consumption = round(
                self.nominal_power + random.uniform(-self.nominal_power * 0.03, self.nominal_power * 0.05), 2
            )
        
        # Zabezpieczenie przed ujemnymi wartościami przy bardzo małych mocach
        if self.current_consumption < 0:
            self.current_consumption = 0.0
            
        return self.current_consumption