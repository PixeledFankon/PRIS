
import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx

from logic import MetaLogic
from knowledge_graph import CreateGraph, FindRelatedEntities

meta = MetaLogic()

st.title("Проверка меты")

st.divider()
st.title("Knowledge Graph Explorer")

G = CreateGraph(meta.rules)
allNodes = list(G.nodes())
selectedNode = st.selectbox("Выберите узел:", allNodes)

if st.button("Найти связи"):
    neighbors = FindRelatedEntities(G, selectedNode)
    st.success(f"Узел '{selectedNode}' связан с: {', '.join(map(str, neighbors))}")

st.write("Визуализация графа")
fig, ax = plt.subplots(figsize=(10, 6))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=2000, font_size=9, ax=ax)
st.pyplot(fig)

