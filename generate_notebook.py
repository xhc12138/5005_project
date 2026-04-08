import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = []

# Step 2
cells.append(nbf.v4.new_markdown_cell("## 步骤二：数据加载与结构验证"))
cells.append(nbf.v4.new_code_cell("""\
import json
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from pyvis.network import Network
import warnings
warnings.filterwarnings('ignore')

# Load data
with open('../data/MC1_graph.json', 'r') as f:
    data = json.load(f)

# Create directed multigraph
G = nx.MultiDiGraph()

# Add nodes
for node in data['nodes']:
    node_id = node['id']
    attrs = {k: v for k, v in node.items() if k != 'id'}
    if 'Node Type' in attrs:
        attrs['type'] = attrs.pop('Node Type')
    G.add_node(node_id, **attrs)

# Add edges
for edge in data['links']:
    source = edge['source']
    target = edge['target']
    attrs = {k: v for k, v in edge.items() if k not in ['source', 'target']}
    if 'Edge Type' in attrs:
        attrs['type'] = attrs.pop('Edge Type')
    if 'edge_type' in attrs:
        attrs['type'] = attrs.pop('edge_type')
    G.add_edge(source, target, **attrs)

# Verification
is_directed_multigraph = G.is_directed() and G.is_multigraph()
num_nodes = G.number_of_nodes()
num_edges = G.number_of_edges()
# To find connected components in a directed graph, we usually use weakly connected components
num_components = nx.number_weakly_connected_components(G)

report = f\"\"\"# Graph Validation Report

- **Is Directed MultiGraph**: {is_directed_multigraph}
- **Total Nodes**: {num_nodes}
- **Total Edges**: {num_edges}
- **Number of Connected Components (Weakly)**: {num_components}
\"\"\"

with open('../output/graph_validation_report.md', 'w') as f:
    f.write(report)

print(report)
"""))

# Step 3
cells.append(nbf.v4.new_markdown_cell("## 步骤三：节点与边 DataFrame 提取"))
cells.append(nbf.v4.new_code_cell("""\
# Nodes DataFrame
nodes_data = []
for node, attrs in G.nodes(data=True):
    node_info = {'node_id': node}
    node_info.update(attrs)
    nodes_data.append(node_info)
nodes_df = pd.DataFrame(nodes_data)

# Edges DataFrame
edges_data = []
for source, target, key, attrs in G.edges(keys=True, data=True):
    edge_info = {'source': source, 'target': target, 'key': key}
    edge_info.update(attrs)
    edges_data.append(edge_info)
edges_df = pd.DataFrame(edges_data)


# Type conversions and missing values
if 'release_date' in nodes_df.columns:
    nodes_df['release_date'] = pd.to_datetime(nodes_df['release_date'], errors='coerce')
if 'notoriety_date' in nodes_df.columns:
    nodes_df['notoriety_date'] = pd.to_datetime(nodes_df['notoriety_date'], errors='coerce')
if 'notable' in nodes_df.columns:
    nodes_df['notable'] = nodes_df['notable'].fillna(False).astype(bool)

# Save to CSV
nodes_df.to_csv('../output/nodes_df.csv', index=False)
edges_df.to_csv('../output/edges_df.csv', index=False)

# Statistics
node_type_counts = nodes_df['type'].value_counts()
edge_type_counts = edges_df['type'].value_counts() if 'type' in edges_df.columns else edges_df.get('edge_type', pd.Series()).value_counts()

print("Node Type Distribution:")
display(pd.DataFrame(node_type_counts))
print("\\nEdge Type Distribution:")
display(pd.DataFrame(edge_type_counts))
"""))

# Step 4
cells.append(nbf.v4.new_markdown_cell("## 步骤四：核心子图与高影响力节点提取"))
cells.append(nbf.v4.new_code_cell("""\
# Extract largest weakly connected component
largest_cc = max(nx.weakly_connected_components(G), key=len)
core_component = G.subgraph(largest_cc).copy()

# Save core component to JSON
core_data = nx.node_link_data(core_component)
with open('../output/core_component.json', 'w') as f:
    json.dump(core_data, f)

# Calculate centrality (use simple Graph for PageRank and Betweenness to avoid multi-edge issues)
G_simple = nx.DiGraph(G)
degree_centrality = nx.degree_centrality(G)
pagerank = nx.pagerank(G_simple)
# Betweenness centrality can be slow, we compute it on simple graph
betweenness = nx.betweenness_centrality(G_simple)

centrality_df = pd.DataFrame({
    'node_id': list(G.nodes()),
    'degree_centrality': [degree_centrality.get(n, 0) for n in G.nodes()],
    'pagerank': [pagerank.get(n, 0) for n in G.nodes()],
    'betweenness': [betweenness.get(n, 0) for n in G.nodes()]
})

# Merge with nodes_df to get type and other info
centrality_df = centrality_df.merge(nodes_df[['node_id', 'type']], on='node_id', how='left')

# Calculate an overall influence score or just sort by PageRank
centrality_df['influence_score'] = centrality_df['pagerank']
top_influential = centrality_df.sort_values(by='influence_score', ascending=False).head(20)

top_influential.to_csv('../output/top_influential_nodes.csv', index=False)

print("Top 10 Influential Nodes:")
display(top_influential.head(10))
"""))

