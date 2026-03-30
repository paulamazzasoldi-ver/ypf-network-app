import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# --- FIX CSS (mejora interacción) ---
st.markdown("""
<style>
iframe {
    pointer-events: auto;
}
</style>
""", unsafe_allow_html=True)

st.title("Mapa de Influencia Organizacional")

# --- Cargar data ---
sheet_id = "1Hj0qe5rbzWHv-W86Yjkm4QL8NcJ_QTQaVQ4tcWQqUlE"
gid = "2076772300"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df = pd.read_csv(url)

# --- Filtros ---
col1, col2 = st.columns(2)

departments = df["department"].dropna().unique()
categories = df["results.category"].dropna().unique()

with col1:
    dept = st.selectbox(
        "Departamento",
        departments,
        index=0  # default
    )

with col2:
    category = st.multiselect(
        "Categoría",
        categories,
        default=categories  # 👈 muestra TODO por default
    )

# --- Filtrar ---
filtered = df[df["department"] == dept]

if category:
    filtered = filtered[filtered["results.category"].isin(category)]

# --- LIMITAR tamaño (evita que explote) ---
filtered = filtered.head(120)

# --- Crear grafo ---
G = nx.Graph()

for _, row in filtered.iterrows():
    G.add_node(
        row["id"],
        label=row["name"],
        category=row["results.category"],
        size=(row["results.degree_centrality"] or 1) * 3
    )

# --- Conexiones livianas (evita grafo denso) ---
for manager, group in filtered.groupby("manager_name"):
    employees = group["id"].tolist()

    for i in range(len(employees) - 1):
        G.add_edge(employees[i], employees[i+1])

# --- Visual ---
net = Network(height="500px", width="100%")

# opciones para mejorar UX
net.set_options("""
var options = {
  interaction: {
    hover: true,
    zoomView: true,
    dragView: true
  },
  physics: {
    stabilization: true
  }
}
""")

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

# --- Render correcto (SIN archivos locales) ---
html = net.generate_html()

components.html(html, height=500, scrolling=True)
