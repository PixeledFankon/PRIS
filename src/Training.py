
import csv
import json
import os
from typing import Dict, List, Optional

import joblib
from sklearn.linear_model import LogisticRegression, Ridge


BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_PATH, "..", "data", "raw")
MODELS_PATH = os.path.join(BASE_PATH, "..", "models")

HEROES_LIST_PATH = os.path.join(DATA_PATH, "HeroesList.csv")
DUELS_PATH = os.path.join(DATA_PATH, "HeroVersusHero.csv")
TEAM_BATTLE_PATH = os.path.join(DATA_PATH, "TeamVersusTeam.csv")
BOSS_BATTLE_PATH = os.path.join(DATA_PATH, "TeamVersusBoss.csv")


def ParseTeam(teamStr: str) -> List[str]:
    return [hero.strip() for hero in teamStr.split("|") if hero.strip()]


def LoadHeroNames() -> List[str]:
    heroes: List[str] = []

    with open(HEROES_LIST_PATH, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            name = (row.get("Name") or "").strip()
            if name:
                heroes.append(name)

    return heroes


def LoadBossNames() -> List[str]:
    if not os.path.exists(BOSS_BATTLE_PATH):
        return []

    bossNames = set()

    with open(BOSS_BATTLE_PATH, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        fieldNames = reader.fieldnames or []

        if "Boss" not in fieldNames:
            return ["Boss"]

        for row in reader:
            bossName = (row.get("Boss") or "").strip()
            if bossName:
                bossNames.add(bossName)

    return sorted(bossNames) if bossNames else ["Boss"]


def MakeHeroIndex(heroes: List[str]) -> Dict[str, int]:
    return {hero: index for index, hero in enumerate(heroes)}


def MakeBossIndex(bosses: List[str]) -> Dict[str, int]:
    return {boss: index for index, boss in enumerate(bosses)}


def EncodeDuel(hero1: str, hero2: str, heroIndex: Dict[str, int]) -> List[int]:
    heroCount = len(heroIndex)
    features = [0] * (heroCount * 2)

    features[heroIndex[hero1]] = 1
    features[heroCount + heroIndex[hero2]] = 1

    return features


def EncodeTeamBattle(team1: List[str], team2: List[str], heroIndex: Dict[str, int]) -> List[int]:
    features = [0] * len(heroIndex)

    for hero in team1:
        features[heroIndex[hero]] += 1

    for hero in team2:
        features[heroIndex[hero]] -= 1

    return features


def EncodeBossBattle(
    team: List[str],
    boss: Optional[str],
    heroIndex: Dict[str, int],
    bossIndex: Dict[str, int]
) -> List[int]:
    features = [0] * (len(heroIndex) + len(bossIndex))

    for hero in team:
        features[heroIndex[hero]] += 1

    if boss is not None and boss in bossIndex:
        features[len(heroIndex) + bossIndex[boss]] = 1

    return features


def TrainDuelModel(heroes: List[str]) -> LogisticRegression:
    heroIndex = MakeHeroIndex(heroes)
    xTrain: List[List[int]] = []
    yTrain: List[int] = []

    with open(DUELS_PATH, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            hero1 = (row.get("Hero1") or "").strip()
            hero2 = (row.get("Hero2") or "").strip()
            result = (row.get("Result") or "").strip()

            if hero1 not in heroIndex or hero2 not in heroIndex:
                continue

            # label = 1, если победил Hero1
            label = 1 if result == hero1 else 0

            xTrain.append(EncodeDuel(hero1, hero2, heroIndex))
            yTrain.append(label)

            # Добавляем зеркальный пример для устойчивости
            reverseLabel = 1 if result == hero2 else 0
            xTrain.append(EncodeDuel(hero2, hero1, heroIndex))
            yTrain.append(reverseLabel)

    model = LogisticRegression(max_iter=2000, class_weight="balanced")
    model.fit(xTrain, yTrain)
    return model


def TrainTeamBattleModel(heroes: List[str]) -> LogisticRegression:
    heroIndex = MakeHeroIndex(heroes)
    xTrain: List[List[int]] = []
    yTrain: List[int] = []

    with open(TEAM_BATTLE_PATH, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            team1 = ParseTeam(row["Team1"])
            team2 = ParseTeam(row["Team2"])
            result = (row.get("Result") or "").strip()

            if any(hero not in heroIndex for hero in team1 + team2):
                continue

            label = 1 if result == "Team1" else 0

            xTrain.append(EncodeTeamBattle(team1, team2, heroIndex))
            yTrain.append(label)

            # Зеркальный пример
            reverseLabel = 1 if result == "Team2" else 0
            xTrain.append(EncodeTeamBattle(team2, team1, heroIndex))
            yTrain.append(reverseLabel)

    model = LogisticRegression(max_iter=2000, class_weight="balanced")
    model.fit(xTrain, yTrain)
    return model


def TrainBossModel(heroes: List[str], bosses: List[str]) -> Ridge:
    heroIndex = MakeHeroIndex(heroes)
    bossIndex = MakeBossIndex(bosses)

    xTrain: List[List[int]] = []
    yTrain: List[float] = []

    with open(BOSS_BATTLE_PATH, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        fieldNames = reader.fieldnames or []
        hasBossColumn = "Boss" in fieldNames

        for row in reader:
            team = ParseTeam(row["Team"])

            if any(hero not in heroIndex for hero in team):
                continue

            bossName = (row.get("Boss") or "").strip() if hasBossColumn else "Boss"

            try:
                damage = float(row["Result"])
            except (ValueError, TypeError, KeyError):
                continue

            xTrain.append(EncodeBossBattle(team, bossName, heroIndex, bossIndex))
            yTrain.append(damage)

    model = Ridge(alpha=1.0)
    model.fit(xTrain, yTrain)
    return model


def SaveMetadata(heroes: List[str], bosses: List[str]) -> None:
    metadata = {
        "heroes": heroes,
        "bosses": bosses
    }

    metadataPath = os.path.join(MODELS_PATH, "metadata.json")
    with open(metadataPath, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4, ensure_ascii=False)


def TrainAll() -> None:
    os.makedirs(MODELS_PATH, exist_ok=True)

    heroes = LoadHeroNames()
    bosses = LoadBossNames()

    if not heroes:
        raise ValueError("Не удалось загрузить героев из HeroesList.csv")

    print("Обучение duel_model...")
    duelModel = TrainDuelModel(heroes)
    joblib.dump(duelModel, os.path.join(MODELS_PATH, "duel_model.pkl"))

    print("Обучение team_model...")
    teamModel = TrainTeamBattleModel(heroes)
    joblib.dump(teamModel, os.path.join(MODELS_PATH, "team_model.pkl"))

    print("Обучение boss_model...")
    bossModel = TrainBossModel(heroes, bosses)
    joblib.dump(bossModel, os.path.join(MODELS_PATH, "boss_model.pkl"))

    SaveMetadata(heroes, bosses)

    print("Готово. Модели сохранены в папку models/")


if __name__ == "__main__":
    TrainAll()