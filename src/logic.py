
import json
import os
from typing import Any, Dict, Optional, List

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_PATH, "..", "Model", "model.json")
HEROES_PATH = os.path.join(BASE_PATH, "..", "data", "raw", "HeroesList.csv")


def load_model() -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(MODEL_PATH):
        return {}

    with open(MODEL_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_hero_stats(hero_name: str) -> Optional[Dict[str, Any]]:
    model = load_model()
    return model.get(hero_name)