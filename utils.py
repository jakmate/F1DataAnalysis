import numpy as np
import pandas as pd


def get_constructor_colours():
    """Return a dictionary of constructor colors."""
    return {
        "Ferrari": "#E8002D",
        "Sauber": "#52E252",
        "Red Bull": "#3671C6",
        "McLaren": "#FF8000",
        "Mercedes": "#27F4D2",
        "Williams": "#64C4FF",
        "Alpine F1 Team": "#FF87BC",
        "Aston Martin": "#229971",
        "RB F1 Team": "#6692FF",
        "Haas F1 Team": "#B6BABD",
    }


def convert_to_time_format(ms):
    """Convert milliseconds to "minutes:seconds.milliseconds" format."""
    if pd.isna(ms):
        return "N/A"
    minutes, seconds = divmod(ms // 1000, 60)
    milliseconds = ms % 1000
    return f"{int(minutes)}:{int(seconds):02}.{int(milliseconds):03}"


def convert_lap_time_to_ms(lap_time):
    """Convert lap time from "minutes:seconds" format to milliseconds."""
    if pd.isna(lap_time) or lap_time == r"\N":
        return np.nan  # Return NaN for missing or invalid values

    lap_time = str(lap_time).strip()
    # Handle different time formats
    if ":" in lap_time:
        # Format is "minutes:seconds" (e.g., "1:23.456")
        parts = lap_time.split(":")
        if len(parts) == 2:
            mins = int(parts[0])
            # Split seconds and milliseconds if present
            sec_parts = parts[1].split(".")
            secs = int(sec_parts[0])
            ms = int(sec_parts[1]) if len(sec_parts) > 1 else 0
            return mins * 60 * 1000 + secs * 1000 + ms
    else:
        # Format is just "seconds" or "seconds.milliseconds" (e.g., "83.456")
        try:
            total_seconds = float(lap_time)
            return int(total_seconds * 1000)
        except ValueError:
            return np.nan

    return np.nan


def format_minutes(x, _):
    """Format y-axis ticks for minutes and seconds."""
    minutes, remainder = divmod(x, 1)
    seconds = remainder * 60
    return f"{int(minutes):02}:{seconds:05.3f}"
