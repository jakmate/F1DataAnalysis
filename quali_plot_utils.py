import matplotlib.pyplot as plt

def plotQualiDrivers(qualiData):
    """Plot time differences by driver."""
    # Fill any missing colors with a default 'gray'
    qualiData['color'].fillna('gray', inplace=True)
    
    plt.style.use('dark_background')
    plt.figure(figsize=(12, 8))
    
    # Plot driver time differences
    bars = plt.barh(qualiData['Driver_code'], qualiData['timeDiff'], color=qualiData['color'])

    # Create the legend based on the unique teams in the qualifying data
    uniqueTeams = qualiData['Constructor_name'].unique()
    
    # Map the unique team names to their respective colors
    legend_handles = [plt.Line2D([0], [0], color=qualiData[qualiData['Constructor_name'] == team]['color'].iloc[0], lw=4) for team in uniqueTeams]
    plt.legend(legend_handles, uniqueTeams, title="Constructor")

    # Add axis labels and title
    plt.xlabel("Time Difference from Fastest (seconds)")
    plt.ylabel("Driver Code")
    plt.xticks(rotation=45, ha='right')
    plt.title("Time Difference from Fastest Lap by Constructor")
    
    # Invert the y-axis to display the slowest drivers at the top
    plt.gca().invert_yaxis()
    
    plt.tight_layout()
    plt.show()


def plotQualiConstructors(qualiData):
    """Plot time differences by constructor."""
    plt.style.use('dark_background')
    plt.figure(figsize=(12, 8))
    
    # Group by constructor and calculate minimum time difference
    constructorTimeDiff = qualiData.groupby('Constructor_name')['timeDiff'].min().reset_index()
    constructorTimeDiff = constructorTimeDiff.sort_values(by='timeDiff')

    # Plot constructor time differences
    bars = plt.barh(constructorTimeDiff['Constructor_name'], constructorTimeDiff['timeDiff'], 
                     color=constructorTimeDiff['Constructor_name'].map(lambda team: qualiData[qualiData['Constructor_name'] == team]['color'].iloc[0]))

    # Create the legend based on the unique teams in the qualifying data
    uniqueTeams = constructorTimeDiff['Constructor_name'].unique()
    
    # Map the unique team names to their respective colors
    legend_handles = [plt.Line2D([0], [0], color=qualiData[qualiData['Constructor_name'] == team]['color'].iloc[0], lw=4) for team in uniqueTeams]
    plt.legend(legend_handles, uniqueTeams, title="Constructor")

    # Add axis labels and title
    plt.xlabel("Time Difference from Fastest (seconds)")
    plt.ylabel("Constructor")
    plt.xticks(rotation=45, ha='right')
    plt.title("Time Difference from Fastest Lap by Constructor")

    # Invert the y-axis to display constructors with the slowest times at the top
    plt.gca().invert_yaxis()

    plt.tight_layout()
    plt.show()