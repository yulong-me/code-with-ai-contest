import pandas as pd

from app import (
    filter_signal_data,
    prepare_signal_data,
    summarize_quality_counts,
    summarize_signal_data,
)


def test_prepare_signal_data_handles_missing_columns_and_dirty_values():
    raw = pd.DataFrame(
        {
            "Latitude": [31.2, "bad"],
            "Longitude": [121.4, 121.5],
            "RSRP_dBm": ["-85", None],
        }
    )

    cleaned = prepare_signal_data(raw)

    assert len(cleaned) == 1
    row = cleaned.iloc[0]
    assert row["Band"] == "Unknown"
    assert row["TerminalType"] == "Unknown"
    assert row["CellID"] == "Unknown"
    assert row["Download_Mbps"] == 0
    assert row["SignalQuality"] == "Excellent"
    assert row["Color"] == [0, 180, 80, 190]


def test_prepare_signal_data_returns_stable_empty_schema():
    cleaned = prepare_signal_data(pd.DataFrame())
    summary = summarize_signal_data(cleaned)

    assert cleaned.empty
    assert {"Latitude", "Longitude", "Band", "RSRP_dBm", "Download_Mbps"}.issubset(
        cleaned.columns
    )
    assert summary["total_points"] == 0
    assert summary["avg_rsrp"] == 0
    assert summary["avg_download"] == 0


def test_filter_signal_data_combines_band_terminal_and_rsrp_filters():
    raw = pd.DataFrame(
        {
            "Latitude": [31.2, 31.3, 31.4],
            "Longitude": [121.4, 121.5, 121.6],
            "CellID": [1001, 1002, 1003],
            "Band": ["n78", "n41", "n78"],
            "RSRP_dBm": [-85, -115, -100],
            "SINR_dB": [12, 8, 18],
            "TerminalType": ["Smartphone", "CPE", "CPE"],
            "Download_Mbps": [500, 100, 700],
        }
    )
    cleaned = prepare_signal_data(raw)

    filtered = filter_signal_data(
        cleaned,
        selected_bands=["n78"],
        selected_terminals=["CPE"],
        rsrp_range=(-110, -90),
    )

    assert filtered["CellID"].tolist() == ["1003"]


def test_summarize_quality_counts_returns_all_quality_buckets():
    raw = pd.DataFrame(
        {
            "Latitude": [31.2, 31.3, 31.4, 31.5],
            "Longitude": [121.4, 121.5, 121.6, 121.7],
            "RSRP_dBm": [-80, -100, -108, -120],
        }
    )

    counts = summarize_quality_counts(prepare_signal_data(raw))

    assert counts == {"Excellent": 1, "Good": 1, "Fair": 1, "Weak": 1}
