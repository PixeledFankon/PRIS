
import os
import csv
import streamlit as st
from logic import get_hero_stats

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
HEROES_CSV = os.path.join(BASE_PATH, "..", "data", "raw", "HeroesList.csv")
MODEL_JSON = os.path.join(BASE_PATH, "..", "Model", "model.json")


def load_hero_names() -> list[str]:
    heroes = []
    with open(HEROES_CSV, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            name = (row.get("Name") or "").strip()
            if name:
                heroes.append(name)
    return heroes


def fmt_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


st.set_page_config(page_title="PRIS Heroes", page_icon="🧠", layout="centered")
st.title("PRIS: Герои и статистика")

if not os.path.exists(HEROES_CSV):
    st.error(f"Не найден {HEROES_CSV}")
    st.stop()

if not os.path.exists(MODEL_JSON):
    st.warning(
        "Модель не найдена. Сначала обучи:\n\n"
        "```bash\npython src/Training.py\n```"
    )
    st.stop()

heroes = load_hero_names()
selected = st.selectbox("Выбери героя", heroes)

stats = get_hero_stats(selected)
if stats is None:
    st.error("Нет данных по герою в model.json. Переобучи Training.py.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("WinRate Team vs Team", fmt_percent(stats["winrate_team_vs_team"]))
c2.metric("WinRate Duel", fmt_percent(stats["winrate_duel"]))
c3.metric("Avg Boss Damage", f"{stats['avg_boss_damage']}")

st.divider()

a1, a2, a3 = st.columns(3)
with a1:
    st.subheader("Лучшие союзники")
    for i, h in enumerate(stats["best_allies"], start=1):
        st.write(f"{i}. {h}")

with a2:
    st.subheader("Против кого хорош")
    for i, h in enumerate(stats["best_against"], start=1):
        st.write(f"{i}. {h}")

with a3:
    st.subheader("Против кого плох")
    for i, h in enumerate(stats["worst_against"], start=1):
        st.write(f"{i}. {h}")