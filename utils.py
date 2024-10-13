import numpy as np
import pandas as pd

# %%
def getFiles():
    return {
        'circuits': 'archive/circuits.csv',
        'constructor_results': 'archive/constructor_results.csv',
        'constructor_standings': 'archive/constructor_standings.csv',
        'constructors': 'archive/constructors.csv',
        'driver_standings': 'archive/driver_standings.csv',
        'drivers': 'archive/drivers.csv',
        'lap_times': 'archive/lap_times.csv',
        'pit_stops': 'archive/pit_stops.csv',
        'qualifying': 'archive/qualifying.csv',
        'races': 'archive/races.csv',
        'results': 'archive/results.csv',
        'seasons': 'archive/seasons.csv',
        'sprint_results': 'archive/sprint_results.csv',
        'status': 'archive/status.csv'
    }

# %%
def getConstructorColours():
    return {
        'Ferrari': '#E8002D',
        'Sauber': '#52E252',
        'Red Bull': '#3671C6',
        'McLaren': '#FF8000',
        'Mercedes': '#27F4D2',
        'Williams': '#64C4FF',
        'Alpine F1 Team': '#FF87BC',
        'Aston Martin': '#229971',
        'RB F1 Team': '#6692FF',
        'Haas F1 Team': '#B6BABD',
    }

# %%
# Convert milliseconds to "minutes:seconds.milliseconds" format
def convert_to_time_format(ms):
    if pd.isna(ms):
        return 'N/A'
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000
    return f"{int(minutes)}:{int(seconds):02}.{int(milliseconds):03}"

# %%
# Convert lap times from "minutes:seconds" to milliseconds
def convert_lap_time_to_milliseconds(lap_time_str):
    if lap_time_str == r'\N':
        return np.nan  # Return NaN for missing values
    minutes, seconds = lap_time_str.split(':')
    return (int(minutes) * 60 * 1000) + (float(seconds) * 1000)

# %%
# Function to format y-axis ticks for minutes and seconds
def format_minutes(x, pos):
    minutes = int(x)
    seconds = (x - minutes) * 60
    return f'{minutes:02}:{seconds:05.3f}'