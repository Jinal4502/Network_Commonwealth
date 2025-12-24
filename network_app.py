# import streamlit as st
# import pandas as pd
# import graphistry
# import matplotlib
# import matplotlib.pyplot as plt

# # --- Streamlit Page Setup ---
# st.set_page_config(page_title="Correlation Network Explorer", layout="wide")
# st.title("📊 Commonwealth Correlation Network Explorer")

# # --- 1. File input or default file ---
# uploaded_file = st.file_uploader("Upload correlation data (.csv or .xlsx)", type=["csv", "xlsx"])
# if uploaded_file is not None:
#     if uploaded_file.name.endswith(".csv"):
#         df = pd.read_csv(uploaded_file)
#     else:
#         df = pd.read_excel(uploaded_file)
# else:
#     df = pd.read_excel("./commonwealth_correlationanalysis.xlsx", engine="openpyxl")
#     st.info("Using default dataset: commonwealth_correlationanalysis.xlsx")

# # --- 2. Connect to Graphistry ---
# graphistry.register(api=3, server="hub.graphistry.com",
#                     username="jjvyas", password="Jinal@4502")

# # --- 3. Sidebar: single slider for correlation ---
# st.sidebar.header("Network Filter")
# corr_threshold = st.sidebar.slider("Minimum |correlation|", 0.0, 1.0, 0.3, 0.05)

# # --- 4. Filter data by p-value, correlation, and remove self-nodes ---
# filtered_edges_df = df[
#     (df["p_value"] < 0.05)
#     & (abs(df["correlation_estimate"]) > corr_threshold)
#     & (df["variable1"] != df["variable2"])  # remove self-nodes
# ].copy()

# if filtered_edges_df.empty:
#     st.warning(f"⚠️ No edges meet the threshold (|r| > {corr_threshold}).")
#     st.stop()

# # --- 5. Prepare node data ---
# nodes_from = filtered_edges_df[["variable1", "category1"]].rename(
#     columns={"variable1": "node", "category1": "category"}
# )
# nodes_to = filtered_edges_df[["variable2", "category2"]].rename(
#     columns={"variable2": "node", "category2": "category"}
# )
# filtered_nodes_df = pd.concat([nodes_from, nodes_to]).drop_duplicates("node")

# # --- 6. Fixed bright color palette for up to 4 categories ---
# bright_colors = ["#FF6F61", "#6B5B95", "#88B04B", "#F7CAC9"]  # bright palette
# unique_categories = filtered_nodes_df["category"].unique()
# topic_colors = {
#     cat: bright_colors[i % len(bright_colors)] for i, cat in enumerate(unique_categories)
# }

# # --- 7. Edge colors for correlation sign ---
# filtered_edges_df["corr_sign"] = filtered_edges_df["correlation_estimate"].apply(
#     lambda x: "positive" if x >= 0 else "negative"
# )
# dummy_colors = {"positive": "#1f77b4", "negative": "#d62728"}

# # --- 8. Node size mapping ---
# normalized_point_sizes = {
#     n: 200 + 800 * (i / len(filtered_nodes_df))
#     for i, n in enumerate(filtered_nodes_df["node"])
# }

# # --- 9. Build Graphistry object (unidirectional, no arrows) ---
# g = (
#     graphistry.edges(filtered_edges_df, source="variable1", destination="variable2", directed=False)
#     .nodes(filtered_nodes_df, node="node")
#     .bind(node="node")
#     .bind(edge_weight="correlation_estimate")
#     .bind(edge_title="corr_sign")
#     .encode_point_color("category", categorical_mapping=topic_colors, as_categorical=True)
#     .encode_edge_color("corr_sign", categorical_mapping=dummy_colors, as_categorical=True)
#     .encode_point_size("node", categorical_mapping=normalized_point_sizes)
#     .encode_edge_icon(None)  
# )

# # --- 10. Layout configuration ---
# g = g.layout_settings(
#     lin_log=True,
#     strong_gravity=False,
#     dissuade_hubs=True,
#     edge_influence=2.0,
#     precision_vs_speed=1.0,
#     gravity=1.0,
#     # show_arrows=False  # remove arrows (make undirected-looking)
# )

