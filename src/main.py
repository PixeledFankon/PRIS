
import streamlit as st

from logic import (
    GetBosses,
    GetHeroes,
    PredictBossBattle,
    PredictDuel,
    PredictTeamBattle,
    PredictWaves
)


st.set_page_config(page_title="PRIS Battle Predictor", page_icon="⚔️", layout="centered")
st.title("PRIS: Battle Predictor")

try:
    heroes = GetHeroes()
    bosses = GetBosses()
except Exception as error:
    st.error(str(error))
    st.info("Сначала обучи модели командой: python src/Training.py")
    st.stop()

if not heroes:
    st.error("Список героев пуст.")
    st.stop()

mode = st.radio(
    "Выбери режим",
    ["1v1", "3v1 Boss", "3v3 Team Battle", "Waves"],
    horizontal=True
)

st.divider()

if mode == "1v1":
    st.subheader("Дуэль 1 на 1")

    col1, col2 = st.columns(2)

    with col1:
        hero1 = st.selectbox("Твой герой", heroes, key="duel_hero_1")

    with col2:
        availableEnemies = [hero for hero in heroes if hero != hero1]
        hero2 = st.selectbox("Противник", availableEnemies, key="duel_hero_2")

    if st.button("Рассчитать дуэль"):
        try:
            probability = PredictDuel(hero1, hero2)
            st.metric("Шанс победы первого героя", f"{probability * 100:.2f}%")
            st.caption(f"{hero1} vs {hero2}")
        except Exception as error:
            st.error(str(error))

elif mode == "3v1 Boss":
    st.subheader("Битва с боссом")

    team = st.multiselect(
        "Выбери 3 разных героев",
        heroes,
        max_selections=3,
        key="boss_team"
    )

    selectedBoss = None
    if bosses:
        selectedBoss = st.selectbox("Выбери босса", bosses, key="boss_name")

    if st.button("Рассчитать урон по боссу"):
        try:
            if len(team) != 3:
                st.error("Нужно выбрать ровно 3 героев")
                st.stop()

            predictedDamage = PredictBossBattle(team, selectedBoss)
            st.metric("Прогнозируемый урон", f"{predictedDamage:.1f}")

            teamText = ", ".join(team)
            if selectedBoss:
                st.caption(f"Команда: {teamText} | Босс: {selectedBoss}")
            else:
                st.caption(f"Команда: {teamText}")
        except Exception as error:
            st.error(str(error))

elif mode == "3v3 Team Battle":
    st.subheader("Командный бой 3 на 3")

    st.markdown("### Команда 1")
    team1 = st.multiselect(
        "Выбери 3 героев для первой команды",
        heroes,
        max_selections=3,
        key="team1"
    )

    st.markdown("### Команда 2")
    team2 = st.multiselect(
        "Выбери 3 героев для второй команды",
        heroes,
        max_selections=3,
        key="team2"
    )

    if st.button("Рассчитать командный бой"):
        try:
            if len(team1) != 3:
                st.error("В первой команде должно быть ровно 3 героя")
                st.stop()

            if len(team2) != 3:
                st.error("Во второй команде должно быть ровно 3 героя")
                st.stop()

            probability = PredictTeamBattle(team1, team2)

            st.metric("Шанс победы команды 1", f"{probability * 100:.2f}%")
            st.metric("Шанс победы команды 2", f"{(1 - probability) * 100:.2f}%")

            st.caption(f"Команда 1: {', '.join(team1)}")
            st.caption(f"Команда 2: {', '.join(team2)}")
        except Exception as error:
            st.error(str(error))

elif mode == "Waves":
    st.subheader("Режим волн")

    team = st.multiselect(
        "Выбери 3 разных героев",
        heroes,
        max_selections=3,
        key="waves_team"
    )

    if st.button("Рассчитать волны"):
        try:
            if len(team) != 3:
                st.error("Нужно выбрать ровно 3 героев")
                st.stop()

            predictedWaves = PredictWaves(team)

            st.metric("Прогнозируемое число волн", f"{predictedWaves:.2f}")
            st.caption(f"Команда: {', '.join(team)}")
        except Exception as error:
            st.error(str(error))