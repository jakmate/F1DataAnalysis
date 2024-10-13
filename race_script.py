# %%
# Load imports
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from utils import getFiles, getConstructorColours, format_minutes
from matplotlib.ticker import FuncFormatter

# %%
# Load the datasets
files = getFiles()

# Load all datasets into a dictionary
data = {name: pd.read_csv(path) for name, path in files.items()}

# %%
# Define colors for constructors
constructor_colors = getConstructorColours()

def boxPlotLapTimes(data):
    # Plot lap times boxplot for Bahrain Grand Prix
    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='code', y='lap_time_minutes', data=data)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_minutes))
    plt.xlabel('Driver Code')
    plt.ylabel('Lap Time (minutes)')
    plt.title('Lap Times for Bahrain Grand Prix (2024)')
    plt.show()
    
def getLapTimes(grand_prix_name, year):
    races_subset = data['races'][['raceId', 'name', 'year']]
    # Prepare lap times data for Bahrain Grand Prix
    lap_times = pd.merge(data['lap_times'], races_subset[races_subset['year'] == year], on='raceId')
    lap_times = pd.merge(lap_times, data['drivers'][['driverId', 'code', 'forename', 'surname']], on='driverId')
    bahrain_gp = lap_times[lap_times['name'] == grand_prix_name].copy()

    results_subset = data['results'][['raceId', 'driverId', 'constructorId']]
    bahrain_gp = pd.merge(bahrain_gp, results_subset, on=['raceId', 'driverId'])
    bahrain_gp = pd.merge(bahrain_gp, data['constructors'][['constructorId', 'name']], on=['constructorId'])
    # Convert lap times to minutes
    bahrain_gp['lap_time_minutes'] = bahrain_gp['milliseconds'] / 60000
    return bahrain_gp