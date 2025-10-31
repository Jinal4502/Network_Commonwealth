import streamlit as st
import pandas as pd
import graphistry
import matplotlib
import matplotlib.pyplot as plt

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Correlation Network Explorer", layout="wide")
st.title("📊 Commonwealth Correlation Network Explorer")

# --- 1. File input or default file ---
uploaded_file = st.file_uploader("Upload correlation data (.csv or .xlsx)", type=["csv", "xlsx"])
if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
else:
    df = pd.read_excel("https://github.com/Jinal4502/Network_Commonwealth/edit/main/commonwealth_correlationanalysis.xlsx")
    st.info("Using default dataset: commonwealth_correlationanalysis.xlsx")

# --- 2. Connect to Graphistry ---
graphistry.register(api=3, server="hub.graphistry.com",
                    username="jjvyas", password="Jinal@4502")

# --- 3. Sidebar: single slider for correlation ---
st.sidebar.header("Network Filter")
corr_threshold = st.sidebar.slider("Minimum |correlation|", 0.0, 1.0, 0.3, 0.05)

# --- 4. Filter data by p-value and correlation ---
filtered_edges_df = df[(df["p_value"] < 0.05) &
                       (abs(df["correlation_estimate"]) > corr_threshold)].copy()

if filtered_edges_df.empty:
    st.warning("⚠️ No edges meet the current correlation threshold (|r| > {}).".format(corr_threshold))
    st.stop()

# --- 5. Prepare node data ---
nodes_from = filtered_edges_df[["variable1", "category1"]].rename(
    columns={"variable1": "node", "category1": "category"}
)
nodes_to = filtered_edges_df[["variable2", "category2"]].rename(
    columns={"variable2": "node", "category2": "category"}
)
filtered_nodes_df = pd.concat([nodes_from, nodes_to]).drop_duplicates("node")

# --- 6. Color mappings ---
unique_categories = filtered_nodes_df["category"].unique()
palette = matplotlib.colormaps.get_cmap("tab10")
topic_colors = {
    cat: matplotlib.colors.rgb2hex(palette(i / len(unique_categories))[:3])
    for i, cat in enumerate(unique_categories)
}

filtered_edges_df["corr_sign"] = filtered_edges_df["correlation_estimate"].apply(
    lambda x: "positive" if x >= 0 else "negative"
)
dummy_colors = {"positive": "#1f77b4", "negative": "#d62728"}

# --- 7. Node size mapping ---
normalized_point_sizes = {
    n: 200 + 800 * (i / len(filtered_nodes_df))
    for i, n in enumerate(filtered_nodes_df["node"])
}

# --- 8. Build Graphistry object ---
g = (
    graphistry.edges(filtered_edges_df, source="variable1", destination="variable2")
    .nodes(filtered_nodes_df, node="node")
    .bind(node="node")
    .bind(edge_weight="correlation_estimate")
    .bind(edge_title="corr_sign")
    .encode_point_color("category", categorical_mapping=topic_colors, as_categorical=True)
    .encode_edge_color("corr_sign", categorical_mapping=dummy_colors, as_categorical=True)
    .encode_point_size("node", categorical_mapping=normalized_point_sizes)
)

# --- 9. Layout configuration ---
g = g.layout_settings(
    lin_log=True,
    strong_gravity=False,
    dissuade_hubs=True,
    edge_influence=2.0,
    precision_vs_speed=1.0,
    gravity=1.0,
)

# --- 10. Render Graphistry Plot ---
st.subheader("Interactive Graphistry Correlation Network")

try:
    plot_url = g.plot(render=False)
    st.components.v1.iframe(plot_url, height=800)
except Exception as e:
    st.error(f"Graphistry failed to render: {e}")

# --- 11. Sidebar summary ---
st.sidebar.markdown("### Network Summary")
st.sidebar.write(f"**Edges:** {len(filtered_edges_df)}")
st.sidebar.write(f"**Nodes:** {len(filtered_nodes_df)}")
st.sidebar.write(f"**Categories:** {len(unique_categories)}")
st.sidebar.caption("Filtered automatically for p < 0.05")
