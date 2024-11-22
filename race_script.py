# Load imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from utils import getFiles, getConstructorColours, format_minutes, convert_to_time_format
from matplotlib.ticker import FuncFormatter

# Load the datasets
files = getFiles()

# Load all datasets into a dictionary
data = {name: pd.read_csv(path) for name, path in files.items()}

# Define colors for constructors
constructor_colors = getConstructorColours()

def getLapTimes(grand_prix_name, year):
    """Retrieve lap times for a specific Grand Prix and year."""
    races_subset = data['races'][['raceId', 'name', 'year']]
    # Prepare lap times data for specific Grand Prix
    lap_times = pd.merge(data['lap_times'], races_subset[races_subset['year'] == year], on='raceId')
    lap_times = pd.merge(lap_times, data['drivers'][['driverId', 'code', 'forename', 'surname']], on='driverId')
    race_data = lap_times[lap_times['name'] == grand_prix_name].copy()

    results_subset = data['results'][['raceId', 'driverId', 'constructorId']]
    race_data = pd.merge(race_data, results_subset, on=['raceId', 'driverId'])
    race_data = pd.merge(race_data, data['constructors'][['constructorId', 'name']], on=['constructorId'])
    # Convert lap times to minutes
    race_data['lap_time_minutes'] = race_data['milliseconds'] / 60000
    return race_data

def removePitstopLaps(lap_times, pit_stops):
    """Remove laps that include pit stops from the lap times."""
    merged_df = pd.merge(lap_times, pit_stops[['raceId', 'driverId', 'lap']], on=['raceId', 'driverId', 'lap'], how='left', indicator=True)

    pitstop_laps = merged_df[merged_df['_merge'] == 'both']
    next_lap_laps = pitstop_laps.copy()
    next_lap_laps['lap'] += 1

    laps_to_remove = pd.concat([pitstop_laps[['raceId', 'driverId', 'lap']], next_lap_laps[['raceId', 'driverId', 'lap']]]).drop_duplicates()

    lap_times_no_pitstops = pd.merge(merged_df, laps_to_remove, on=['raceId', 'driverId', 'lap'], how='left', indicator='remove_status')
    lap_times_no_pitstops = lap_times_no_pitstops[lap_times_no_pitstops['remove_status'] != 'both']

    lap_times_no_pitstops.reset_index(drop=True, inplace=True)
    return lap_times_no_pitstops

def calculateDriverStatistics(df, driver_names):
    """Calculate mean and standard deviation lap times for each driver."""
    stats = df.groupby('driverId')['milliseconds'].agg(['mean', 'std']).reset_index()
    stats = stats.join(driver_names, on='driverId')
    stats['mean_time'] = stats['mean'].apply(convert_to_time_format)
    stats['std_time'] = stats['std'].apply(convert_to_time_format)
    return stats

def plotLapTimesBoxplot(data):
    """Plot a boxplot of lap times for the Bahrain Grand Prix."""
    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='code', y='lap_time_minutes', data=data)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_minutes))
    plt.xlabel('Driver Code')
    plt.ylabel('Lap Time (minutes)')
    plt.title('Lap Times for Bahrain Grand Prix (2024)')
    plt.show()

def plotStdDevLapTimes(stats, constructor_colors):
    """Plot standard deviation of lap times by driver."""
    unique_teams = stats['name_y'].unique()
    for team in unique_teams:
        if team not in constructor_colors:
            constructor_colors[team] = 'gray'

    plot_data = stats[['forename', 'surname', 'name_y', 'no_pitstops_std']].reset_index()
    plot_data = plot_data.melt(id_vars=['forename', 'surname', 'name_y'],
                               value_vars=['no_pitstops_std'],
                               var_name='Scenario',
                               value_name='Standard Deviation')

    plot_data['Standard Deviation (s)'] = plot_data['Standard Deviation'] / 1000
    plot_data_sorted = plot_data.sort_values(by='Standard Deviation (s)')

    drivers = plot_data_sorted['surname'].unique()
    x = np.arange(len(drivers))
    bar_width = 0.8

    fig, ax = plt.subplots(figsize=(16, 10))
    bars = ax.bar(x, plot_data_sorted['Standard Deviation (s)'],
                  color=plot_data_sorted['name_y'].map(constructor_colors),
                  width=bar_width, align='center')

    ax.set_xlabel('Driver')
    ax.set_ylabel('Standard Deviation (seconds)')
    ax.set_title('Standard Deviation of Lap Times by Driver')
    ax.set_xticks(x)
    ax.set_xticklabels(drivers, rotation=90)
    ax.set_xlim(-bar_width, len(drivers) - 1 + bar_width)

    handles = [plt.Line2D([0], [0], color=color, lw=4) for color in constructor_colors.values()]
    labels = list(constructor_colors.keys())
    ax.legend(handles, labels, title='Constructor', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()

def plotMeanLapTimes(stats, constructor_colors):
    """Plot average difference in lap times by driver."""
    plot_data = stats[['forename', 'surname', 'name_y', 'no_pitstops_mean']].reset_index()
    plot_data = plot_data.melt(id_vars=['forename', 'surname', 'name_y'],
                               value_vars=['no_pitstops_mean'],
                               var_name='Scenario',
                               value_name='Mean')

    plot_data_sorted = plot_data.sort_values(by='Mean')
    plot_data_sorted['Dif_from_fastest'] = (plot_data_sorted['Mean'] - plot_data_sorted['Mean'].min()) / 6000

    drivers = plot_data_sorted['surname'].unique()
    x = np.arange(len(drivers))
    bar_width = 0.8

    fig, ax = plt.subplots(figsize=(16, 10))
    bars = ax.bar(x, plot_data_sorted['Dif_from_fastest'],
                  color=plot_data_sorted['name_y'].map(constructor_colors),
                  width=bar_width, align='center')

    ax.set_xlabel('Driver')
    ax.set_ylabel('+ from quickest car (s)')
    ax.set_title('Average Difference in Lap Times by Drivers')
    ax.set_xticks(x)
    ax.set_xticklabels(drivers, rotation=90)
    ax.set_xlim(-bar_width, len(drivers) - 1 + bar_width)

    handles = [plt.Line2D([0], [0], color=color, lw=4) for color in constructor_colors.values()]
    labels = list(constructor_colors.keys())
    ax.legend(handles, labels, title='Constructor', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()