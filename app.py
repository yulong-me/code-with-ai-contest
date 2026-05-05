import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
from data_processor import process_signal_data

# 设置页面配置
st.set_page_config(page_title="5G 信号可视化看板", layout="wide")

# 加载数据，使用 st.cache_data 进行缓存优化
@st.cache_data
def load_data():
    return process_signal_data("data/signal_samples.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"无法加载数据: {e}")
    st.stop()

# ==========================================
# 侧边栏联动筛选
# ==========================================
st.sidebar.header("🔍 数据筛选")

# 频段筛选下拉菜单
bands = ["全部"] + list(df['Band'].unique())
selected_band = st.sidebar.selectbox("选择频段 (Band)", bands)

# RSRP 筛选滑动条
min_rsrp = int(df['RSRP_dBm'].min())
max_rsrp = int(df['RSRP_dBm'].max())
selected_rsrp = st.sidebar.slider(
    "RSRP 范围 (dBm)", 
    min_value=min_rsrp, 
    max_value=max_rsrp, 
    value=(min_rsrp, max_rsrp)
)

# 动态过滤数据
filtered_df = df[
    (df['RSRP_dBm'] >= selected_rsrp[0]) & 
    (df['RSRP_dBm'] <= selected_rsrp[1])
]
if selected_band != "全部":
    filtered_df = filtered_df[filtered_df['Band'] == selected_band]

# ==========================================
# 主页面内容
# ==========================================
st.title("📡 5G 信号可视化看板")
st.markdown("**极客视觉体验：** 3D 信号热力与下载速率分布展示")

# --- 3D 地图渲染 ---
st.subheader("🗺️ 5G 信号 3D 地图")

if not filtered_df.empty:
    # 定义 PyDeck 3D柱状图层
    # 经纬度定位，高度为下载速率，颜色按 RSRP 区分
    layer = pdk.Layer(
        "ColumnLayer",
        data=filtered_df,
        get_position=["Longitude", "Latitude"],
        get_elevation="Download_Mbps",
        elevation_scale=5,
        radius=100,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )

    # 初始视图状态，自动聚焦到数据中心
    view_state = pdk.ViewState(
        longitude=filtered_df["Longitude"].mean(),
        latitude=filtered_df["Latitude"].mean(),
        zoom=11,
        pitch=45,
        bearing=0,
    )

    # 渲染地图
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "text": "CellID: {CellID}\nRSRP: {RSRP_dBm} dBm\n下载速率: {Download_Mbps} Mbps\n终端类型: {TerminalType}"
        },
    )
    st.pydeck_chart(r)
else:
    st.warning("当前筛选条件下无数据，请调整筛选范围。")

# --- 数据概览图表 ---
st.subheader("📊 数据概览")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**各频段基站数量分布**")
    if not filtered_df.empty:
        band_counts = filtered_df['Band'].value_counts()
        st.bar_chart(band_counts)
    else:
        st.info("无数据")

with col2:
    st.markdown("**不同类型终端分布比例**")
    if not filtered_df.empty:
        term_counts = filtered_df['TerminalType'].value_counts()
        st.bar_chart(term_counts)
    else:
        st.info("无数据")
