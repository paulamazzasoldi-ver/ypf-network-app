import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import math

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
# LIMPIEZA
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

net.toggle_physics(False)
net.options.layout = {"improvedLayout": False}
net.options.edges.smooth = False

net.options.nodes = {
    "shape": "dot",
    "font": {"size": 0}
}

# =========================
# COLORES
# =========================
color_map = {
    "central": "#2ecc71",
    "intermediary": "#f39c12",
    "peripheral": "#e74c3c"
}

# =========================
# ESCALA
# =========================
scale = 550000
# =========================
# NODOS
# =========================
nodes_data = []

for _, row in filtered.iterrows():

    color = color_map.get(row["results.category"], "#95a5a6")

    x = row["x_centered"] / scale
    y = row["y_centered"] / scale

    net.add_node(
        row["id"],
        label=" ",
        x=x,
        y=y,
        color=color,
        size=6,
        borderWidth=0,
        title=f"""
        <b>{row['name']}</b><br>
        Rank: {row['results.rank']}<br>
        Categoría: {row['results.category']}
        """
    )

    nodes_data.append((row["id"], x, y, color))

# =========================
# EDGES POR CERCANÍA (🔥 CLAVE)
# =========================
def distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

threshold = 0.5  # 🔥 ajustar esto es CLAVE

for i in range(len(nodes_data)):
    id1, x1, y1, color1 = nodes_data[i]

    # convertir color a RGBA
    hex_color = color1.replace("#", "")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    edge_color = f"rgba({r},{g},{b},0.15)"  # 🔥 más visible que antes

    for j in range(i+1, len(nodes_data)):
        id2, x2, y2, _ = nodes_data[j]

        if distance((x1, y1), (x2, y2)) < threshold:
            net.add_edge(
                id1,
                id2,
                width=0.2,
                color=edge_color
            )

# =========================
# RENDER
# =========================
html = net.generate_html()
components.html(html, height=700, scrolling=True)
