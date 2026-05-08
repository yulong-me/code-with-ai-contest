from pathlib import Path

import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st


DATA_PATH = Path("data/signal_samples.csv")

REQUIRED_COLUMNS = {
    "Latitude": pd.NA,
    "Longitude": pd.NA,
    "CellID": "Unknown",
    "Band": "Unknown",
    "RSRP_dBm": -120,
    "SINR_dB": 0,
    "TerminalType": "Unknown",
    "Download_Mbps": 0,
}

DISPLAY_COLUMNS = [
    "CellID",
    "Band",
    "TerminalType",
    "RSRP_dBm",
    "SINR_dB",
    "Download_Mbps",
    "SignalQuality",
]

QUALITY_DOMAIN = ["Excellent", "Good", "Fair", "Weak"]
QUALITY_RANGE = ["#10b981", "#f6c343", "#fb923c", "#ef4444"]
BAND_RANGE = ["#2563eb", "#38bdf8", "#f97316", "#7c3aed", "#14b8a6"]
TERMINAL_RANGE = ["#2563eb", "#38bdf8", "#ef4444", "#10b981", "#a855f7"]

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@400;500;600;700&display=swap');

:root {
    --bg: #f6f8fb;
    --panel: #ffffff;
    --ink: #172033;
    --muted: #667085;
    --line: #dbe3ef;
    --blue: #2563eb;
    --cyan: #0ea5e9;
    --amber: #f59e0b;
    --red: #ef4444;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(37, 99, 235, 0.10), transparent 34rem),
        linear-gradient(180deg, #f8fbff 0%, var(--bg) 42%, #ffffff 100%);
    color: var(--ink);
    font-family: "Fira Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

[data-testid="stSidebar"] {
    background: #eef3f9;
    border-right: 1px solid var(--line);
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label {
    color: #1d2939;
    font-weight: 700;
}

.block-container {
    max-width: 1180px;
    padding-top: 2.2rem;
}

.signal-hero {
    border: 1px solid rgba(37, 99, 235, 0.18);
    border-radius: 8px;
    background:
        linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(14, 165, 233, 0.05)),
        #ffffff;
    padding: 1.45rem 1.6rem 1.25rem;
    margin-bottom: 1.2rem;
}

.signal-eyebrow {
    color: var(--blue);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

.signal-hero h1 {
    color: var(--ink);
    font-size: clamp(2.15rem, 4vw, 3.25rem);
    line-height: 1.05;
    letter-spacing: 0;
    margin: 0;
}

.signal-hero p {
    max-width: 720px;
    color: var(--muted);
    font-size: 1rem;
    margin: 0.65rem 0 0;
}

.metric-card {
    min-height: 112px;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.92);
    padding: 1rem 1.05rem;
    box-shadow: 0 12px 24px rgba(15, 23, 42, 0.05);
}

.metric-label {
    color: var(--muted);
    font-size: 0.82rem;
    font-weight: 700;
    margin-bottom: 0.35rem;
}

.metric-value {
    color: var(--ink);
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.1;
}

.metric-note {
    color: var(--muted);
    font-size: 0.78rem;
    margin-top: 0.35rem;
}

.section-title {
    margin-top: 1.9rem;
    margin-bottom: 0.55rem;
    color: var(--ink);
    font-size: 1.45rem;
    font-weight: 700;
}

.quality-strip {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.75rem;
    margin: 1rem 0 0.4rem;
}

.quality-pill {
    border: 1px solid var(--line);
    border-radius: 8px;
    background: #ffffff;
    padding: 0.75rem 0.85rem;
}

.quality-pill span {
    display: block;
    color: var(--muted);
    font-size: 0.78rem;
    font-weight: 700;
}

.quality-pill strong {
    color: var(--ink);
    display: block;
    font-size: 1.45rem;
    line-height: 1.15;
}

.quality-excellent { border-top: 4px solid #10b981; }
.quality-good { border-top: 4px solid #f6c343; }
.quality-fair { border-top: 4px solid #fb923c; }
.quality-weak { border-top: 4px solid #ef4444; }

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 0.9rem 1rem;
}

@media (max-width: 760px) {
    .block-container { padding-top: 3.2rem; }
    .signal-hero { padding: 1.1rem; }
    .signal-hero h1 { font-size: 2.25rem; }
    .quality-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .metric-card { min-height: auto; }
}
</style>
"""


def classify_signal(rsrp: float) -> str:
    if rsrp > -90:
        return "Excellent"
    if rsrp > -105:
        return "Good"
    if rsrp >= -110:
        return "Fair"
    return "Weak"


def signal_color(rsrp: float) -> list[int]:
    if rsrp > -90:
        return [0, 180, 80, 190]
    if rsrp > -105:
        return [255, 190, 40, 190]
    if rsrp >= -110:
        return [255, 125, 35, 190]
    return [220, 45, 45, 190]


def empty_signal_frame() -> pd.DataFrame:
    columns = list(REQUIRED_COLUMNS) + ["SignalQuality", "Color", "Tooltip"]
    return pd.DataFrame(columns=columns)


def prepare_signal_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Normalize contest CSV data so the dashboard keeps running on dirty input."""
    if raw_data is None or raw_data.empty:
        return empty_signal_frame()

    data = raw_data.copy()
    for column, default in REQUIRED_COLUMNS.items():
        if column not in data.columns:
            data[column] = default

    for column in ["Latitude", "Longitude", "RSRP_dBm", "SINR_dB", "Download_Mbps"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=["Latitude", "Longitude"]).copy()
    if data.empty:
        return empty_signal_frame()

    data["RSRP_dBm"] = data["RSRP_dBm"].fillna(-120).clip(-140, -40).round(2)
    data["SINR_dB"] = data["SINR_dB"].fillna(0).round(2)
    data["Download_Mbps"] = data["Download_Mbps"].fillna(0).clip(lower=0).round(2)

    for column in ["CellID", "Band", "TerminalType"]:
        data[column] = data[column].fillna("Unknown").astype(str).replace("", "Unknown")

    data["SignalQuality"] = data["RSRP_dBm"].apply(classify_signal)
    data["Color"] = data["RSRP_dBm"].apply(signal_color)
    data["Tooltip"] = data.apply(
        lambda row: (
            f"Cell {row['CellID']} | {row['Band']} | "
            f"{row['RSRP_dBm']} dBm | {row['Download_Mbps']} Mbps"
        ),
        axis=1,
    )
    return data


def filter_signal_data(
    data: pd.DataFrame,
    selected_bands: list[str] | None,
    selected_terminals: list[str] | None,
    rsrp_range: tuple[float, float],
) -> pd.DataFrame:
    if data.empty:
        return data.copy()

    filtered = data.copy()
    if selected_bands:
        filtered = filtered[filtered["Band"].isin(selected_bands)]
    if selected_terminals:
        filtered = filtered[filtered["TerminalType"].isin(selected_terminals)]

    min_rsrp, max_rsrp = rsrp_range
    return filtered[
        (filtered["RSRP_dBm"] >= min_rsrp) & (filtered["RSRP_dBm"] <= max_rsrp)
    ].copy()


def summarize_signal_data(data: pd.DataFrame) -> dict[str, float]:
    if data.empty:
        return {"total_points": 0, "avg_rsrp": 0, "avg_download": 0, "weak_points": 0}

    return {
        "total_points": int(len(data)),
        "avg_rsrp": round(float(data["RSRP_dBm"].mean()), 2),
        "avg_download": round(float(data["Download_Mbps"].mean()), 2),
        "weak_points": int((data["RSRP_dBm"] < -110).sum()),
    }


def summarize_quality_counts(data: pd.DataFrame) -> dict[str, int]:
    counts = data["SignalQuality"].value_counts().to_dict() if not data.empty else {}
    return {quality: int(counts.get(quality, 0)) for quality in QUALITY_DOMAIN}


@st.cache_data
def load_signal_data(path: str) -> pd.DataFrame:
    try:
        return prepare_signal_data(pd.read_csv(path))
    except FileNotFoundError:
        return empty_signal_frame()
    except pd.errors.EmptyDataError:
        return empty_signal_frame()


def render_sidebar(data: pd.DataFrame) -> tuple[list[str], list[str], tuple[float, float]]:
    st.sidebar.header("筛选")
    st.sidebar.caption("筛选会同步刷新地图、统计图和数据表。")

    if data.empty:
        st.sidebar.info("当前没有可用信号点，筛选器已使用安全默认值。")
        return [], [], (-140, -40)

    bands = sorted(data["Band"].dropna().unique().tolist())
    terminals = sorted(data["TerminalType"].dropna().unique().tolist())
    min_rsrp = int(data["RSRP_dBm"].min())
    max_rsrp = int(data["RSRP_dBm"].max())

    selected_bands = st.sidebar.multiselect("频段 Band", bands, default=bands)
    selected_terminals = st.sidebar.multiselect(
        "终端类型", terminals, default=terminals
    )
    rsrp_range = st.sidebar.slider(
        "RSRP 范围 (dBm)",
        min_value=min_rsrp,
        max_value=max_rsrp,
        value=(min_rsrp, max_rsrp),
    )
    return selected_bands, selected_terminals, rsrp_range


def render_3d_map(data: pd.DataFrame) -> None:
    if data.empty:
        st.warning("没有可绘制的经纬度数据。请检查 CSV 是否为空或字段是否缺失。")
        return

    st.caption("下方柱高图与 WebGL 3D 柱使用同一份下载速率数据，用于稳定呈现柱高关系。")
    render_column_fallback(data)

    midpoint = [float(data["Longitude"].mean()), float(data["Latitude"].mean())]
    layer = pdk.Layer(
        "ColumnLayer",
        data=data,
        get_position="[Longitude, Latitude]",
        get_elevation="Download_Mbps",
        elevation_scale=45,
        radius=260,
        extruded=True,
        coverage=0.9,
        get_fill_color="Color",
        pickable=True,
        auto_highlight=True,
    )
    view_state = pdk.ViewState(
        longitude=midpoint[0],
        latitude=midpoint[1],
        zoom=11,
        pitch=48,
        bearing=-18,
    )
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{Tooltip}"},
            map_style=pdk.map_styles.CARTO_LIGHT,
        ),
        width="stretch",
        height=500,
    )


def render_column_fallback(data: pd.DataFrame) -> None:
    top_cells = data.nlargest(24, "Download_Mbps").copy()
    if top_cells.empty:
        return

    st.altair_chart(
        alt.Chart(top_cells)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("CellID:N", title="Cell ID", sort="-y"),
            y=alt.Y("Download_Mbps:Q", title="柱高 / 下载速率 Mbps"),
            color=alt.Color(
                "SignalQuality:N",
                title="RSRP",
                scale=alt.Scale(
                    domain=["Excellent", "Good", "Fair", "Weak"],
                    range=QUALITY_RANGE,
                ),
            ),
            tooltip=DISPLAY_COLUMNS,
        )
        .properties(height=260),
        width="stretch",
    )


def render_signal_scatter_map(data: pd.DataFrame) -> None:
    if data.empty:
        st.warning("没有可绘制的经纬度数据。请检查 CSV 是否为空或字段是否缺失。")
        return

    st.altair_chart(
        alt.Chart(data)
        .mark_circle(opacity=0.78, stroke="white", strokeWidth=0.4)
        .encode(
            x=alt.X("Longitude:Q", title="Longitude", scale=alt.Scale(zero=False)),
            y=alt.Y("Latitude:Q", title="Latitude", scale=alt.Scale(zero=False)),
            size=alt.Size(
                "Download_Mbps:Q",
                title="Download Mbps",
                scale=alt.Scale(range=[40, 420]),
            ),
            color=alt.Color(
                "SignalQuality:N",
                title="RSRP",
                scale=alt.Scale(
                    domain=["Excellent", "Good", "Fair", "Weak"],
                    range=QUALITY_RANGE,
                ),
            ),
            tooltip=DISPLAY_COLUMNS,
        )
        .properties(height=420),
        width="stretch",
    )


def render_charts(data: pd.DataFrame) -> None:
    if data.empty:
        st.info("暂无统计图表数据。")
        return

    left, right = st.columns(2)
    band_counts = data.groupby("Band", as_index=False).agg(Count=("CellID", "count"))
    terminal_counts = data.groupby("TerminalType", as_index=False).agg(
        Count=("CellID", "count")
    )

    with left:
        st.subheader("各频段基站数量")
        st.altair_chart(
            alt.Chart(band_counts)
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(
                x=alt.X("Band:N", title="Band"),
                y=alt.Y("Count:Q", title="数量"),
                color=alt.Color(
                    "Band:N",
                    legend=None,
                    scale=alt.Scale(range=BAND_RANGE),
                ),
                tooltip=["Band", "Count"],
            ),
            width="stretch",
        )

    with right:
        st.subheader("终端类型占比")
        st.altair_chart(
            alt.Chart(terminal_counts)
            .mark_arc(innerRadius=45)
            .encode(
                theta=alt.Theta("Count:Q"),
                color=alt.Color(
                    "TerminalType:N",
                    title="终端",
                    scale=alt.Scale(range=TERMINAL_RANGE),
                ),
                tooltip=["TerminalType", "Count"],
            ),
            width="stretch",
        )


def render_page_chrome() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)


def render_hero() -> None:
    st.markdown(
        """
        <section class="signal-hero">
            <div class="signal-eyebrow">5G FIELD INTELLIGENCE</div>
            <h1>5G 信号可视化看板</h1>
            <p>面向路测数据复盘的本地看板，聚合信号强度、终端类型、下载速率和弱覆盖点，侧边栏筛选实时联动全部视图。</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_grid(summary: dict[str, float]) -> None:
    columns = st.columns(4)
    metrics = [
        ("信号点", f"{summary['total_points']}", "当前筛选样本"),
        ("平均 RSRP", f"{summary['avg_rsrp']} dBm", "越接近 0 越强"),
        ("平均下载速率", f"{summary['avg_download']} Mbps", "柱高映射字段"),
        ("弱覆盖点", f"{summary['weak_points']}", "RSRP < -110 dBm"),
    ]
    for column, metric in zip(columns, metrics):
        with column:
            render_metric_card(*metric)


def render_quality_strip(counts: dict[str, int]) -> None:
    st.markdown(
        f"""
        <div class="quality-strip">
            <div class="quality-pill quality-excellent"><span>Excellent</span><strong>{counts['Excellent']}</strong></div>
            <div class="quality-pill quality-good"><span>Good</span><strong>{counts['Good']}</strong></div>
            <div class="quality-pill quality-fair"><span>Fair</span><strong>{counts['Fair']}</strong></div>
            <div class="quality-pill quality-weak"><span>Weak</span><strong>{counts['Weak']}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def render_dashboard() -> None:
    st.set_page_config(page_title="5G 信号可视化看板", layout="wide")
    render_page_chrome()
    render_hero()

    data = load_signal_data(str(DATA_PATH))
    selected_bands, selected_terminals, rsrp_range = render_sidebar(data)
    filtered = filter_signal_data(data, selected_bands, selected_terminals, rsrp_range)
    summary = summarize_signal_data(filtered)
    quality_counts = summarize_quality_counts(filtered)

    render_metric_grid(summary)
    render_quality_strip(quality_counts)

    section_title("信号散点地图")
    render_signal_scatter_map(filtered)

    render_charts(filtered)

    section_title("3D 信号柱地图")
    render_3d_map(filtered)

    section_title("当前筛选数据")
    st.dataframe(filtered[DISPLAY_COLUMNS] if not filtered.empty else filtered)


if __name__ == "__main__":
    render_dashboard()
