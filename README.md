# VAST 2025 MC1 Knowledge Graph Visualization Project
# VAST 2025 MC1 知识图谱可视化项目

---

*(English version follows the Chinese version below)*

## 🇨🇳 中文版 (Chinese Version)

### Section 1: 项目目前的具体结构与已完成的功能

本项目旨在处理和可视化 VAST 2025 MC1 数据集中的知识图谱。
目前项目结构如下：

```
5005_project/
│
├── data/
│   └── MC1_graph.json                 # 原始的知识图谱数据文件
├── notebooks/
│   ├── main_preprocess.ipynb          # 数据预处理与特征提取的主 Notebook
│   └── Phase_I_Summary.md             # 第一阶段数据处理的总结报告
├── output/                            # 预处理后生成的所有数据表、子图、图表和压缩包存放目录
│   ├── core_component.json            # 核心最大连通分量子图数据
│   ├── d3_data.json                   # 供 D3.js 渲染使用的简化版 JSON
│   ├── nodes_df.csv                   # 清洗后的节点数据表
│   ├── edges_df.csv                   # 清洗后的边（关系）数据表
│   ├── top_influential_nodes.csv      # 通过 PageRank 计算的 Top 20 核心节点
│   ├── network_metrics.csv            # 网络整体宏观统计指标
│   ├── temporal_stats.csv             # 音乐作品历年发行与流行度统计表
│   └── phase1_deliverables.zip        # 所有产出物的打包备份
├── app.py                             # Streamlit 可视化交互数据看板的主程序
├── generate_notebook.py               # 用于程序化生成预处理 Notebook 的辅助脚本
└── requirements.txt                   # 项目依赖清单
```

**目前已完成的功能：**
1. **数据加载与清洗**：成功读取原始 JSON 格式的图谱数据，提取节点和多重有向边结构，转换为易于分析的 Pandas DataFrame。
2. **核心子图与影响力挖掘**：利用 NetworkX 提取最大连通分量，并使用 PageRank 中心性算法挖掘出排名前 20 的核心影响力节点。
3. **时序与统计特征分析**：按发行年份聚合数据，分析音乐作品数量趋势及“知名(Notable)”作品的演化规律。
4. **多维度交互式数据看板**：通过 Streamlit 构建了一个包含“数据概览”、“时序演化分析”和“交互式网络拓扑”三个页面的 Web 看板，全面呈现分析成果。

### Section 2: 各个代码文件的用途

- **`notebooks/main_preprocess.ipynb`**：数据预处理的核心工作流。在这里进行了 NetworkX 图对象的构建、缺失值填充、数据类型转换、中心性算法计算、网络基础指标的统计以及初始静态图表的生成。
- **`app.py`**：基于 Streamlit 框架构建的交互式前端应用。它负责读取 `output/` 文件夹中清洗好的数据，并将它们以动态图表（Plotly）、指标卡片和网络拓扑图（PyVis/D3.js）的形式直观地展示给用户。
- **`generate_notebook.py`**：一个辅助性 Python 脚本，通过 `nbformat` 库以代码方式自动组装并生成了上述的 `main_preprocess.ipynb`。

### Section 3: 交互式网络拓扑展示界面的详细说明与性能优化

在 `app.py` 驱动的数据看板中，**“交互式网络拓扑 (Interactive Network Topology)”** 是最核心的探索模块。
我们提供了两种渲染引擎供用户选择：
1. **PyVis 力导向图**：物理模拟真实，节点会根据引力和斥力自动散开，适合观察聚类特征。
2. **D3.js 基础原型**：轻量级定制实现，支持拖拽和悬停提示，交互响应更为直接。

**性能挑战与优化考量：**
- **挑战**：我们提取出的核心连通子图包含了超过 **17,000 个节点**和 **37,000 条边**。如果直接将如此庞大的数据量交给浏览器的 JavaScript 物理引擎（如 ForceAtlas2）进行实时渲染，巨大的计算开销会直接导致浏览器卡死（白屏或进度条永久停滞在 0%）。
- **优化方案 (Sub-sampling)**：我们在 `app.py` 中引入了**动态智能采样策略**。在将数据送入前端渲染前，系统会实时计算全网节点的度数（Degree，即连接数），并**仅截取连接最紧密的 Top 300 个核心节点**以及它们之间的边。
- **效果**：这一优化确保了网络拓扑图能够在瞬间完成加载并流畅散开，既保留了网络中最核心骨干的结构特征，又赋予了用户丝滑的拖拽、缩放和探索体验。

### Section 4: 如何复现我们的项目

当其他开发者将我们的代码仓库 clone 下来后，只需按照以下步骤即可完全复现我们的数据看板：

1. **准备数据**：确保 `data/` 目录下存在 `MC1_graph.json` 文件（如果没有，请将源数据集放置于此）。
2. **安装依赖**：
   项目根目录下已经包含了完整的 `requirements.txt`（刚才已将 Streamlit 等新增依赖更新其中）。请使用 conda 或 pip 创建环境并安装依赖：
   ```bash
   # 推荐使用 conda 环境
   conda create -n msbd5005 python=3.10 -y
   conda activate msbd5005
   
   # 安装所有需要的依赖
   pip install -r requirements.txt
   ```
3. **执行数据预处理**：
   如果您需要重新生成分析数据，可以运行 Notebook（或者直接使用我们已提供的 `output/` 中的数据跳过此步）：
   ```bash
   cd notebooks
   jupyter nbconvert --to notebook --execute main_preprocess.ipynb --inplace
   cd ..
   ```
