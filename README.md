# 5G 信号可视化看板

一个基于 Streamlit 的本地 5G 路测数据看板，用于展示 `data/signal_samples.csv` 中的经纬度、小区、频段、RSRP、SINR、终端类型和下载速率。

## 功能

- 读取 CSV 路测数据，并对缺失字段、空 CSV、脏数值做安全降级。
- 提供经纬度 RSRP 散点地图；在 WebGL 可用时提供 3D 柱状地图，柱高随 `Download_Mbps` 变化，并附同数据源的柱高降级图。
- 地图颜色按 `RSRP_dBm` 分级：强信号为绿色，弱覆盖为红色。
- 提供信号质量分布、核心 KPI 卡片和统一的专业数据看板视觉样式。
- 侧边栏支持按频段、终端类型、RSRP 范围联动筛选。
- 展示信号点数量、平均 RSRP、平均下载速率、弱覆盖点数量。
- 展示各频段基站数量和终端类型占比。
- 包含针对数据清洗、空数据和组合筛选的单元测试。

## 运行

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

打开终端输出的本地地址即可查看看板，默认通常是 `http://localhost:8501`。

## 测试

```bash
.venv/bin/python -m pytest
```

## 数据降级策略

看板不会因为样本不完整而崩溃：

- 缺少 `Band`、`TerminalType`、`CellID` 时显示为 `Unknown`。
- 缺少 `RSRP_dBm` 时按 `-120 dBm` 处理，归入弱覆盖。
- 缺少 `SINR_dB` 或 `Download_Mbps` 时按 `0` 处理。
- 经纬度缺失或不可解析的行会被跳过。
- 数据为空时仍展示页面结构，并显示无可绘制数据提示。

## 交付物

- 源码：`app.py`
- 依赖：`requirements.txt`
- 测试：`tests/test_dashboard_data.py`
- 运行截图：`screenshots/`
- AI 交互日志：`AI_PROMPTS.md`

## Git Tag

基础关卡完成后：

```bash
git tag basic-done
git push origin basic-done
```

进阶关卡完成后：

```bash
git tag advanced-done
git push origin advanced-done
```
