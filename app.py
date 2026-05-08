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

    st.caption("优先渲染 WebGL 3D 柱；若当前浏览器禁用 WebGL，下方柱高图仍可校验同一份下载速率数据。")
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
                    range=["#00b450", "#ffbe28", "#ff7d23", "#dc2d2d"],
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
                    range=["#00b450", "#ffbe28", "#ff7d23", "#dc2d2d"],
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
                color=alt.Color("Band:N", legend=None),
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
                color=alt.Color("TerminalType:N", title="终端"),
                tooltip=["TerminalType", "Count"],
            ),
            width="stretch",
        )


def render_dashboard() -> None:
    st.set_page_config(page_title="5G 信号可视化看板", layout="wide")
    st.title("5G 信号可视化看板")
    st.caption("侧边栏筛选会实时联动 3D 地图、频段统计和终端占比。")

    data = load_signal_data(str(DATA_PATH))
    selected_bands, selected_terminals, rsrp_range = render_sidebar(data)
    filtered = filter_signal_data(data, selected_bands, selected_terminals, rsrp_range)
    summary = summarize_signal_data(filtered)

    metric_columns = st.columns(4)
    metric_columns[0].metric("信号点", summary["total_points"])
    metric_columns[1].metric("平均 RSRP", f"{summary['avg_rsrp']} dBm")
    metric_columns[2].metric("平均下载速率", f"{summary['avg_download']} Mbps")
    metric_columns[3].metric("弱覆盖点", summary["weak_points"])

    st.subheader("信号散点地图")
    render_signal_scatter_map(filtered)

    render_charts(filtered)

    st.subheader("3D 信号柱地图")
    render_3d_map(filtered)

    st.subheader("当前筛选数据")
    st.dataframe(filtered[DISPLAY_COLUMNS] if not filtered.empty else filtered)


if __name__ == "__main__":
    render_dashboard()
