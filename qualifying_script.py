# Load imports
import pandas as pd
import matplotlib.pyplot as plt
from utils import getFiles, getConstructorColours, convert_lap_time_to_ms

# Load the datasets
files = getFiles()

# Load all datasets into a dictionary
data = {name: pd.read_csv(path) for name, path in files.items()}

# Define colors for constructors
constructor_colors = getConstructorColours()

def filterData(data, column, value):
    """Filtering function to filter by any column."""
    if value == 'all':
        print(f"Returning all values for {column}.")
        return data
    if isinstance(value, list):
        print(f"Filtering by values: {value} for {column}.")
        return data[data[column].isin(value)]
    print(f"Filtering by single value: {value} for {column}.")
    return data[data[column] == value]

def getQualiData(gp='all', year='all', sessions='all'):
    """Retrieve qualifying data with filtering and necessary transformations."""
    # Merge qualifying data with race information
    races_info = data['races'][['raceId', 'name', 'year']]
    quali_data = pd.merge(data['qualifying'], races_info, on='raceId')
    
    # Filter by year, race
    quali_data = filterData(quali_data, 'year', year)
    quali_data = filterData(quali_data, 'name', gp)

    # If no data exists for the given race, handle this edge case
    if quali_data.empty:
        print(f"No data found for {gp} in {year}.")
        return None

    # Merge with drivers to get driver codes
    drivers = data['drivers'][['driverId', 'code']]
    quali_with_drivers = pd.merge(quali_data, drivers, on='driverId')

    if sessions == 'all':
        sessions = ["q1", "q2", "q3"]

    # Filter valid sessions that exist in the data
    valid_sessions = [session for session in sessions if session in quali_with_drivers.columns]
    if not valid_sessions:
        print("No valid qualifying sessions found.")
        return None

    # Convert lap times for the valid sessions to milliseconds
    for session in valid_sessions:
        quali_with_drivers[f'{session}_ms'] = quali_with_drivers[session].apply(convert_lap_time_to_ms)
    
    # Collect session columns for which we have times in milliseconds
    session_ms_columns = [f'{s}_ms' for s in valid_sessions]

    if session_ms_columns:
        # Calculate the fastest lap time for each driver across the sessions
        quali_with_drivers['fastest_lap_ms'] = quali_with_drivers[session_ms_columns].min(axis=1, skipna=True)

        # Convert fastest lap from milliseconds back to time format
        quali_with_drivers['fastest_lap'] = quali_with_drivers['fastest_lap_ms']

    # Merge with constructors data
    constructors = data['constructors'][['constructorId', 'name']].rename(columns={'name': 'team_name'})
    quali_with_teams = pd.merge(quali_with_drivers, constructors, on='constructorId')

    # Calculate the time difference from the fastest lap
    quali_with_teams['time_diff'] = (quali_with_teams['fastest_lap_ms'] - quali_with_teams['fastest_lap_ms'].min()) / 6000
    quali_with_teams = quali_with_teams.sort_values(by='time_diff')

    # Assign colors to teams
    quali_with_teams['color'] = quali_with_teams['team_name'].map(constructor_colors)

    return quali_with_teams

def plotQualiDrivers(quali_data):
    """Plot time differences by driver."""
    # Fill any missing colors with a default 'gray'
    quali_data['color'].fillna('gray', inplace=True)
    
    plt.style.use('dark_background')
    plt.figure(figsize=(12, 8))
    
    # Plot driver time differences
    bars = plt.barh(quali_data['code'], quali_data['time_diff'], color=quali_data['color'])

    # Create the legend based on the unique teams in the qualifying data
    unique_teams = quali_data['team_name'].unique()
    
    # Map the unique team names to their respective colors
    legend_handles = [plt.Line2D([0], [0], color=quali_data[quali_data['team_name'] == team]['color'].iloc[0], lw=4) for team in unique_teams]
    plt.legend(legend_handles, unique_teams, title="Constructor")

    # Add axis labels and title
    plt.xlabel("Time Difference from Fastest (seconds)")
    plt.ylabel("Driver Code")
    plt.xticks(rotation=45, ha='right')
    plt.title("Time Difference from Fastest Lap by Constructor")
    
    # Invert the y-axis to display the slowest drivers at the top
    plt.gca().invert_yaxis()
    
    plt.tight_layout()
    plt.show()


def plotQualiConstructors(quali_data):
    """Plot time differences by constructor."""
    plt.style.use('dark_background')
    plt.figure(figsize=(12, 8))
    
    # Group by constructor and calculate minimum time difference
    constructor_time_diff = quali_data.groupby('team_name')['time_diff'].min().reset_index()
    constructor_time_diff = constructor_time_diff.sort_values(by='time_diff')

    # Plot constructor time differences
    bars = plt.barh(constructor_time_diff['team_name'], constructor_time_diff['time_diff'], 
                     color=constructor_time_diff['team_name'].map(lambda team: quali_data[quali_data['team_name'] == team]['color'].iloc[0]))

    # Create the legend based on the unique teams in the qualifying data
    unique_teams = constructor_time_diff['team_name'].unique()
    
    # Map the unique team names to their respective colors
    legend_handles = [plt.Line2D([0], [0], color=quali_data[quali_data['team_name'] == team]['color'].iloc[0], lw=4) for team in unique_teams]
    plt.legend(legend_handles, unique_teams, title="Constructor")

    # Add axis labels and title
    plt.xlabel("Time Difference from Fastest (seconds)")
    plt.ylabel("Constructor")
    plt.xticks(rotation=45, ha='right')
    plt.title("Time Difference from Fastest Lap by Constructor")

    # Invert the y-axis to display constructors with the slowest times at the top
    plt.gca().invert_yaxis()

    plt.tight_layout()
    plt.show()