# # --- 11. Render Graphistry Plot ---
# st.subheader("Interactive Graphistry Correlation Network")

# try:
#     plot_url = g.plot(render=False)
#     st.components.v1.iframe(plot_url, height=800)
# except Exception as e:
#     st.error(f"Graphistry failed to render: {e}")

# # --- 12. Sidebar summary ---
# st.sidebar.markdown("### Network Summary")
# st.sidebar.write(f"**Edges:** {len(filtered_edges_df)}")
# st.sidebar.write(f"**Nodes:** {len(filtered_nodes_df)}")
# st.sidebar.write(f"**Categories:** {len(unique_categories)}")
# st.sidebar.caption("Filtered automatically for p < 0.05")

# # --- 13. Legend for node categories ---
# st.markdown("### 🗂️ Category Legend")
# legend_cols = st.columns(len(topic_colors))
# for i, (cat, color) in enumerate(topic_colors.items()):
#     with legend_cols[i]:
#         st.markdown(
#             f"<div style='background-color:{color}; width:25px; height:25px; display:inline-block; border-radius:50%;'></div> "
#             f"<b>{cat}</b>",
#             unsafe_allow_html=True
#         )

import streamlit as st
import pandas as pd
import graphistry
import matplotlib
import matplotlib.pyplot as plt
import numpy as np


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
    df = pd.read_excel("./commonwealth_correlationanalysis.xlsx", engine="openpyxl")
    st.info("Using default dataset: commonwealth_correlationanalysis.xlsx")


# --- 2. Connect to Graphistry ---
graphistry.register(
    api=3,
    server="hub.graphistry.com",
    username="jjvyas",
    password="Jinal@4502"
)


# --- 3. Sidebar: correlation + category filter ---
st.sidebar.header("Network Filter")
corr_threshold = st.sidebar.slider("Minimum |correlation|", 0.0, 1.0, 0.3, 0.05)

# We will define unique_categories AFTER we know which edges survive;
# for now, do correlation/p-value filtering on the raw df.


# --- 4. Filter by correlation, p-value, self-nodes ---
edge_filtered = df[
    (df["p_value"] < 0.05)
    & (abs(df["correlation_estimate"]) > corr_threshold)
    & (df["variable1"] != df["variable2"])
].copy()

if edge_filtered.empty:
    st.warning(f"⚠️ No edges meet the threshold (|r| > {corr_threshold}).")
    st.stop()


# --- 5. Prepare node data from edge_filtered ---
nodes_from = edge_filtered[["variable1", "category1"]].rename(
    columns={"variable1": "node", "category1": "category"}
)
nodes_to = edge_filtered[["variable2", "category2"]].rename(
    columns={"variable2": "node", "category2": "category"}
)
filtered_nodes_df = pd.concat([nodes_from, nodes_to]).drop_duplicates("node")

# Categories present in the filtered graph
unique_categories = filtered_nodes_df["category"].unique()


# --- 3a. Now that we know categories, build sidebar category filter ---
st.sidebar.subheader("Categories")
selected_categories = st.sidebar.multiselect(
    "Select categories to include:",
    options=unique_categories.tolist(),
    default=unique_categories.tolist()
)

# If user deselects some categories, re-filter edges & nodes
if selected_categories:
    edge_filtered = edge_filtered[
        (edge_filtered["category1"].isin(selected_categories)) &
        (edge_filtered["category2"].isin(selected_categories))
    ].copy()

    if edge_filtered.empty:
        st.warning(
            f"⚠️ No edges meet criteria (|r| > {corr_threshold}, "
            f"categories: {selected_categories})."
        )
        st.stop()

    nodes_from = edge_filtered[["variable1", "category1"]].rename(
        columns={"variable1": "node", "category1": "category"}
    )
    nodes_to = edge_filtered[["variable2", "category2"]].rename(
        columns={"variable2": "node", "category2": "category"}
    )
    filtered_nodes_df = pd.concat([nodes_from, nodes_to]).drop_duplicates("node")

    unique_categories = filtered_nodes_df["category"].unique()

filtered_edges_df = edge_filtered


