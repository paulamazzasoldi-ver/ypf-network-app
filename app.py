import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import random

st.set_page_config(layout="wide")

st.title("Mapa de Influencia Organizacional")

# --- DATA ---
sheet_id = "1Hj0qe5rbzWHv-W86Yjkm4QL8NcJ_QTQaVQ4tcWQqUlE"
gid = "2076772300"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df = pd.read_csv(url)

# --- LIMPIEZA ---
df["results.x"] = df["results.x"].astype(str).str.replace(",", "").astype(float)
df["results.y"] = df["results.y"].astype(str).str.replace(",", "").astype(float)

# --- FILTROS ---
col1, col2 = st.columns(2)

departments = sorted(df["department"].dropna().unique())
categories = sorted(df["results.category"].dropna().unique())

with col1:
    dept = st.selectbox("Departamento", ["Todos"] + list(departments))

with col2:
    category = st.multiselect("Categoría", categories, default=categories)

# --- FILTRADO ---
filtered = df.copy()

if dept != "Todos":
    filtered = filtered[filtered["department"] == dept]

if category:
    filtered = filtered[filtered["results.category"].isin(category)]

# --- RED ---
net = Network(height="650px", width="100%")
net.set_options("""
{
  "physics": {
    "enabled": false
  }
}
""")
color_map = {
    "central": "#2ecc71",
    "intermediary": "#f39c12",
    "peripheral": "#e74c3c"
}

# --- NODOS (MUY CHICOS 🔥) ---
for _, row in filtered.iterrows():

    color = color_map.get(row["results.category"], "#95a5a6")

    net.add_node(
        row["id"],
        label=" ",
        x=row["results.x"] / 1e7,
        y=row["results.y"] / 1e7,
        color=color,
        size=2,  # 🔥 CLAVE: bien chico
        borderWidth=0,
        title=f"""
        <b>{row['name']}</b><br>
        Rank: {row['results.rank']}<br>
        Categoría: {row['results.category']}
        """
    )

# --- EDGES (FULL DENSITY 🔥) ---
nodes = filtered[["id", "results.category"]].values.tolist()

for node_id, category in nodes:

    color = color_map.get(category, "#cccccc")

    # 🔥 MÁS conexiones → densidad real
    connections = random.sample(nodes, min(8, len(nodes)))

    for target_id, _ in connections:
        if node_id != target_id:
            net.add_edge(
                node_id,
                target_id,
                width=0.2,  # 🔥 más fino
                color=color,  # 🔥 color correcto
                opacity=0.08  # 🔥 súper transparente
            )

# --- ESTILO VISUAL ---
net.set_options("""
{
  "edges": {
    "smooth": {
      "type": "continuous"
    }
  },
  "interaction": {
    "hover": true
  }
}
""")

# --- RENDER ---
html = net.generate_html()
components.html(html, height=650, scrolling=True)
