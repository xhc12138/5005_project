import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import json
from pyvis.network import Network

# Page config
st.set_page_config(page_title="Knowledge Graph Dashboard", page_icon="🎵", layout="wide")

# Title and Intro
st.title("🎵 VAST MC1 Knowledge Graph Dashboard")
st.markdown("""
**Welcome to the VAST 2025 MC1 Knowledge Graph Dashboard!**

In the data preprocessing phase, we transformed complex JSON data into structured tables and extracted the core graph structure.
To clearly show what each part represents, we designed this dashboard. Use the sidebar to switch between views:
- **📊 Data Overview & Statistics**: Understand basic metrics (e.g., number of songs, record labels) and their relationships.
- **📈 Temporal Evolution**: Observe the publication trends of music works over the years and the proportion of notable works.
- **🕸️ Interactive Network Topology**: Visually explore the connections between nodes and identify core hubs.
""")

# Data Loading
@st.cache_data
def load_data():
    nodes_df = pd.read_csv('output/nodes_df.csv')
    edges_df = pd.read_csv('output/edges_df.csv')
    top_nodes = pd.read_csv('output/top_influential_nodes.csv')
    temporal_stats = pd.read_csv('output/temporal_stats.csv')
    metrics = pd.read_csv('output/network_metrics.csv')
    return nodes_df, edges_df, top_nodes, temporal_stats, metrics

try:
    nodes_df, edges_df, top_nodes, temporal_stats, metrics = load_data()
except Exception as e:
    st.error(f"Failed to load data. Please ensure preprocessing scripts have run: {e}")
    st.stop()

# Sidebar Navigation
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Select a view:", ["📊 Data Overview & Statistics", "📈 Temporal Evolution", "🕸️ Interactive Network Topology"])

if page == "📊 Data Overview & Statistics":
    st.header("1. Network Scale")
    st.markdown("Macro statistics of the entire knowledge graph, reflecting the dataset's scale.")
    cols = st.columns(4)
    for i, row in metrics.iterrows():
        val = row['Value']
        disp_val = f"{val:.4f}" if isinstance(val, float) else str(val)
        cols[i % 4].metric(row['Metric'], disp_val)

    st.markdown("---")
    st.header("2. Entity and Relationship Distribution")
    st.markdown("""
    **Left (Node Types)**: The proportion of different entities (e.g., `Song`, `Person`, `RecordLabel`).  
    **Right (Edge Types)**: The frequency of interaction relationships (e.g., `RecordedBy`, `DistributedBy`).
    """)
    col1, col2 = st.columns(2)
    with col1:
        if 'type' in nodes_df.columns:
            fig_nodes = px.pie(nodes_df, names='type', title="What types of entities are in the network? (Node Types)", hole=0.3)
            st.plotly_chart(fig_nodes, use_container_width=True)
        else:
            st.warning("Missing 'type' column in nodes data.")
            
    with col2:
        if 'type' in edges_df.columns:
            edge_counts = edges_df['type'].value_counts().reset_index()
            edge_counts.columns = ['Relationship', 'Count']
            fig_edges = px.bar(edge_counts, x='Relationship', y='Count', title="What relationships exist? (Edge Types)", text='Count')
            fig_edges.update_traces(textposition='outside')
            st.plotly_chart(fig_edges, use_container_width=True)
        else:
            st.warning("Missing 'type' column in edges data.")

    st.markdown("---")
    st.header("3. Core Influential Nodes (Top 20)")
    st.markdown("""
    We used the **PageRank algorithm** to find the 20 most influential nodes.  
    These are typically top record labels or highly connected songs.
    """)
    st.dataframe(top_nodes[['node_id', 'type', 'degree_centrality', 'pagerank']].style.background_gradient(cmap='Blues'))

elif page == "📈 Temporal Evolution":
    st.header("Temporal Evolution of the Music Graph")
    st.markdown("""
    This view aggregates works by **year** to answer:
    1. How many works were published each year?
    2. How many are 'Notable', and how does the ratio change?
    """)
    
    if not temporal_stats.empty:
        fig_temp = px.bar(temporal_stats, x='year', y=['works_count', 'notable_count'], 
                          title="Total Works vs Notable Works Over Time", 
                          labels={'value': 'Count', 'variable': 'Metrics', 'year': 'Year'},
                          barmode='group')
        st.plotly_chart(fig_temp, use_container_width=True)
        
        fig_ratio = px.line(temporal_stats, x='year', y='notable_ratio', 
                            title="Proportion of Notable Works Over Time", markers=True)
        st.plotly_chart(fig_ratio, use_container_width=True)
    else:
        st.warning("No temporal data available.")

