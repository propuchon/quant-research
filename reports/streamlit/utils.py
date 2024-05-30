from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go

from enum import Enum


# ########################
# ENUM
# ########################
class TimeFrame(Enum):
    DAILY = "daily"
    YEARLY = "yearly"


class Method(Enum):
    PERCENTAGE = "pct"
    HLO = "hlo"  # (high - low) / close


# ########################
# CALCULATION
# ########################
def cal_voltility(data: pd.DataFrame, timeframe=TimeFrame, method=Method) -> pd.Series:
    """
    Calculate the volatility of financial data.

    Parameters
    ----------
    data : pd.DataFrame
        A DataFrame containing financial data, including columns for 'open', 'high', 'low', and 'close'.
    timeframe : TimeFrame, optional
        The timeframe over which to calculate volatility, either TimeFrame.DAILY or TimeFrame.YEARLY.
        Defaults to TimeFrame.DAILY.
    method : Method, optional
        The method to use for calculating volatility, either Method.PERCENTAGE or Method.HLO.
        Defaults to Method.PERCENTAGE.

    Returns
    -------
    pd.Series
        A pandas Series containing the calculated volatility.

    Raises
    ------
    ValueError
        If an invalid method is provided.
    """

    def _cal_method(data: pd.Series):
        return (
            data.groupby(data.index.year).std()
            if timeframe == TimeFrame.DAILY
            else data.groupby(data.index.year).std() * np.sqrt(252)
        )

    if method == Method.PERCENTAGE:
        volatility = data["close"].pct_change()
        return _cal_method(data=volatility)
    elif method == method.HLO:
        volatility = (data["high"] - data["low"]) / data["open"]
        return _cal_method(data=volatility)
    else:
        raise ValueError("Not found method!")


def cal_stats(data: pd.Series):
    """Calculate the min max and mean from the series data which normalized as percentage"""
    data_min = round(data.min(), 2)
    data_max = round(data.max(), 2)
    data_mean = round(data.mean(), 2)

    # # Output
    # print(f"min: {data_min}%\nmax: {data_max}%\nmean: {data_mean}%")

    return data_min, data_max, data_mean


def _cal_stdev(
    mean: float, std: float
) -> tuple[float, float, float, float, float, float]:
    stdev_pos_1 = mean + std
    stdev_neg_1 = mean - std
    stdev_pos_2 = mean + 2 * std
    stdev_neg_2 = mean - 2 * std
    stdev_pos_3 = mean + 3 * std
    stdev_neg_3 = mean - 3 * std

    return stdev_pos_1, stdev_neg_1, stdev_pos_2, stdev_neg_2, stdev_pos_3, stdev_neg_3


# ########################
# TRANSFORM SERIES TO TABLE
# ########################
def transform_to_table(data: pd.Series) -> pd.DataFrame:
    """Transform stats table which index is datetime and values is percentage"""
    df = pd.DataFrame(data)
    df.rename(columns={"close": "%"}, inplace=True)
    df["%"] = df["%"].apply(lambda x: "{:.2f}".format(x))
    df.index.name = "year"
    df.index = df.index.astype(str)

    return df


# ########################
# PLOT
# ########################
def plot_close_prices_histogram(
    data: pd.DataFrame,
    title=None,
    x_label="Closing Price",
    y_label="Frequency",
    grid=True,
):
    """Plot the close price histogram using Plotly"""
    # Check if DataFrame index is of datetime type
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be of datetime type")

    # Creating the histogram
    fig = px.histogram(
        data,
        x="close",
        nbins=50,
        title=title
        or f"Histogram of Closing Prices from {data.index.year[0]} to {data.index.year[-1]}",
    )

    # Updating layout for customization
    last_close_price = data["close"].iloc[-1]
    fig.add_trace(
        go.Scatter(
            x=[last_close_price],
            y=[0],
            mode="markers+text",
            text=[f"Last Price: {last_close_price:.2f}"],
            textposition="top center",
            marker=dict(color="green", size=10),
            name="Last Price",
        )
    )

    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        showlegend=False,
        hovermode="x unified",
    )

    if grid:
        fig.update_xaxes(showgrid=True)
        fig.update_yaxes(showgrid=True)
    else:
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)

    return fig


