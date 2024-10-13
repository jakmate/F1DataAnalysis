# %%
# Load imports
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils import getFiles, getConstructorColours, convert_to_time_format, convert_lap_time_to_milliseconds

# %%
# Load the datasets
files = getFiles()

# Load all datasets into a dictionary
data = {name: pd.read_csv(path) for name, path in files.items()}

# %%
# Define colors for constructors
constructor_colors = getConstructorColours()

# %%
def get_qualifying_data(grand_prix_name, year, qualifying_sessions):
    # Merge qualifying data with race information
    races_info = data['races'][['raceId', 'name', 'year']]
    qualifying_data = pd.merge(data['qualifying'], races_info, on='raceId')
    
    # Check if the year exists in the dataset
    if year not in qualifying_data['year'].values:
        print(f"No qualifying data found for the year {year}.")
        return None
    
    # Filter for the specified year and race (e.g., Bahrain GP)
    qualifying_for_year = qualifying_data[qualifying_data['year'] == year]
    qualifying_for_race = qualifying_for_year[qualifying_for_year['name'] == grand_prix_name]

    # If no data exists for the given race, handle this edge case
    if qualifying_for_race.empty:
        print(f"No data found for {grand_prix_name} in {year}.")
        return None

    # Merge with drivers to get driver codes
    driver_info = data['drivers'][['driverId', 'code']]
    qualifying_with_drivers = pd.merge(qualifying_for_race, driver_info, on='driverId')

    # Ensure 'qualifying_sessions' is a list
    if isinstance(qualifying_sessions, str):
        qualifying_sessions = [qualifying_sessions]

    # Convert lap times for the specified sessions to milliseconds
    for session in qualifying_sessions:
        if session in qualifying_with_drivers.columns:
            qualifying_with_drivers[f'{session}_ms'] = qualifying_with_drivers[session].apply(convert_lap_time_to_milliseconds)
        else:
            print(f"Session {session} not found in the data.")

    # Collect session columns for which we have times in milliseconds
    session_ms_columns = [f'{s}_ms' for s in ['q1', 'q2', 'q3'] if f'{s}_ms' in qualifying_with_drivers.columns]

    if session_ms_columns:
        # Calculate the fastest lap time for each driver across the sessions
        qualifying_with_drivers['fastest_lap_ms'] = qualifying_with_drivers[session_ms_columns].min(axis=1, skipna=True)

        # Convert fastest lap from milliseconds back to time format
        qualifying_with_drivers['fastest_lap'] = qualifying_with_drivers['fastest_lap_ms'].apply(convert_to_time_format)

    # Merge with constructors data
    constructor_info = data['constructors'][['constructorId', 'name']].rename(columns={'name': 'team_name'})
    qualifying_with_teams = pd.merge(qualifying_with_drivers, constructor_info, on='constructorId')

    # Calculate the time difference from the fastest lap
    qualifying_with_teams['time_diff_from_fastest'] = (qualifying_with_teams['fastest_lap_ms'] - qualifying_with_teams['fastest_lap_ms'].min()) / 6000
    qualifying_with_teams = qualifying_with_teams.sort_values(by='time_diff_from_fastest')

    # Assign colors to teams
    qualifying_with_teams['color'] = qualifying_with_teams['team_name'].map(constructor_colors)

    return qualifying_with_teams

# %%
def plot_qualifying_drivers(qualifying_data):
    # Set the plot style and figure size
    plt.style.use('dark_background')
    plt.figure(figsize=(12, 8))
    
    # Plot horizontal bar chart for time difference from fastest lap
    bars = plt.barh(qualifying_data['code'], qualifying_data['time_diff_from_fastest'], color=qualifying_data['color'])

    # Create legend for constructors based on team colors
    legend_handles = [plt.Line2D([0], [0], color=color, lw=4) for color in constructor_colors.values()]
    legend_labels = list(constructor_colors.keys())
    plt.legend(legend_handles, legend_labels, title="Constructor")

    # Add axis labels and title
    plt.xlabel("Time Difference from Fastest (seconds)")
    plt.ylabel("Driver Code")
    plt.xticks(rotation=45, ha='right')
    plt.title("Time Difference from Fastest Lap by Constructor")
    
    # Invert the y-axis to display the slowest drivers at the top
    plt.gca().invert_yaxis()
    
    plt.tight_layout()
    plt.show()

# %%
def plot_time_diff_by_constructor(qualifying_data):
    # Set the plot style and figure size
    plt.style.use('dark_background')
    plt.figure(figsize=(12, 8))
    
    # Group data by constructor and calculate the minimum time difference for each constructor
    constructor_time_diff = qualifying_data.groupby('team_name')['time_diff_from_fastest'].min().reset_index()

    # Sort constructors by time difference for better visual representation
    constructor_time_diff = constructor_time_diff.sort_values(by='time_diff_from_fastest')

    # Plot horizontal bar chart for constructors' time difference from the fastest lap
    bars = plt.barh(constructor_time_diff['team_name'], constructor_time_diff['time_diff_from_fastest'], 
                     color=constructor_time_diff['team_name'].map(constructor_colors))

    # Create legend for constructors based on team colors
    legend_handles = [plt.Line2D([0], [0], color=color, lw=4) for color in constructor_colors.values()]
    legend_labels = list(constructor_colors.keys())
    plt.legend(legend_handles, legend_labels, title="Constructor")

    # Add axis labels and title
    plt.xlabel("Time Difference from Fastest (seconds)")
    plt.ylabel("Constructor")
    plt.xticks(rotation=45, ha='right')
    plt.title("Time Difference from Fastest Lap by Constructor")

    # Invert the y-axis to display constructors with the slowest times at the top
    plt.gca().invert_yaxis()

    plt.tight_layout()
    plt.show()