elif page == "🕸️ Interactive Network Topology":
    st.header("Interactive Exploration: Network Topology")
    st.markdown("""
    **Note on Performance**: The original core component contains over 17,000 nodes and 37,000 edges. Rendering this directly in the browser causes the JavaScript physics engine to freeze. 
    To ensure a smooth interactive experience, we dynamically **sub-sampled** the graph to display the **Top 300 most connected nodes** and their relationships.
    """)
    
    graph_type = st.radio("Select Rendering Engine:", ["PyVis Force-Directed (Recommended)", "D3.js Basic Prototype"])
    
    @st.cache_data
    def get_sampled_graph(max_nodes=300):
        # Calculate degree for sampling
        degree_counts = edges_df['source'].value_counts().add(edges_df['target'].value_counts(), fill_value=0)
        top_n_ids = degree_counts.nlargest(max_nodes).index.tolist()
        
        sampled_edges = edges_df[edges_df['source'].isin(top_n_ids) & edges_df['target'].isin(top_n_ids)]
        sampled_nodes = nodes_df[nodes_df['node_id'].isin(top_n_ids)]
        return sampled_nodes, sampled_edges

    samp_nodes, samp_edges = get_sampled_graph(300)
    
    if "PyVis" in graph_type:
        net = Network(height='650px', width='100%', directed=True, bgcolor='#ffffff', font_color='black')
        net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=150)
        
        color_map = {'Song': '#ff9999', 'Person': '#66b3ff', 'RecordLabel': '#99ff99', 'Organization': '#ffcc99', 'Document': '#c2c2f0'}
        
        for _, row in samp_nodes.iterrows():
            ntype = row.get('type', 'Unknown')
            color = color_map.get(ntype, '#cccccc')
            # Handle float values in node_id gracefully
            node_id = int(row['node_id']) if isinstance(row['node_id'], float) else row['node_id']
            net.add_node(node_id, label=str(node_id), title=f"Type: {ntype}", color=color, size=15)
            
        for _, row in samp_edges.iterrows():
            src = int(row['source']) if isinstance(row['source'], float) else row['source']
            tgt = int(row['target']) if isinstance(row['target'], float) else row['target']
            net.add_edge(src, tgt, title=row.get('type', 'Unknown'))
            
        net.save_graph("output/sampled_pyvis.html")
        with open("output/sampled_pyvis.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=700, scrolling=True)
            
    else:
        d3_nodes = [{'id': int(row['node_id']) if isinstance(row['node_id'], float) else row['node_id'], 'group': row.get('type', 'Unknown')} for _, row in samp_nodes.iterrows()]
        d3_edges = [{'source': int(row['source']) if isinstance(row['source'], float) else row['source'], 'target': int(row['target']) if isinstance(row['target'], float) else row['target'], 'type': row.get('type', 'Unknown')} for _, row in samp_edges.iterrows()]
        d3_data_str = json.dumps({'nodes': d3_nodes, 'links': d3_edges})
        
        d3_html = f"""
        <!DOCTYPE html>
        <meta charset="utf-8">
        <style>
        .links line {{ stroke: #999; stroke-opacity: 0.6; }}
        .nodes circle {{ stroke: #fff; stroke-width: 1.5px; cursor: pointer; }}
        .nodes circle:hover {{ stroke: #000; stroke-width: 3px; }}
        </style>
        <body>
        <script src="https://d3js.org/d3.v6.min.js"></script>
        <script>
        var graph = {d3_data_str};
        var width = 800, height = 650;
        
        var color = d3.scaleOrdinal(d3.schemeCategory10);
        
        var svg = d3.select("body").append("svg")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("viewBox", [0, 0, width, height]);
            
        var simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(function(d) {{ return d.id; }}).distance(40))
            .force("charge", d3.forceManyBody().strength(-40))
            .force("center", d3.forceCenter(width / 2, height / 2));
        
        var link = svg.append("g").attr("class", "links").selectAll("line")
            .data(graph.links).enter().append("line");
            
        var node = svg.append("g").attr("class", "nodes").selectAll("circle")
            .data(graph.nodes).enter().append("circle")
            .attr("r", 6)
            .attr("fill", function(d) {{ return color(d.group); }})
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
                
        node.append("title").text(function(d) {{ return "ID: " + d.id + "\\nType: " + d.group; }});
                
        simulation.nodes(graph.nodes).on("tick", ticked);
        simulation.force("link").links(graph.links);
        
        function ticked() {{
            link.attr("x1", function(d) {{ return d.source.x; }})
                .attr("y1", function(d) {{ return d.source.y; }})
                .attr("x2", function(d) {{ return d.target.x; }})
                .attr("y2", function(d) {{ return d.target.y; }});
            node.attr("cx", function(d) {{ return d.x; }})
                .attr("cy", function(d) {{ return d.y; }});
        }}
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x; d.fy = d.y;
        }}
        function dragged(event, d) {{
            d.fx = event.x; d.fy = event.y;
        }}
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null; d.fy = null;
        }}
        </script>
        </body>
        </html>
        """
        components.html(d3_html, height=700, scrolling=True)
