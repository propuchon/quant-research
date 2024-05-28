import streamlit as st
from tvDatafeed import Interval, TvDatafeed
from utils import plot_close_prices_histogram, plot_close_prices_histogram_with_stdev

interval = Interval.in_daily

st.title("🌟 Market Research 101")

# ########################
# INPUT SECTION
# ########################
symbol = st.selectbox(
    "symbol",
    options=("XAUUSD", "BTCUSDT", "USOIL"),
)
exchange_mapping = {"XAUUSD": "OANDA", "BTCUSDT": "OKX", "USOIL": "TVC"}
exchange = exchange_mapping[symbol]

tv = TvDatafeed()
data = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=10_000)

col1, col2 = st.columns(2)
with col1:
    start_year = st.selectbox(
        "Start Year", range(data.index.year[0], (data.index.year[-1] + 1))
    )
with col2:
    end_year = st.selectbox(
        "End Year", range(data.index.year[0], (data.index.year[-1] + 1))
    )

# Filter data
data = data[(data.index.year >= start_year) & (data.index.year <= end_year)]

if start_year > end_year:
    st.error('"Start Year" cannot be greater than "End Year".')

# ########################
# VISUALIZE
# ########################
fig = plot_close_prices_histogram(
    data=data, title=f"{symbol} Price Distribution", x_label="Price", y_label=""
)
st.plotly_chart(fig)

fig = plot_close_prices_histogram_with_stdev(
    data=data,
    title=f"{symbol} Price Distribution with STDEV",
    x_label="Price",
    y_label="",
)
st.plotly_chart(fig)
