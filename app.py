import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("Mapa de Influencia Organizacional")

# --- Cargar data ---
sheet_id = "1Hj0qe5rbzWHv-W86Yjkm4QL8NcJ_QTQaVQ4tcWQqUlE"
gid = "2076772300"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df = pd.read_csv(url)

# --- Filtros ---
col1, col2 = st.columns(2)

with col1:
    dept = st.selectbox("Departamento", df["department"].dropna().unique())

with col2:
    category = st.multiselect(
        "Categoría",
        df["results.category"].dropna().unique()
    )

# --- Filtrar ---
filtered = df[df["department"] == dept]

if category:
    filtered = filtered[filtered["results.category"].isin(category)]

# --- Crear grafo ---
G = nx.Graph()

for _, row in filtered.iterrows():
    G.add_node(
        row["id"],
        label=row["name"],
        category=row["results.category"],
        size=(row["results.degree_centrality"] or 1) * 3
    )

# conexiones por manager
for manager, group in filtered.groupby("manager_name"):
    employees = group["id"].tolist()
    for i in range(len(employees)):
        for j in range(i+1, len(employees)):
            G.add_edge(employees[i], employees[j])

# --- Visual ---
net = Network(height="600px", width="100%")

for node, data in G.nodes(data=True):
    color = {
        "central": "#2ecc71",
        "intermediary": "#f39c12",
        "peripheral": "#e74c3c"
    }.get(data["category"], "#95a5a6")

    net.add_node(
        node,
        label=data["label"],
        color=color,
        size=data["size"]
    )

for source, target in G.edges():
    net.add_edge(source, target)

net.save_graph("graph.html")

HtmlFile = open("graph.html", "r", encoding="utf-8")
components.html(HtmlFile.read(), height=600)