# Step 5
cells.append(nbf.v4.new_markdown_cell("## 步骤五：网络指标与时序统计"))
cells.append(nbf.v4.new_code_cell("""\
# Network Metrics
metrics = {
    'Total Nodes': G.number_of_nodes(),
    'Total Edges': G.number_of_edges(),
    'Density': nx.density(G),
    'Average Degree': sum(dict(G.degree()).values()) / G.number_of_nodes()
}
metrics_df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])
metrics_df.to_csv('../output/network_metrics.csv', index=False)

# Temporal Stats
if 'release_date' in nodes_df.columns:
    nodes_df['year'] = nodes_df['release_date'].dt.year
    temporal_stats = nodes_df.groupby('year').agg(
        works_count=('node_id', 'count'),
        notable_count=('notable', 'sum')
    ).reset_index()
    temporal_stats['notable_ratio'] = temporal_stats['notable_count'] / temporal_stats['works_count']
    temporal_stats.to_csv('../output/temporal_stats.csv', index=False)
    
    print("### Temporal Statistics Summary")
    print(f"- Data spans from {nodes_df['year'].min()} to {nodes_df['year'].max()}")
    print(f"- Year with most works: {temporal_stats.loc[temporal_stats['works_count'].idxmax()]['year']}")
else:
    print("No release_date column found for temporal stats.")
"""))

# Step 6
cells.append(nbf.v4.new_markdown_cell("## 步骤六：初步网络可视化（力导向图）"))
cells.append(nbf.v4.new_code_cell("""\
# PyVis Network
# We use the core component for visualization to avoid browser freezing
net = Network(height='750px', width='100%', directed=True, notebook=True, cdn_resources='remote')

# Add nodes with degree centrality as size
color_map = {'person': '#ff9999', 'organization': '#66b3ff', 'document': '#99ff99', 'location': '#ffcc99', 'event': '#c2c2f0'}

for node, attrs in core_component.nodes(data=True):
    node_type = attrs.get('type', 'unknown')
    color = color_map.get(node_type, '#cccccc')
    size = degree_centrality.get(node, 0.01) * 1000  # Scale size
    net.add_node(node, label=str(node), title=f"Type: {node_type}", color=color, size=max(10, size))

for source, target, attrs in core_component.edges(data=True):
    edge_type = attrs.get('type', 'unknown')
    net.add_edge(source, target, title=edge_type)

net.force_atlas_2based()
# PyVis save logic
html_path = '../output/network_overview.html'
net.show(html_path)
print(f"Network visualization saved to {html_path}")
"""))

# Step 7
cells.append(nbf.v4.new_markdown_cell("## 步骤七：时序与统计交互图表（Plotly 替换 Tableau）"))
cells.append(nbf.v4.new_code_cell("""\
# 1. Node type distribution
fig1 = px.pie(nodes_df, names='type', title='Node Type Distribution')
with open('../output/stats_dashboard.html', 'w') as f:
    f.write(fig1.to_html(full_html=True, include_plotlyjs='cdn'))

# 2. Temporal evolution
if 'year' in nodes_df.columns:
    fig2 = px.bar(temporal_stats, x='year', y=['works_count', 'notable_count'], barmode='group', title='Temporal Evolution of Works')
    with open('../output/temporal_evolution.html', 'w') as f:
        f.write(fig2.to_html(full_html=True, include_plotlyjs='cdn'))

print("Interactive charts saved to output directory.")
"""))

# Step 8
cells.append(nbf.v4.new_markdown_cell("## 步骤八：Design & Technical Validation（Figma + D3.js 原型验证）"))
cells.append(nbf.v4.new_code_cell("""\
# D3 data preparation
d3_nodes = [{'id': n, 'group': attrs.get('type', 'unknown')} for n, attrs in core_component.nodes(data=True)]
d3_edges = [{'source': u, 'target': v, 'type': attrs.get('type', 'unknown')} for u, v, attrs in core_component.edges(data=True)]

d3_data = {'nodes': d3_nodes, 'links': d3_edges}

with open('../output/d3_data.json', 'w') as f:
    json.dump(d3_data, f)

d3_html = \"\"\"<!DOCTYPE html>
<meta charset="utf-8">
<style>
.links line { stroke: #999; stroke-opacity: 0.6; }
.nodes circle { stroke: #fff; stroke-width: 1.5px; }
</style>
<body>
<script src="https://d3js.org/d3.v6.min.js"></script>
<script>
d3.json("d3_data.json").then(function(graph) {
    var width = 800, height = 600;
    var svg = d3.select("body").append("svg").attr("width", width).attr("height", height);
    var simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id(function(d) { return d.id; }))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));
    
    var link = svg.append("g").attr("class", "links").selectAll("line")
        .data(graph.links).enter().append("line");
        
    var node = svg.append("g").attr("class", "nodes").selectAll("circle")
        .data(graph.nodes).enter().append("circle").attr("r", 5)
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));
            
    simulation.nodes(graph.nodes).on("tick", ticked);
    simulation.force("link").links(graph.links);
    
    function ticked() {
        link.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });
        node.attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });
    }
    
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x; d.fy = d.y;
    }
    function dragged(event, d) {
        d.fx = event.x; d.fy = event.y;
    }
    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null; d.fy = null;
    }
});
</script>
</body>
</html>\"\"\"

with open('../output/d3_prototype.html', 'w') as f:
    f.write(d3_html)

print("D3 prototype generated.")
"""))

nb.cells = cells
with open('notebooks/main_preprocess.ipynb', 'w') as f:
    nbf.write(nb, f)
print("Notebook generated.")
