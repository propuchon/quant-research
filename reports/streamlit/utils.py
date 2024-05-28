import pandas as pd
import plotly.express as px


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
    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label, showlegend=False)

    if grid:
        fig.update_xaxes(showgrid=True)
        fig.update_yaxes(showgrid=True)
    else:
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)

    return fig


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
        {"x": mean, "color": "blue", "dash": "solid", "name": "Mean"},
        {"x": stdev_pos_1, "color": "blue", "dash": "dash", "name": "Mean + 1SD"},
        {"x": stdev_neg_1, "color": "blue", "dash": "dash", "name": "Mean - 1SD"},
        {"x": stdev_pos_2, "color": "green", "dash": "dash", "name": "Mean + 2SD"},
        {"x": stdev_neg_2, "color": "green", "dash": "dash", "name": "Mean - 2SD"},
        {"x": stdev_pos_3, "color": "red", "dash": "dash", "name": "Mean + 3SD"},
        {"x": stdev_neg_3, "color": "red", "dash": "dash", "name": "Mean - 3SD"},
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
            y=0,
            yanchor="bottom",
            text=line["name"],
            showarrow=False,
            font=dict(color=line["color"]),
            xanchor="left" if "neg" in line["name"] else "right",
        )

    # Updating layout for customization
    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label, showlegend=False)

    if grid:
        fig.update_xaxes(showgrid=True)
        fig.update_yaxes(showgrid=True)
    else:
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)

    return fig