def plot_close_prices_histogram_by_year(
    data: pd.DataFrame,
    title=None,
    x_label="Closing Price",
    y_label="Frequency",
    grid=True,
):
    """Plot the close price histogram by year"""
    # Check if DataFrame index is of datetime type
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be of datetime type")

    # Group data by year
    grouped_data = data.groupby(data.index.year)

    # Create the plot
    plt.figure(figsize=(10, 6))
    for year, year_data in grouped_data:
        plt.hist(year_data["close"], bins=50, alpha=0.7, label=str(year))

    # Customization
    if title:
        plt.title(title)
    else:
        plt.title(
            f"Histogram of Closing Prices by Year from {data.index.year[0]} to {data.index.year[-1]}"
        )
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    if grid:
        plt.grid(True)
    plt.legend(title="Year")

    return plt


def plot_close_prices_histogram_with_stdev(
    data: pd.DataFrame,
    title=None,
    x_label="Closing Price",
    y_label="Frequency",
    grid=True,
):
    """Plot the close price histogram with standard deviation lines using Plotly"""
    # Check if DataFrame index is of datetime type
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be of datetime type")

    mean = data["close"].mean()
    std = data["close"].std()
    stdev_pos_1, stdev_neg_1, stdev_pos_2, stdev_neg_2, stdev_pos_3, stdev_neg_3 = (
        _cal_stdev(mean=mean, std=std)
    )

    # Creating the histogram
    fig = px.histogram(
        data,
        x="close",
        nbins=50,
        title=title
        or f"Histogram of Closing Prices from {data.index.year[0]} to {data.index.year[-1]}",
    )

    # Adding vertical lines for mean and SD ranges
    lines = [
        {"x": mean, "color": "white", "dash": "solid", "name": "Mean"},
        {"x": stdev_pos_1, "color": "coral", "dash": "dash", "name": "Mean + 1SD"},
        {"x": stdev_neg_1, "color": "coral", "dash": "dash", "name": "Mean - 1SD"},
        {"x": stdev_pos_2, "color": "cadetblue", "dash": "dash", "name": "Mean + 2SD"},
        {"x": stdev_neg_2, "color": "cadetblue", "dash": "dash", "name": "Mean - 2SD"},
        {"x": stdev_pos_3, "color": "crimson", "dash": "dash", "name": "Mean + 3SD"},
        {"x": stdev_neg_3, "color": "crimson", "dash": "dash", "name": "Mean - 3SD"},
    ]

    for line in lines:
        fig.add_shape(
            type="line",
            x0=line["x"],
            x1=line["x"],
            y0=0,
            y1=1,
            xref="x",
            yref="paper",
            line=dict(color=line["color"], width=2, dash=line["dash"]),
            name=line["name"],
        )

    # Adding annotations for each line
    for line in lines:
        fig.add_annotation(
            x=line["x"],
            y=1.05,
            yanchor="top",
            text=line["name"],
            showarrow=False,
            font=dict(color=line["color"]),
            xanchor="left" if "neg" in line["name"] else "right",
        )

    # Updating layout for customization
    last_close_price = data["close"].iloc[-1]
    fig.add_trace(
        go.Scatter(
            x=[last_close_price],
            y=[0],
            mode="markers+text",
            text=[f"Last Price: {last_close_price:.2f}"],
            textposition="top center",
            marker=dict(color="green", size=10),
            name="Last Price",
        )
    )

    # Updating layout for customization
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        showlegend=False,
        hovermode="x unified",
    )

    if grid:
        fig.update_xaxes(showgrid=True)
        fig.update_yaxes(showgrid=True)
    else:
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)

    return fig


def plot_volatility_by_hlo(
    data: pd.DataFrame,
    title=None,
    x_label="Closing Price",
    y_label="Frequency",
    grid=True,
):
    data["%"] = ((data["high"] - data["low"]) / data["open"]) * 100

    # Create the scatter plot with Plotly
    fig = px.scatter(
        data,
        x="close",
        y="%",
        title="(High - Low) / Open vs Closing Price",
        opacity=0.5,
    )

    # Updating layout for customization
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        showlegend=False,
        hovermode="x unified",
    )

    if grid:
        fig.update_xaxes(showgrid=True)
        fig.update_yaxes(showgrid=True)
    else:
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)

    return fig
