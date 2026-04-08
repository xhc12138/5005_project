# Phase I Summary

## 1. 数据加载成功证明
- **NetworkX 图对象**: `MultiDiGraph` (已验证包含有向多重边结构)
- **节点总数**: 17412
- **边总数**: 37857
- **连通分量数量 (Weakly)**: 16 (核心子图抽取了最大的连通分量)
- 已成功从 JSON 加载，并转化为 DataFrame 保存。

## 2. 输出文件路径列表
所有的输出文件都已保存在 `output/` 文件夹中：
- `graph_validation_report.md`: 数据结构验证报告
- `nodes_df.csv`: 节点 DataFrame，包含属性与缺失值处理
- `edges_df.csv`: 边 DataFrame，包含源、目标与关系类型
- `core_component.json`: 最大连通分量子图 JSON 数据
- `top_influential_nodes.csv`: Top20 高影响力节点列表
- `network_metrics.csv`: 整体网络指标统计
- `temporal_stats.csv`: 时序与流行度统计表
- `network_overview.html`: 初步的 PyVis 力导向图可视化
- `stats_dashboard.html`: 节点类型分布与流派分布图 (Plotly)
- `temporal_evolution.html`: 年代演化与流行度趋势图 (Plotly)
- `d3_data.json`: 供 D3.js 渲染使用的简化版数据
- `d3_prototype.html`: 最简 D3.js 交互式原型

## 3. Top20 高影响力节点 (按 PageRank 排序)
| Node ID | Type | Degree Centrality | PageRank | Betweenness |
|---------|------|-------------------|----------|-------------|
| 15622 | Song | 0.00878 | 0.00673 | 3.107e-05 |
| 174 | RecordLabel | 0.01286 | 0.00660 | 0.0 |
| 79 | RecordLabel | 0.00551 | 0.00567 | 0.0 |
| 1841 | Song | 0.00861 | 0.00478 | 1.118e-05 |
| 620 | RecordLabel | 0.00562 | 0.00441 | 0.0 |
| 262 | RecordLabel | 0.00063 | 0.00400 | 0.0 |
| 218 | RecordLabel | 0.00901 | 0.00393 | 0.0 |
| 460 | RecordLabel | 0.00114 | 0.00344 | 0.0 |
| 9716 | Song | 0.00086 | 0.00339 | 9.788e-06 |
| 138 | RecordLabel | 0.00344 | 0.00310 | 0.0 |
| 444 | RecordLabel | 0.00396 | 0.00290 | 0.0 |
| 7350 | RecordLabel | 0.00005 | 0.00284 | 0.0 |
| 6006 | Song | 0.00476 | 0.00269 | 9.681e-06 |
| 168 | RecordLabel | 0.00246 | 0.00221 | 0.0 |
| 458 | RecordLabel | 0.00034 | 0.00220 | 0.0 |
| 2086 | RecordLabel | 0.00275 | 0.00212 | 0.0 |
| 9 | RecordLabel | 0.00407 | 0.00200 | 0.0 |
| 2322 | RecordLabel | 0.00172 | 0.00193 | 0.0 |
| 46 | RecordLabel | 0.00333 | 0.00174 | 0.0 |
| 9884 | Song | 0.00327 | 0.00172 | 7.116e-06 |

## 4. 所有 HTML 预览链接
本地 HTTP 服务已在端口 `8792` 启动，您可以通过以下链接访问对应的交互式图表：
- **初步力导向图**: [http://localhost:8792/network_overview.html](http://localhost:8792/network_overview.html)
- **节点与流派统计图**: [http://localhost:8792/stats_dashboard.html](http://localhost:8792/stats_dashboard.html)
- **年代演化统计图**: [http://localhost:8792/temporal_evolution.html](http://localhost:8792/temporal_evolution.html)
- **D3.js 原型**: [http://localhost:8792/d3_prototype.html](http://localhost:8792/d3_prototype.html)
