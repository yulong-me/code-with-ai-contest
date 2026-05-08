# Agent 交互日志

**团队名称：** show me your prompt
**成员名单：** 郑玉龙、杨玉云、王瑞昕
**使用的 AI Coding Agent 工具：** OpenAI Codex

> 说明：以下记录为本次实现过程中围绕比赛仓库的真实 Agent 协作摘要。

## 交互记录

### 1. 任务启动

**用户提示：**

> `https://github.com/besa-2026/code-with-ai-contest.git 参赛`

**Agent 响应要点：**

- 核对仓库 README 中的比赛要求。
- 确认必须交付本地 Python Web 看板、`README.md`、截图、`AI_PROMPTS.md`。
- 将目标收敛为尽快完成 `advanced-done`：RSRP 变色地图、频段/终端统计、侧栏筛选联动、3D pydeck 柱和单元测试。

### 2. 架构评审

**挑战架构师结论：**

> 架构结论：通过
>
> 保留风险：必须把数据字段缺失/空数据路径做成可运行降级，否则截图、`advanced-done` tag 和 README 会被一个脏样本同时卡死。

### 3. TDD 实现

**实现指令：**

> 请据此实现，完成后提交 Reviewer 审查。

**Agent 执行动作：**

- 克隆比赛仓库到独立工作区。
- 先新增 `tests/test_dashboard_data.py`，覆盖缺字段、脏数值、空数据和组合筛选。
- 首次运行测试失败，原因是模板 `app.py` 没有可导入的数据处理函数。
- 重写 `app.py`，拆出 `prepare_signal_data()`、`filter_signal_data()`、`summarize_signal_data()` 等函数。
- 保留 Streamlit 页面入口，并增加侧边栏筛选、截图友好的经纬度散点地图、3D pydeck 地图、WebGL 不可用时的同数据源柱高降级图、Altair 统计图和数据表。
- 增加 `.gitignore`，避免提交虚拟环境和缓存。

### 4. 验证

**执行命令：**

```bash
.venv/bin/python -m pytest tests/test_dashboard_data.py
```

**结果：**

```text
3 passed
```

**执行命令：**

```bash
.venv/bin/streamlit run app.py
```

**结果：**

看板可在本地浏览器打开，并用于生成 `screenshots/` 下的运行截图。

### 5. 视觉门禁补充

**发现：**

Headless 浏览器截图时 deck.gl 报 WebGL context 相关错误，`3D 信号柱地图` 区域可能空白。

**处理：**

- 保留 pydeck `ColumnLayer` 作为进阶关卡 3D 实现。
- 在同一 3D 区块增加同数据源的柱高降级图，确保 WebGL 不可用时截图仍能验证柱高、RSRP 颜色和筛选数据。
- 重新生成 `screenshots/dashboard-full.png` 作为运行证据。

### 6. UI/UX 强化

**用户提示：**

> `UI UX pro max. 优化下界面，优化完重新打tag`

**Agent 执行动作：**

- 使用 UI/UX 设计检索生成数据看板方向：专业、技术感、强层级、响应式。
- 增加页面 Hero、KPI 卡片、信号质量分布条、统一图表配色和移动端安全间距。
- 为信号质量分布补充单元测试。
- 重新生成 `screenshots/dashboard-main.png`、`screenshots/dashboard-mobile.png`、`screenshots/dashboard-full.png`。
