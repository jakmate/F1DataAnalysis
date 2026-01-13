import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from utils import get_constructor_colours, format_minutes
from matplotlib.ticker import FuncFormatter

# Define colors for constructors
constructor_colors = get_constructor_colours()


def plot_lap_times_boxplot(data):
    """Plot a boxplot of lap times for the Bahrain Grand Prix."""
    plt.style.use("dark_background")
    plt.figure(figsize=(10, 6))
    sns.boxplot(
        x="code",
        y="timeMinutes",
        hue="constructor",
        data=data,
        palette=constructor_colors,
    )
    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_minutes))
    plt.xlabel("Driver Code")
    plt.ylabel("Lap Time (minutes)")
    plt.title("Lap Times for Bahrain Grand Prix (2024)")
    plt.show()


def plot_std_dev_lap_times(stats, constructor_colors):
    """Plot standard deviation of lap times by driver."""
    unique_teams = stats["constructor"].unique()
    for team in unique_teams:
        if team not in constructor_colors:
            constructor_colors[team] = "gray"

    plot_data = stats[
        ["firstName", "lastName", "constructor", "adjustedStd"]
    ].reset_index()
    plot_data = plot_data.melt(
        id_vars=["firstName", "lastName", "constructor"],
        value_vars=["adjustedStd"],
        var_name="Scenario",
        value_name="Standard Deviation",
    )

    plot_data["Standard Deviation (s)"] = plot_data["Standard Deviation"] / 1000
    plot_data_sorted = plot_data.sort_values(by="Standard Deviation (s)")

    drivers = plot_data_sorted["lastName"].unique()
    x = np.arange(len(drivers))
    bar_width = 0.8

    _, ax = plt.subplots(figsize=(16, 10))
    _ = ax.bar(
        x,
        plot_data_sorted["Standard Deviation (s)"],
        color=plot_data_sorted["constructor"].map(constructor_colors),
        width=bar_width,
        align="center",
    )

    ax.set_xlabel("Driver")
    ax.set_ylabel("Standard Deviation (seconds)")
    ax.set_title("Standard Deviation of Lap Times by Driver")
    ax.set_xticks(x)
    ax.set_xticklabels(drivers, rotation=90)
    ax.set_xlim(-bar_width, len(drivers) - 1 + bar_width)

    handles = [
        plt.Line2D([0], [0], color=color, lw=4) for color in constructor_colors.values()
    ]
    labels = list(constructor_colors.keys())
    ax.legend(
        handles, labels, title="Constructor", bbox_to_anchor=(1.05, 1), loc="upper left"
    )

    plt.tight_layout()
    plt.show()


def plot_mean_lap_times(stats, constructor_colors):
    """Plot average difference in lap times by driver."""
    plot_data = stats[
        ["firstName", "lastName", "constructor", "adjustedMean"]
    ].reset_index()
    plot_data = plot_data.melt(
        id_vars=["firstName", "lastName", "constructor"],
        value_vars=["adjustedMean"],
        var_name="Scenario",
        value_name="Mean",
    )

    plot_data_sorted = plot_data.sort_values(by="Mean")
    plot_data_sorted["DifFromFastest"] = (
        plot_data_sorted["Mean"] - plot_data_sorted["Mean"].min()
    ) / 6000

    drivers = plot_data_sorted["lastName"].unique()
    x = np.arange(len(drivers))
    bar_width = 0.8

    _, ax = plt.subplots(figsize=(16, 10))
    _ = ax.bar(
        x,
        plot_data_sorted["DifFromFastest"],
        color=plot_data_sorted["constructor"].map(constructor_colors),
        width=bar_width,
        align="center",
    )

    ax.set_xlabel("Driver")
    ax.set_ylabel("+ from quickest car (s)")
    ax.set_title("Average Difference in Lap Times by Drivers")
    ax.set_xticks(x)
    ax.set_xticklabels(drivers, rotation=90)
    ax.set_xlim(-bar_width, len(drivers) - 1 + bar_width)

    handles = [
        plt.Line2D([0], [0], color=color, lw=4) for color in constructor_colors.values()
    ]
    labels = list(constructor_colors.keys())
    ax.legend(
        handles, labels, title="Constructor", bbox_to_anchor=(1.05, 1), loc="upper left"
    )

    plt.tight_layout()
    plt.show()
