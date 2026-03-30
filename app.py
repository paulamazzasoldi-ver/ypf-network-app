import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# --- CSS fix (interacción) ---
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

# --- Limpieza de coordenadas ---
df["results.x"] = df["results.x"].astype(str).str.replace(",", "").astype(float)
df["results.y"] = df["results.y"].astype(str).str.replace(",", "").astype(float)

# --- Filtros ---
col1, col2 = st.columns(2)

departments = sorted(df["department"].dropna().unique())
categories = sorted(df["results.category"].dropna().unique())

with col1:
    dept = st.selectbox("Departamento", departments)

with col2:
    category = st.multiselect(
        "Categoría",
        categories,
        default=categories
    )

# --- Filtrar ---
filtered = df[df["department"] == dept]

if category:
    filtered = filtered[filtered["results.category"].isin(category)]

# --- Crear red ---
net = Network(height="600px", width="100%")

# 🔥 usamos layout real (sin física)
net.toggle_physics(False)

# estilo visual
net.set_options("""
{
  "nodes": {
    "shape": "dot",
    "scaling": {
      "min": 3,
      "max": 6
    }
  },
  "interaction": {
    "hover": true
  }
}
""")

# --- Nodos ---
for _, row in filtered.iterrows():

    color = {
        "central": "#2ecc71",
        "intermediary": "#f39c12",
        "peripheral": "#e74c3c"
    }.get(row["results.category"], "#95a5a6")

    net.add_node(
        row["id"],
        label="",  # 🔥 sin nombres visibles
        x=row["results.x"] / 1e7,
        y=row["results.y"] / 1e7,
        color=color,
        size=4,  # 🔥 nodos chicos tipo original
        borderWidth=0.5,
        title=f"""
        <b>{row['name']}</b><br>
        Rank: {row['results.rank']}<br>
        Categoría: {row['results.category']}<br>
        Influence: {row['results.influence']}
        """
    )

# --- Render ---
html = net.generate_html()
components.html(html, height=600, scrolling=True)
