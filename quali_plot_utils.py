import matplotlib.pyplot as plt


def plot_quali_drivers(quali_data):
    """Plot time differences by driver."""
    plt.style.use("dark_background")
    plt.figure(figsize=(12, 8))

    # Plot driver time differences
    plt.barh(
        quali_data["Driver_code"], quali_data["timeDiff"], color=quali_data["color"]
    )

    # Create the legend based on the unique teams in the qualifying data
    unique_teams = quali_data["Constructor_name"].unique()

    # Map the unique team names to their respective colors
    legend_handles = [
        plt.Line2D(
            [0],
            [0],
            color=quali_data[quali_data["Constructor_name"] == team]["color"].iloc[0],
            lw=4,
        )
        for team in unique_teams
    ]
    plt.legend(legend_handles, unique_teams, title="Constructor")

    # Add axis labels and title
    plt.xlabel("Time Difference from Fastest (seconds)")
    plt.ylabel("Driver Code")
    plt.xticks(rotation=45, ha="right")
    plt.title("Time Difference from Fastest Lap by Constructor")

    # Invert the y-axis to display the slowest drivers at the top
    plt.gca().invert_yaxis()

    plt.tight_layout()
    plt.show()


def plot_quali_constructors(quali_data):
    """Plot time differences by constructor."""
    plt.style.use("dark_background")
    plt.figure(figsize=(12, 8))

    # Group by constructor and calculate minimum time difference
    constructor_time_diff = (
        quali_data.groupby("Constructor_name")["timeDiff"].min().reset_index()
    )
    constructor_time_diff = constructor_time_diff.sort_values(by="timeDiff")

    # Plot constructor time differences
    plt.barh(
        constructor_time_diff["Constructor_name"],
        constructor_time_diff["timeDiff"],
        color=constructor_time_diff["Constructor_name"].map(
            lambda team: quali_data[quali_data["Constructor_name"] == team][
                "color"
            ].iloc[0]
        ),
    )

    # Create the legend based on the unique teams in the qualifying data
    unique_teams = constructor_time_diff["Constructor_name"].unique()

    # Map the unique team names to their respective colors
    legend_handles = [
        plt.Line2D(
            [0],
            [0],
            color=quali_data[quali_data["Constructor_name"] == team]["color"].iloc[0],
            lw=4,
        )
        for team in unique_teams
    ]
    plt.legend(legend_handles, unique_teams, title="Constructor")

    # Add axis labels and title
    plt.xlabel("Time Difference from Fastest (seconds)")
    plt.ylabel("Constructor")
    plt.xticks(rotation=45, ha="right")
    plt.title("Time Difference from Fastest Lap by Constructor")

    # Invert the y-axis to display constructors with the slowest times at the top
    plt.gca().invert_yaxis()

    plt.tight_layout()
    plt.show()
