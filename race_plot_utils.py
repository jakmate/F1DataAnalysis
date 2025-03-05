import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from utils import  getConstructorColours, formatMinutes
from matplotlib.ticker import FuncFormatter

# Define colors for constructors
constructorColors = getConstructorColours()

def plotLapTimesBoxplot(data):
    """Plot a boxplot of lap times for the Bahrain Grand Prix."""
    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='code', y='timeMinutes', data=data)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(formatMinutes))
    plt.xlabel('Driver Code')
    plt.ylabel('Lap Time (minutes)')
    plt.title('Lap Times for Bahrain Grand Prix (2024)')
    plt.show()

def plotStdDevLapTimes(stats, constructorColors):
    """Plot standard deviation of lap times by driver."""
    uniqueTeams = stats['constructor'].unique()
    for team in uniqueTeams:
        if team not in constructorColors:
            constructorColors[team] = 'gray'

    plotData = stats[['firstName', 'lastName', 'constructor', 'adjustedStd']].reset_index()
    plotData = plotData.melt(id_vars=['firstName', 'lastName', 'constructor'],
                               value_vars=['adjustedStd'],
                               var_name='Scenario',
                               value_name='Standard Deviation')

    plotData['Standard Deviation (s)'] = plotData['Standard Deviation'] / 1000
    plotDataSorted = plotData.sort_values(by='Standard Deviation (s)')

    drivers = plotDataSorted['lastName'].unique()
    x = np.arange(len(drivers))
    barWidth = 0.8

    fig, ax = plt.subplots(figsize=(16, 10))
    bars = ax.bar(x, plotDataSorted['Standard Deviation (s)'],
                  color=plotDataSorted['constructor'].map(constructorColors),
                  width=barWidth, align='center')

    ax.set_xlabel('Driver')
    ax.set_ylabel('Standard Deviation (seconds)')
    ax.set_title('Standard Deviation of Lap Times by Driver')
    ax.set_xticks(x)
    ax.set_xticklabels(drivers, rotation=90)
    ax.set_xlim(-barWidth, len(drivers) - 1 + barWidth)

    handles = [plt.Line2D([0], [0], color=color, lw=4) for color in constructorColors.values()]
    labels = list(constructorColors.keys())
    ax.legend(handles, labels, title='Constructor', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()

def plotMeanLapTimes(stats, constructorColors):
    """Plot average difference in lap times by driver."""
    plotData = stats[['firstName', 'lastName', 'constructor', 'adjustedMean']].reset_index()
    plotData = plotData.melt(id_vars=['firstName', 'lastName', 'constructor'],
                               value_vars=['adjustedMean'],
                               var_name='Scenario',
                               value_name='Mean')

    plotData_sorted = plotData.sort_values(by='Mean')
    plotData_sorted['DifFromFastest'] = (plotData_sorted['Mean'] - plotData_sorted['Mean'].min()) / 6000

    drivers = plotData_sorted['lastName'].unique()
    x = np.arange(len(drivers))
    bar_width = 0.8

    fig, ax = plt.subplots(figsize=(16, 10))
    bars = ax.bar(x, plotData_sorted['DifFromFastest'],
                  color=plotData_sorted['constructor'].map(constructorColors),
                  width=bar_width, align='center')

    ax.set_xlabel('Driver')
    ax.set_ylabel('+ from quickest car (s)')
    ax.set_title('Average Difference in Lap Times by Drivers')
    ax.set_xticks(x)
    ax.set_xticklabels(drivers, rotation=90)
    ax.set_xlim(-bar_width, len(drivers) - 1 + bar_width)

    handles = [plt.Line2D([0], [0], color=color, lw=4) for color in constructorColors.values()]
    labels = list(constructorColors.keys())
    ax.legend(handles, labels, title='Constructor', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()