import numpy as np
import pandas as pd

def getConstructorColours():
    """Return a dictionary of constructor colors."""
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

def convertToTimeFormat(ms):
    """Convert milliseconds to "minutes:seconds.milliseconds" format."""
    if pd.isna(ms):
        return 'N/A'
    minutes, seconds = divmod(ms // 1000, 60)
    milliseconds = ms % 1000
    return f"{int(minutes)}:{int(seconds):02}.{int(milliseconds):03}"

def convertLapTimeToMs(lapTime):
    """Convert lap time from "minutes:seconds" format to milliseconds."""
    if pd.isna(lapTime) or lapTime == r'\N':
        return np.nan  # Return NaN for missing or invalid values
    mins, secs = lapTime.split(':')
    return int(mins) * 60 * 1000 + float(secs) * 1000

def formatMinutes(x, pos):
    """Format y-axis ticks for minutes and seconds."""
    minutes, remainder = divmod(x, 1)
    seconds = remainder * 60
    return f'{int(minutes):02}:{seconds:05.3f}'