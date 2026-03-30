import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("Mapa de Influencia Organizacional")

# --- Cargar data ---
sheet_id = "1Hj0qe5rbzWHv-W86Yjkm4QL8NcJ_QTQaVQ4tcWQqUlE"
gid = "2076772300"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df = pd.read_csv(url)

# --- Limpieza de coordenadas ---
df["results.x"] = df["results.x"].astype(str).str.replace(",", "").astype(float)
df["results.y"] = df["results.y"].astype(str).str.replace(",", "").astype(float)

# --- Filtros ---
col1, col2 = st.columns(2)

departments = df["department"].dropna().unique()
categories = df["results.category"].dropna().unique()

with col1:
    dept = st.selectbox("Departamento", departments)

with col2:
    category = st.multiselect("Categoría", categories, default=categories)

# --- Filtrar ---
filtered = df[df["department"] == dept]

if category:
    filtered = filtered[filtered["results.category"].isin(category)]

# --- Crear red ---
net = Network(height="600px", width="100%")

# 🔥 desactivar física (usamos posiciones reales)
net.toggle_physics(False)

for _, row in filtered.iterrows():

    color = {
        "central": "#2ecc71",
        "intermediary": "#f39c12",
        "peripheral": "#e74c3c"
    }.get(row["results.category"], "#95a5a6")

    net.add_node(
        row["id"],
        label=row["name"],
        x=row["results.x"] / 1e7,   # escala para que se vea bien
        y=row["results.y"] / 1e7,
        color=color,
        size=10,  # tamaño uniforme como el original
        title=f"""
        {row['name']}<br>
        Rank: {row['results.rank']}<br>
        Category: {row['results.category']}
        """
    )

# ❗ Opcional: sin edges (como visual limpio)
# Si querés, después agregamos edges suaves

# --- Render ---
html = net.generate_html()
components.html(html, height=600, scrolling=True)