4. **启动交互式数据看板**：
   在项目根目录下运行 Streamlit 启动命令：
   ```bash
   streamlit run app.py
   ```
   随后，在浏览器中访问控制台输出的地址（通常是 `http://localhost:8501`）即可看到完整的可视化网页！

---
---

## 🇬🇧 English Version

### Section 1: Current Project Structure and Completed Features

This project aims to process and visualize the knowledge graph from the VAST 2025 MC1 dataset. 
The current project structure is as follows:

```
5005_project/
│
├── data/
│   └── MC1_graph.json                 # Original knowledge graph JSON data
├── notebooks/
│   ├── main_preprocess.ipynb          # Main Notebook for data preprocessing & feature extraction
│   └── Phase_I_Summary.md             # Summary report of the Phase I data processing
├── output/                            # Directory for all generated tables, subgraphs, and archives
│   ├── core_component.json            # Core largest connected component subgraph data
│   ├── d3_data.json                   # Simplified JSON for D3.js rendering
│   ├── nodes_df.csv                   # Cleaned nodes data table
│   ├── edges_df.csv                   # Cleaned edges (relationships) data table
│   ├── top_influential_nodes.csv      # Top 20 core nodes calculated via PageRank
│   ├── network_metrics.csv            # Macro network statistical metrics
│   ├── temporal_stats.csv             # Temporal statistics of music release and popularity
│   └── phase1_deliverables.zip        # Backup archive of all deliverables
├── app.py                             # Main script for the Streamlit interactive dashboard
├── generate_notebook.py               # Helper script to programmatically generate the Notebook
└── requirements.txt                   # Project dependency list
```

**Completed Features:**
1. **Data Loading and Cleaning**: Successfully parsed the raw JSON graph, extracted nodes and directed multi-edges, and transformed them into Pandas DataFrames for easy analysis.
2. **Core Subgraph and Influence Mining**: Used NetworkX to extract the largest connected component and applied the PageRank centrality algorithm to identify the Top 20 most influential nodes.
3. **Temporal and Statistical Analysis**: Aggregated data by release year to analyze the trend of music publication volume and the evolution of "Notable" works.
4. **Multi-dimensional Interactive Dashboard**: Built a Web dashboard via Streamlit with three views ("Data Overview", "Temporal Evolution", and "Interactive Topology") to comprehensively present the analysis results.

### Section 2: Purpose of Each Code File

- **`notebooks/main_preprocess.ipynb`**: The core workflow for data preprocessing. This handles NetworkX graph construction, missing value imputation, type conversion, centrality calculations, basic metric statistics, and the generation of initial static charts.
- **`app.py`**: The interactive frontend application built with the Streamlit framework. It reads the cleaned data from the `output/` folder and visually presents it to the user using dynamic charts (Plotly), metric cards, and network topologies (PyVis/D3.js).
- **`generate_notebook.py`**: A supplementary Python script that uses the `nbformat` library to automatically assemble and generate the `main_preprocess.ipynb` mentioned above.

### Section 3: Detailed Explanation of the Interactive Topology Interface and Performance Optimization

In the dashboard driven by `app.py`, the **"Interactive Network Topology"** is the most crucial exploration module.
We offer users a choice between two rendering engines:
1. **PyVis Force-Directed Graph**: Provides realistic physics simulation where nodes automatically repel and attract to reveal clustering features.
2. **D3.js Basic Prototype**: A lightweight custom implementation that supports dragging and hover tooltips for direct interaction.

**Performance Challenges and Optimization Considerations:**
- **Challenge**: The core connected subgraph we extracted contains over **17,000 nodes** and **37,000 edges**. Feeding this massive amount of data directly into a browser's JavaScript physics engine (like ForceAtlas2) for real-time rendering causes massive computational overhead, freezing the browser entirely (resulting in a blank screen or a loading bar permanently stuck at 0%).
- **Optimization Strategy (Sub-sampling)**: We introduced a **dynamic intelligent sampling strategy** in `app.py`. Before sending the data to the frontend, the backend calculates the degree (number of connections) of all nodes in real-time and **extracts only the Top 300 most densely connected nodes** and their corresponding edges.
- **Result**: This optimization ensures that the network topology loads and spreads out instantly. It preserves the most critical backbone structure of the network while granting users a buttery-smooth dragging, zooming, and exploratory experience.

### Section 4: How to Reproduce Our Project

When other developers clone our code repository, they can fully reproduce our dashboard by following these steps:

1. **Prepare Data**: Ensure the `MC1_graph.json` file is present in the `data/` directory (if not, place the source dataset there).
2. **Install Dependencies**:
   The project root already contains a complete `requirements.txt` (which has been updated to include new dependencies like Streamlit). Please create an environment and install the requirements:
   ```bash
   # Conda environment is recommended
   conda create -n msbd5005 python=3.10 -y
   conda activate msbd5005
   
   # Install all required dependencies
   pip install -r requirements.txt
   ```
3. **Execute Data Preprocessing**:
   If you need to regenerate the analysis data, run the Notebook (or simply skip this step by using the pre-generated data we provided in the `output/` folder):
   ```bash
   cd notebooks
   jupyter nbconvert --to notebook --execute main_preprocess.ipynb --inplace
   cd ..
   ```
4. **Launch the Interactive Dashboard**:
   Run the Streamlit start command in the project root directory:
   ```bash
   streamlit run app.py
   ```
   Afterward, access the URL printed in the console (usually `http://localhost:8501`) in your browser to view the complete visualized webpage!
