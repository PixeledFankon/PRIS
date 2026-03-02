
import csv
import json
import os
from collections import defaultdict
from typing import Dict, List, DefaultDict, Any


BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_PATH, "..", "data", "raw")
MODEL_PATH = os.path.join(BASE_PATH, "..", "Model", "model.json")


def load_hero_names() -> List[str]:
    heroes: List[str] = []
    file_path = os.path.join(DATA_PATH, "HeroesList.csv")

    with open(file_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            name = (row.get("Name") or "").strip()
            if name:
                heroes.append(name)

    return heroes


def parse_team(team_str: str) -> List[str]:
    return [h.strip() for h in team_str.split("|") if h.strip()]


def train() -> None:
    heroes = load_hero_names()

    # Статы по герою
    stats: Dict[str, Dict[str, Any]] = {}

    for hero in heroes:
        stats[hero] = {
            "team_vs_team": {"wins": 0, "games": 0},
            "team_vs_boss": {"total_damage": 0, "games": 0},
            "duel": {"wins": 0, "games": 0},
            "allies": defaultdict(int),    # type: DefaultDict[str, int]
            "vs_win": defaultdict(int),    # type: DefaultDict[str, int]
            "vs_lose": defaultdict(int)    # type: DefaultDict[str, int]
        }

    # --- Team vs Team ---
    team_vs_team_path = os.path.join(DATA_PATH, "TeamVersusTeam.csv")
    with open(team_vs_team_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            team1 = parse_team(row["Team1"])
            team2 = parse_team(row["Team2"])
            winner = row["Result"]

            for hero in team1:
                stats[hero]["team_vs_team"]["games"] += 1
                if winner == "Team1":
                    stats[hero]["team_vs_team"]["wins"] += 1

            for hero in team2:
                stats[hero]["team_vs_team"]["games"] += 1
                if winner == "Team2":
                    stats[hero]["team_vs_team"]["wins"] += 1

            # союзники (частота совместных игр)
            for team in (team1, team2):
                for hero in team:
                    for ally in team:
                        if ally != hero:
                            stats[hero]["allies"][ally] += 1

            # противники (победы/поражения)
            for hero in team1:
                for enemy in team2:
                    if winner == "Team1":
                        stats[hero]["vs_win"][enemy] += 1
                    else:
                        stats[hero]["vs_lose"][enemy] += 1

            for hero in team2:
                for enemy in team1:
                    if winner == "Team2":
                        stats[hero]["vs_win"][enemy] += 1
                    else:
                        stats[hero]["vs_lose"][enemy] += 1

    # --- Team vs Boss ---
    team_vs_boss_path = os.path.join(DATA_PATH, "TeamVersusBoss.csv")
    with open(team_vs_boss_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            team = parse_team(row["Team"])
            dmg = int(row["Result"])

            for hero in team:
                stats[hero]["team_vs_boss"]["games"] += 1
                stats[hero]["team_vs_boss"]["total_damage"] += dmg

    # --- Duel 1v1 ---
    duel_path = os.path.join(DATA_PATH, "HeroVersusHero.csv")
    with open(duel_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            h1 = row["Hero1"]
            h2 = row["Hero2"]
            winner = row["Result"]

            stats[h1]["duel"]["games"] += 1
            stats[h2]["duel"]["games"] += 1

            if winner == h1:
                stats[h1]["duel"]["wins"] += 1
                stats[h1]["vs_win"][h2] += 1
                stats[h2]["vs_lose"][h1] += 1
            else:
                stats[h2]["duel"]["wins"] += 1
                stats[h2]["vs_win"][h1] += 1
                stats[h1]["vs_lose"][h2] += 1

    # --- Финальная модель ---
    model: Dict[str, Dict[str, Any]] = {}

    for hero in heroes:
        hero_data = stats[hero]

        team_games = hero_data["team_vs_team"]["games"]
        duel_games = hero_data["duel"]["games"]
        boss_games = hero_data["team_vs_boss"]["games"]

        winrate_team = round(hero_data["team_vs_team"]["wins"] / team_games, 3) if team_games else 0.0
        winrate_duel = round(hero_data["duel"]["wins"] / duel_games, 3) if duel_games else 0.0
        avg_boss_damage = round(hero_data["team_vs_boss"]["total_damage"] / boss_games, 1) if boss_games else 0.0

        allies = hero_data["allies"]
        vs_win = hero_data["vs_win"]
        vs_lose = hero_data["vs_lose"]

        model[hero] = {
            "winrate_team_vs_team": winrate_team,
            "winrate_duel": winrate_duel,
            "avg_boss_damage": avg_boss_damage,
            "best_allies": sorted(allies, key=allies.get, reverse=True)[:3],
            "best_against": sorted(vs_win, key=vs_win.get, reverse=True)[:3],
            "worst_against": sorted(vs_lose, key=vs_lose.get, reverse=True)[:3]
        }

    os.makedirs(os.path.join(BASE_PATH, "..", "Model"), exist_ok=True)
    with open(MODEL_PATH, "w", encoding="utf-8", newline="") as f:
        json.dump(model, f, indent=4, ensure_ascii=False)

    print("Model trained successfully.")


if __name__ == "__main__":
    train()