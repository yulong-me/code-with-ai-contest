# 📡 5G 信号可视化看板 (5G Dashboard)

这是一个极具“极客视觉体验”的 5G 信号数据可视化 Web 看板，基于 Python 和 Streamlit 框架构建。本项目为 "Code with AI" 极客探索赛的完赛作品。

## 🌟 核心功能

1. **3D 交互地图渲染**：
   - 使用 `pydeck` 将 5G 信号点映射在 3D 地图上。
   - **颜色指示**：动态根据 RSRP (信号接收功率) 变色。信号好 (> -90dBm) 显示为绿色，较差 (< -110dBm) 显示为红色，一般显示为黄色。
   - **高度指示**：信号柱的高度映射为该数据点的下载速率 (Download_Mbps)，高度越高表示速率越快，给您最直观的性能感受。
   - 鼠标悬停可查看详细基站和小区信息。

2. **动态侧边栏筛选**：
   - 支持按 **5G频段 (Band)** 进行筛选。
   - 支持通过拖动滑动条按 **RSRP 范围** 过滤数据。
   - 右侧 3D 地图和统计图表会根据您的筛选条件**实时无缝联动更新**。

3. **数据概览分析**：
   - 提供统计图表，直观展示当前条件下的“各频段基站数量分布”。
   - 提供各类终端 (Smartphone, CPE, IoT 等) 的数量比例分布图。

## 🚀 快速开始

本项目依赖纯 Python 环境，无需配置复杂的前端工程。

### 1. 环境准备

请确保您已安装 Python (建议 3.8 及以上版本)。在终端中执行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

### 2. 运行应用

执行以下命令启动 Streamlit 服务器：

```bash
streamlit run app.py
```

服务器启动后，您的默认浏览器会自动打开 `http://localhost:8501` 并展示看板。

### 3. 运行单元测试

本项目遵循优秀的工程化实践，包含了针对核心数据处理逻辑的单元测试。运行以下命令执行测试：

```bash
python -m unittest test_data_processor.py
```

## 📂 项目结构

- `app.py`: Streamlit Web 应用的主入口文件，包含 UI 布局和交互逻辑。
- `data_processor.py`: 核心数据处理模块，负责读取 CSV 并处理地图颜色映射。
- `test_data_processor.py`: 单元测试文件。
- `data/signal_samples.csv`: 提供的 5G 信号测试数据集。
- `requirements.txt`: Python 依赖清单。

## 🤖 AI 协作说明

本项目的核心代码与此文档均在 AI Coding Agent 辅助下完成。详细的交互记录已保存在 `AI_PROMPTS.md` 文件中。