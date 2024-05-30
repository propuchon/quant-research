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
    plot_volatility_by_hlo,
    transform_to_table,
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
fig = plot_volatility_by_hlo(
    data=data, title="(H-L / O) vs Close Price", x_label="Price", y_label="Percentage"
)
st.plotly_chart(fig)


def calculate_and_display_return_stats(data, timeframe, option, filter=False):
    # Calculate volatility based on the specified timeframe
    volatility = cal_voltility(data, timeframe=timeframe, method=Method[option]) * 100

    # Filter blackswan if required
    if filter:
        filtered_volatility = volatility[volatility < volatility.quantile(0.99)]
    else:
        filtered_volatility = volatility

    # Calculate basic statistics
    data_min, data_max, data_mean = cal_stats(data=filtered_volatility)
    stats = pd.DataFrame(
        [
            {"": "min", "%": data_min},
            {"": "max", "%": data_max},
            {"": "mean", "%": data_mean},
        ]
    )
    # Format the values with two decimal places
    stats["%"] = stats["%"].apply(lambda x: "{:.2f}".format(x))

    # Display basic statistics
    st.subheader(
        "Daily Volatility" if timeframe == TimeFrame.DAILY else "Annualized Volatility"
    )

    # Calculate and display annualized volatility
    df = transform_to_table(filtered_volatility)

    st.dataframe(data=df, use_container_width=True)
    st.dataframe(data=stats, hide_index=True, use_container_width=True)

    # Show removed outliers if filter is applied
    if filter:
        remove_indices = volatility.index.difference(filtered_volatility.index)
        st.write(f"\nRemove out of quantile 99%:")
        df = transform_to_table(volatility[remove_indices])
        st.dataframe(data=df, use_container_width=True)


st.title("Statistics")
col1, col2 = st.columns(2)
with col1:
    option = st.selectbox("Method", ("PERCENTAGE", "HLO"))
    filter = st.toggle("Filter Outlier (99%)")

col1, col2 = st.columns(2)
with col1:
    calculate_and_display_return_stats(
        data=data, timeframe=TimeFrame.DAILY, option=option, filter=filter
    )

with col2:
    calculate_and_display_return_stats(
        data=data, timeframe=TimeFrame.YEARLY, option=option, filter=filter
    )
