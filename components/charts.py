"""WingStop Texas store sales chart — mock data + rendering."""

import numpy as np
import pandas as pd
import streamlit as st

# -- Seasonal multipliers (Jan=0 .. Dec=11) --
# Super Bowl bump in Feb, summer peak, football season lift
_SEASONAL = np.array([
    0.88,  # Jan — post-holiday dip
    1.12,  # Feb — Super Bowl
    0.96,  # Mar
    0.98,  # Apr
    1.05,  # May
    1.10,  # Jun — summer
    1.08,  # Jul
    1.06,  # Aug
    1.04,  # Sep — football starts
    1.07,  # Oct — football + fall
    1.02,  # Nov
    0.97,  # Dec — holidays
])

# Base monthly revenue per region (USD thousands)
_BASES = {
    "Dallas-Fort Worth": 115,
    "Houston": 95,
    "Austin": 72,
}

_ANNUAL_GROWTH = 0.06  # 6% YoY


def _build_data() -> pd.DataFrame:
    """Generate realistic monthly sales data, Jan 2023 to Jan 2026."""
    rng = np.random.default_rng(seed=42)
    months = pd.date_range("2023-01-01", "2026-01-01", freq="MS")

    records = {}
    for region, base in _BASES.items():
        values = []
        for dt in months:
            years_elapsed = (dt.year - 2023) + dt.month / 12
            growth = (1 + _ANNUAL_GROWTH) ** years_elapsed
            seasonal = _SEASONAL[dt.month - 1]
            noise = rng.normal(1.0, 0.03)  # +/- 3% random noise
            revenue = base * growth * seasonal * noise
            values.append(round(revenue, 1))
        records[region] = values

    df = pd.DataFrame(records, index=months)
    df.index.name = "Month"
    return df


def render() -> None:
    """Render the sales chart in a clean card-like container."""
    data = _build_data()

    st.markdown(
        '<p style="font-size:0.95rem; font-weight:600; margin:0 0 4px;">'
        "Texas Monthly Store Sales (USD K)"
        "</p>"
        '<p style="font-size:0.76rem; color:#86868B; margin:0 0 12px;">'
        "Jan 2023 -- Jan 2026 &middot; Mock data"
        "</p>",
        unsafe_allow_html=True,
    )

    tab_chart, tab_data = st.tabs(["Chart", "Data"])

    with tab_chart:
        st.line_chart(data, height=280, use_container_width=True)

    with tab_data:
        st.dataframe(
            data.style.format("{:.1f}"),
            height=280,
            use_container_width=True,
        )
