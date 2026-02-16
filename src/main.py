
import streamlit as st
from logic import CreateHeroes, EvaluateHero, MetaRanking

st.set_page_config(page_title="Meta Bot", page_icon="🤖")

st.title("Meta Analyzer Bot")

heroes = CreateHeroes()

if "step" not in st.session_state:
    st.session_state.step = 0

if st.session_state.step == 0:
    st.write("Салам Алейкум ! Я анализирую положение героев в мете .")
    if st.button("Начать"):
        st.session_state.step = 1


elif st.session_state.step == 1:
    st.write("Бот : О состоянии в мете какого героя вы хотите узнать ?")

    hero = st.selectbox("Выберите героя", heroes, format_func=lambda x: x.Name)

    if st.button("Проверить"):
        score, details = EvaluateHero(hero, heroes)
        ranking = MetaRanking(heroes)

        position = [h[0].Name for h in ranking].index(hero.Name) + 1

        st.write(f"Вот место героя в мете : {position} из {len(heroes)}")
        st.write(f"Общий балл: {score}")

        st.write("Против кого он:")
        for name, status in details:
            st.write(f"- {name}: {status}")

        st.session_state.step = 2


elif st.session_state.step == 2:
    if st.button("Анализировать другого героя"):
        st.session_state.step = 1
