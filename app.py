import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import random

st.set_page_config(layout="wide")

st.title("Mapa de Influencia Organizacional")

# =========================
# DATA
# =========================
sheet_id = "1Hj0qe5rbzWHv-W86Yjkm4QL8NcJ_QTQaVQ4tcWQqUlE"
gid = "2076772300"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df = pd.read_csv(url)

# =========================
# LIMPIEZA COORDENADAS
# =========================
df["results.x"] = df["results.x"].astype(str).str.replace(",", "").astype(float)
df["results.y"] = df["results.y"].astype(str).str.replace(",", "").astype(float)

# =========================
# CENTRAR (SIN DEFORMAR)
# =========================
x_mean = df["results.x"].mean()
y_mean = df["results.y"].mean()

df["x_centered"] = df["results.x"] - x_mean
df["y_centered"] = df["results.y"] - y_mean

# =========================
# FILTROS
# =========================
col1, col2 = st.columns(2)

departments = sorted(df["department"].dropna().unique())
categories = sorted(df["results.category"].dropna().unique())

with col1:
    dept = st.selectbox("Departamento", ["Todos"] + list(departments))

with col2:
    category = st.multiselect("Categoría", categories, default=categories)

# =========================
# FILTRADO
# =========================
filtered = df.copy()

if dept != "Todos":
    filtered = filtered[filtered["department"] == dept]

if category:
    filtered = filtered[filtered["results.category"].isin(category)]

# =========================
# RED
# =========================
net = Network(height="700px", width="100%")

# 🔥 SIN MOVIMIENTO
net.toggle_physics(False)

# 🔥 EVITAR QUE PYVIS REORDENE
net.options.layout = {"improvedLayout": False}

# 🔥 EDGES RECTOS (menos ruido visual)
net.options.edges.smooth = False

# =========================
# COLORES
# =========================
color_map = {
    "central": "#2ecc71",
    "intermediary": "#f39c12",
    "peripheral": "#e74c3c"
}

# =========================
# ESCALA (ajustá si querés)
# =========================
scale = 500000  # 🔥 clave para mantener forma orgánica

# =========================
# NODOS
# =========================
for _, row in filtered.iterrows():

    color = color_map.get(row["results.category"], "#95a5a6")

    net.add_node(
        row["id"],
        label=" ",  # 🔥 evita mostrar ID
        x=row["x_centered"] / scale,
        y=row["y_centered"] / scale,
        color=color,
        size=2,  # 🔥 tamaño tipo producto real
        borderWidth=0,
        title=f"""
        <b>{row['name']}</b><br>
        Rank: {row['results.rank']}<br>
        Categoría: {row['results.category']}<br>
        Influence: {row['results.influence']}
        """
    )

# =========================
# EDGES (DENSIDAD ALTA, COLOR CORRECTO)
# =========================
nodes = filtered[["id", "results.category"]].values.tolist()

for node_id, cat in nodes:

    color = color_map.get(cat, "#cccccc")

    # 🔥 densidad alta pero controlada
    connections = random.sample(nodes, min(5, len(nodes)))

    for target_id, _ in connections:
        if node_id != target_id:
            net.add_edge(
                node_id,
                target_id,
                width=0.2,
                color=color,
                opacity=0.08
            )

# =========================
# RENDER
# =========================
html = net.generate_html()
components.html(html, height=700, scrolling=True)