# --- 6. Fixed bright color palette for categories ---
bright_colors = ["#FF6F61", "#6B5B95", "#88B04B", "#F7CAC9"]  # bright palette
topic_colors = {
    cat: bright_colors[i % len(bright_colors)] for i, cat in enumerate(unique_categories)
}


# --- 7. Edge colors for correlation sign ---
filtered_edges_df["corr_sign"] = filtered_edges_df["correlation_estimate"].apply(
    lambda x: "positive" if x >= 0 else "negative"
)
dummy_colors = {"positive": "#1f77b4", "negative": "#d62728"}


# --- 8. Node size mapping ---
normalized_point_sizes = {
    n: 200 + 800 * (i / len(filtered_nodes_df))
    for i, n in enumerate(filtered_nodes_df["node"])
}


# --- 8b. Explicit positions: category circle + inner circle ---

# parameters
R_outer = 8.0        # distance between category groups
R_inner = 2.0        # radius of each category's inner node circle

# deterministic ordering for reproducibility
filtered_nodes_df = filtered_nodes_df.sort_values(['category', 'node']).reset_index(drop=True)

# map category -> index
cat_to_idx = {cat: i for i, cat in enumerate(unique_categories)}
n_cat = len(unique_categories)

xs = []
ys = []

for _, row in filtered_nodes_df.iterrows():
    cat = row['category']
    node = row['node']

    # nodes in same category
    cat_nodes = filtered_nodes_df[filtered_nodes_df['category'] == cat]
    pos_in_cat = cat_nodes[cat_nodes['node'] == node].index[0] - cat_nodes.index[0]
    n_in_cat = len(cat_nodes)

    # center of category group on big circle
    theta_cat = 2 * np.pi * cat_to_idx[cat] / max(n_cat, 1)
    cx = R_outer * np.cos(theta_cat)
    cy = R_outer * np.sin(theta_cat)

    # angle within category's inner circle
    theta_node = 2 * np.pi * pos_in_cat / max(n_in_cat, 1)

    x = cx + R_inner * np.cos(theta_node)
    y = cy + R_inner * np.sin(theta_node)

    xs.append(x)
    ys.append(y)

filtered_nodes_df['x'] = xs
filtered_nodes_df['y'] = ys


# --- 9. Build Graphistry object (unidirectional, no arrows) ---
g = (
    graphistry.edges(filtered_edges_df, source="variable1", destination="variable2", directed=False)
    .nodes(filtered_nodes_df, node="node")
    .bind(node="node")
    .bind(edge_weight="correlation_estimate")
    .bind(edge_title="corr_sign")
    .bind(point_x='x', point_y='y')   # manual positions
    .encode_point_color("category", categorical_mapping=topic_colors, as_categorical=True)
    .encode_edge_color("corr_sign", categorical_mapping=dummy_colors, as_categorical=True)
    .encode_point_size("node", categorical_mapping=normalized_point_sizes)
    .encode_edge_icon(None)
    .settings(url_params={'play': 0})  # stop FA2; keep manual layout
)


# --- 11. Render Graphistry Plot ---
st.subheader("Interactive Graphistry Correlation Network")

try:
    plot_url = g.plot(render=False)
    st.components.v1.iframe(plot_url, height=800)
except Exception as e:
    st.error(f"Graphistry failed to render: {e}")


# --- 12. Sidebar summary ---
st.sidebar.markdown("### Network Summary")
st.sidebar.write(f"**Edges:** {len(filtered_edges_df)}")
st.sidebar.write(f"**Nodes:** {len(filtered_nodes_df)}")
st.sidebar.write(f"**Categories:** {len(unique_categories)}")
st.sidebar.caption("Filtered automatically for p < 0.05 and selected categories")


# --- 13. Legend for node categories ---
st.markdown("### 🗂️ Category Legend")
legend_cols = st.columns(len(topic_colors) if len(topic_colors) > 0 else 1)
for i, (cat, color) in enumerate(topic_colors.items()):
    with legend_cols[i]:
        st.markdown(
            f"<div style='background-color:{color}; "
            f"width:25px; height:25px; display:inline-block; border-radius:50%;'></div> "
            f"<b>{cat}</b>",
            unsafe_allow_html=True
        )
