
from dataclasses import dataclass

@dataclass
class ClassHero:
    Name: str
    Faction: str        # blue, red, green
    Role: str           # warrior, mage, marksman
    AttackType: str     # melee, ranged, artillery

    def __str__(self):
        return f"{self.Name} ({self.Faction}, {self.Role}, {self.AttackType})"