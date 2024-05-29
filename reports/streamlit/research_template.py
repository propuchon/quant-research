import pandas as pd
import streamlit as st
import plotly.graph_objs as go
from tvDatafeed import Interval, TvDatafeed
from utils import (
    Method,
    TimeFrame,
    cal_stats,
    cal_voltility,
    plot_close_prices_histogram,
    plot_close_prices_histogram_by_year,
    plot_close_prices_histogram_with_stdev,
)

interval = Interval.in_daily

st.title("🌟 Market Overview")

# ########################
# INPUT SECTION
# ########################
symbol = st.selectbox(
    "symbol",
    options=("XAUUSD", "BTCUSDT", "USOIL"),
)
exchange = st.text_input(label="Exchange", value="")

if exchange == "":
    exchange_mapping = {"XAUUSD": "OANDA", "BTCUSDT": "OKX", "USOIL": "TVC"}
    exchange = exchange_mapping[symbol]

tv = TvDatafeed()
data = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=10_000)

if not isinstance(data, pd.DataFrame):
    st.error("No data fetched from the data feed")
    exit()

col1, col2 = st.columns(2)
date_range = range(data.index.year[0], (data.index.year[-1] + 1))
with col1:
    start_year = st.selectbox("Start Year", date_range, index=len(date_range) - 4)
with col2:
    end_year = st.selectbox("End Year", date_range, index=len(date_range) - 1)

# Filter data
data = data[(data.index.year >= start_year) & (data.index.year <= end_year)]

if start_year > end_year:
    st.error('"Start Year" cannot be greater than "End Year".')
    exit()


st.text(f"Symbol: {symbol}, Exchange: {exchange}")

# ########################
# Distribution
# ########################
st.title("Distribution")

fig = plot_close_prices_histogram(
    data=data, title=f"{symbol} Price Distribution", x_label="Price", y_label=""
)
st.plotly_chart(fig)

with st.expander("Distribution by year"):
    fig = plot_close_prices_histogram_by_year(
        data=data, title=f"{symbol} Price Distribution", x_label="Price", y_label=""
    )
    st.pyplot(fig)

fig = plot_close_prices_histogram_with_stdev(
    data=data,
    title=f"{symbol} Price Distribution with STDEV",
    x_label="Price",
    y_label="",
)
st.plotly_chart(fig)


st.title("Volatility")
col1, col2 = st.columns(2)
with col1:
    option = st.selectbox("Method", ("PERCENTAGE", "HLO"))
    filter = st.toggle("Filter Outlier")

col1, col2 = st.columns(2)
with col1:
    daily_volatility = (
        cal_voltility(data, timeframe=TimeFrame.DAILY, method=Method[option]) * 100
    )

    if filter:
        # filter blackswan
        vol_data = daily_volatility[daily_volatility < daily_volatility.quantile(0.99)]
    else:
        vol_data = daily_volatility

    # ### BASIC STATS ###
    st.header("Daily Return")
    data_min, data_max, data_mean = cal_stats(data=vol_data)
    stats = pd.DataFrame(
        [
            {"": "min", "%": data_min},
            {"": "max", "%": data_max},
            {"": "mean", "%": data_mean},
        ]
    )
    st.dataframe(data=stats, hide_index=True, use_container_width=True)

    # ### ANNUALIZED ###
    annualized = pd.DataFrame(vol_data)
    annualized.rename(columns={"close": "%"}, inplace=True)
    annualized["%"] = annualized["%"].apply(lambda x: "{:.2f}".format(x))
    annualized.index.name = "year"
    annualized.index = annualized.index.astype(str)
    st.dataframe(data=annualized, use_container_width=True)

    # show remove outlier
    if filter:
        remove_indices = daily_volatility.index.difference(vol_data.index)
        st.write(f"\nRemove out of quantile 99%:")
        annualized = pd.DataFrame(daily_volatility[remove_indices])
        annualized.rename(columns={"close": "%"}, inplace=True)
        annualized["%"] = annualized["%"].apply(lambda x: "{:.2f}".format(x))
        annualized.index.name = "year"
        annualized.index = annualized.index.astype(str)
        st.dataframe(data=annualized, use_container_width=True)

with col2:
    annualized_volatility = (
        cal_voltility(data, timeframe=TimeFrame.YEARLY, method=Method[option]) * 100
    )

    # filter blackswan
    if filter:
        # filter blackswan
        vol_data = annualized_volatility[
            annualized_volatility < annualized_volatility.quantile(0.99)
        ]
    else:
        vol_data = annualized_volatility
    # ### BASIC STATS ###
    st.header("Yearly Return")
    data_min, data_max, data_mean = cal_stats(data=vol_data)
    stats = pd.DataFrame(
        [
            {"": "min", "%": data_min},
            {"": "max", "%": data_max},
            {"": "mean", "%": data_mean},
        ]
    )
    st.dataframe(data=stats, hide_index=True, use_container_width=True)

    # ### ANNUALIZED ###
    annualized = pd.DataFrame(vol_data)
    annualized.rename(columns={"close": "%"}, inplace=True)
    annualized["%"] = annualized["%"].apply(lambda x: "{:.2f}".format(x))
    annualized.index.name = "year"
    annualized.index = annualized.index.astype(str)
    st.dataframe(data=annualized, use_container_width=True)

    # show remove outlier
    if filter:
        remove_indices = annualized_volatility.index.difference(vol_data.index)
        st.write(f"\nRemove out of quantile 99%:")
        annualized = pd.DataFrame(annualized_volatility[remove_indices])
        annualized.rename(columns={"close": "%"}, inplace=True)
        annualized["%"] = annualized["%"].apply(lambda x: "{:.2f}".format(x))
        annualized.index.name = "year"
        annualized.index = annualized.index.astype(str)
        st.dataframe(data=annualized, use_container_width=True)
