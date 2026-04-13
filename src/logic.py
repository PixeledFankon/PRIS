
import json
import os
from functools import lru_cache
from typing import Dict, List, Optional

import joblib


BASE_PATH = os.path.dirname(os.path.abspath(__file__))
MODELS_PATH = os.path.join(BASE_PATH, "..", "models")

DUEL_MODEL_PATH = os.path.join(MODELS_PATH, "duel_model.pkl")
TEAM_MODEL_PATH = os.path.join(MODELS_PATH, "team_model.pkl")
BOSS_MODEL_PATH = os.path.join(MODELS_PATH, "boss_model.pkl")
METADATA_PATH = os.path.join(MODELS_PATH, "metadata.json")
WAVES_MODEL_PATH = os.path.join(MODELS_PATH, "waves_model.pkl")


@lru_cache(maxsize=1)
def LoadMetadata() -> Dict[str, List[str]]:
    if not os.path.exists(METADATA_PATH):
        raise FileNotFoundError("Сначала надо запустить тренировку.")

    with open(METADATA_PATH, encoding="utf-8") as file:
        return json.load(file)


@lru_cache(maxsize=1)
def LoadDuelModel():
    if not os.path.exists(DUEL_MODEL_PATH):
        raise FileNotFoundError("Не найден models/duel_model.pkl. Сначала запусти Training.py")
    return joblib.load(DUEL_MODEL_PATH)


@lru_cache(maxsize=1)
def LoadTeamModel():
    if not os.path.exists(TEAM_MODEL_PATH):
        raise FileNotFoundError("Не найден models/team_model.pkl. Сначала запусти Training.py")
    return joblib.load(TEAM_MODEL_PATH)


@lru_cache(maxsize=1)
def LoadBossModel():
    if not os.path.exists(BOSS_MODEL_PATH):
        raise FileNotFoundError("Не найден models/boss_model.pkl. Сначала запусти Training.py")
    return joblib.load(BOSS_MODEL_PATH)


@lru_cache(maxsize=1)
def LoadWavesModel():
    if not os.path.exists(WAVES_MODEL_PATH):
        raise FileNotFoundError("Не найден models/waves_model.pkl. Сначала запусти Training.py")
    return joblib.load(WAVES_MODEL_PATH)


def GetHeroes() -> List[str]:
    metadata = LoadMetadata()
    return metadata.get("heroes", [])


def GetBosses() -> List[str]:
    metadata = LoadMetadata()
    return metadata.get("bosses", [])


def MakeHeroIndex() -> Dict[str, int]:
    heroes = GetHeroes()
    return {hero: index for index, hero in enumerate(heroes)}


def MakeBossIndex() -> Dict[str, int]:
    bosses = GetBosses()
    return {boss: index for index, boss in enumerate(bosses)}


def EncodeDuel(hero1: str, hero2: str) -> List[int]:
    heroIndex = MakeHeroIndex()
    heroCount = len(heroIndex)

    features = [0] * (heroCount * 2)
    features[heroIndex[hero1]] = 1
    features[heroCount + heroIndex[hero2]] = 1

    return features


def EncodeTeamBattle(team1: List[str], team2: List[str]) -> List[int]:
    heroIndex = MakeHeroIndex()
    features = [0] * len(heroIndex)

    for hero in team1:
        features[heroIndex[hero]] += 1

    for hero in team2:
        features[heroIndex[hero]] -= 1

    return features


def EncodeBossBattle(team: List[str], boss: Optional[str]) -> List[int]:
    heroIndex = MakeHeroIndex()
    bossIndex = MakeBossIndex()

    features = [0] * (len(heroIndex) + len(bossIndex))

    for hero in team:
        features[heroIndex[hero]] += 1

    if boss is not None and boss in bossIndex:
        features[len(heroIndex) + bossIndex[boss]] = 1

    return features


def EncodeWavesTeam(team: List[str]) -> List[int]:
    heroIndex = MakeHeroIndex()
    features = [0] * len(heroIndex)

    for hero in team:
        features[heroIndex[hero]] += 1

    return features


def PredictDuel(hero1: str, hero2: str) -> float:
    if hero1 == hero2:
        raise ValueError("Для дуэли нужны два разных героя")

    model = LoadDuelModel()
    features = EncodeDuel(hero1, hero2)
    probability = model.predict_proba([features])[0][1]
    return float(probability)


def PredictTeamBattle(team1: List[str], team2: List[str]) -> float:
    if len(team1) != 3 or len(team2) != 3:
        raise ValueError("Для командного боя нужно выбрать ровно 3 героя в каждую команду")

    if len(set(team1)) != len(team1):
        raise ValueError("В первой команде есть повторяющиеся герои")

    if len(set(team2)) != len(team2):
        raise ValueError("Во второй команде есть повторяющиеся герои")

    model = LoadTeamModel()
    features = EncodeTeamBattle(team1, team2)
    probability = model.predict_proba([features])[0][1]
    return float(probability)


def PredictBossBattle(team: List[str], boss: Optional[str]) -> float:
    if len(team) != 3:
        raise ValueError("Для боя с боссом нужно выбрать ровно 3 героев")

    if len(set(team)) != len(team):
        raise ValueError("В команде есть повторяющиеся герои")

    model = LoadBossModel()
    features = EncodeBossBattle(team, boss)
    predictedDamage = model.predict([features])[0]
    return max(0.0, float(predictedDamage))


def PredictWaves(team: List[str]) -> float:
    if len(team) != 3:
        raise ValueError("Для режима волн нужно выбрать ровно 3 героев")

    if len(set(team)) != len(team):
        raise ValueError("В команде есть повторяющиеся герои")

    model = LoadWavesModel()
    features = EncodeWavesTeam(team)
    predictedWaves = model.predict([features])[0]

    return max(0.0, min(12.0, float(predictedWaves)))