
from dataclasses import dataclass

@dataclass
class ClassHero:
    Name: str
    Faction: str        # blue, red, green, purple
    Class: str          # warrior, mage, marksman, defender
    AttackType: str     # melee, ranged, artillery

    def __str__(self):
        return f"{self.Name} ({self.Faction}, {self.Class}, {self.AttackType})"