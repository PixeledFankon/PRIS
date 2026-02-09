
from dataclasses import dataclass
from typing import List

@dataclass
class HeroClass:
    Name: str
    Tier: str
    Tags: List[str]

    def __str__(self) -> str:
        return f"{self.Name} (Tier {self.Tier}, {', '.join(self.Tags)})"