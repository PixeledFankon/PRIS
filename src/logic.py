
import json
from pathlib import Path

RULES_PATH = Path(__file__).parent.parent / "data" / "raw" / "rules.json"

class MetaLogic:
    def __init__(self):
        with open(RULES_PATH, "r", encoding="utf-8") as f:
            self.rules = json.load(f)

    def GetTier(self, heroClass):
        return self.rules["tiers"].get(heroClass, "Unknown")

    def IsCounter(self, attacker, defender):
        return defender in self.rules["counters"].get(attacker, [])

    def IsStrongPick(self, heroClass):
        tier = self.GetTier(heroClass)
        return tier in self.rules["meta_thresholds"]["strong_pick"]

def EvaluateMeta(entity, metaLogic):
    hero = entity["hero_class"]
    enemies = entity.get("enemy_classes", [])

    tier = metaLogic.GetTier(hero)

    countered = any(
        metaLogic.IsCounter(enemy, hero)
        for enemy in enemies
    )

    strong_pick = metaLogic.IsStrongPick(hero)

    return {
        "hero": hero,
        "tier": tier,
        "is_countered": countered,
        "is_strong_pick": strong_pick
    }
