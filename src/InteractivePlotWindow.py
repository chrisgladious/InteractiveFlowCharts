import os
# os.chdir(r'C:\Users\secn17444\OneDrive - WSP O365\pyproj\flow_env\src')
import pandas as pd
import openpyxl

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QCheckBox,QPushButton, QWidget, QLabel
from PyQt6.QtGui import QKeySequence, QShortcut
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
import matplotlib.dates as mdates
from matplotlib.dates import MO, WeekdayLocator
import matplotlib.pyplot as plt
import sys
import numpy as np
import pandas as pd

import inspect
import re
def dprint(x): # https://stackoverflow.com/questions/32000934/print-a-variables-name-and-value/57225950#57225950
    frame = inspect.currentframe().f_back
    s = inspect.getframeinfo(frame).code_context[0]
    r = re.search(r"\((.*)\)", s).group(1)
    print("{} = {}".format(r,x))

class CustomNavigationToolbar(NavigationToolbar2QT):
    def __init__(self, canvas, parent=None, plot_window = None):
        super().__init__(canvas, parent)
        self.plot_window = plot_window
        self.addSeparator()
        self.addAction('Autoscale', self.autoscale)
        self.addSeparator()
        self.addAction('Autoscale LY', self.autoscaleLeftY)
        self.addSeparator()
        self.addAction('Autoscale RY', self.autoscaleRightY)
        self.addSeparator()        
        self.addAction('Move Left', self.moveLeft)
        self.addSeparator()
        self.addAction('Move Right', self.moveRight)
        self.addSeparator()
        self.addAction('Reset X', self.plot_window.reformatXAxis)
        self.addSeparator()
#         # Set fixed size for buttons
#         button_width = 100
#         button_height = 30
        # Add keyboard shortcuts
        self.shortcut_pan = QShortcut(QKeySequence("P"), self)
        self.shortcut_pan.activated.connect(self.pan)

        self.shortcut_zoom = QShortcut(QKeySequence("Z"), self)
        self.shortcut_zoom.activated.connect(self.zoom)

        # Add QLabel to display xAxisLen
        self.xAxisLenLabel = QLabel("xAxisLen: N/A")
        self.addWidget(self.xAxisLenLabel)

    def autoscale(self):
        ax1 = self.plot_window.axL
        ax1.autoscale(axis='both')
        self.canvas.draw()
        self.update_xAxisLen()

    def autoscaleLeftY(self):
        df_axL = self.plot_window.df_axL
        series_visibleLeftY = self.plot_window.series_visible[:len(df_axL.columns)]
        if not any(series_visibleLeftY):
            return
        # dprint(len(series_visibleLeftY))
        selected_columns = df_axL.loc[:, series_visibleLeftY]

        # Get current x-axis limits
        xlim = self.plot_window.axL.get_xlim()
        xlim = [mdates.num2date(x).replace(tzinfo=None) for x in xlim]  # Remove timezone info
        selected_columns = selected_columns[(selected_columns.index >= xlim[0]) & (selected_columns.index <= xlim[1])]

        ylim = (selected_columns.min().min(), selected_columns.max().max())
        self.plot_window.axL.set_ylim(ylim)
        self.canvas.draw()

    def autoscaleRightY(self):
        df_axL = self.plot_window.df_axL
        df_axR = self.plot_window.df_axR
        if df_axR.empty:
            df_axRcolumns = 0
        else:
            df_axRcolumns = len(df_axR.columns)
        series_visibleRightY = self.plot_window.series_visible[len(df_axL.columns):len(df_axL.columns) + df_axRcolumns]
        if not any(series_visibleRightY):
            return
        # dprint(len(series_visibleRightY))
        selected_columns = df_axR.loc[:, series_visibleRightY]

        # Get current x-axis limits
        xlim = self.plot_window.axR.get_xlim()
        xlim = [mdates.num2date(x).replace(tzinfo=None) for x in xlim]  # Remove timezone info
        selected_columns = selected_columns[(selected_columns.index >= xlim[0]) & (selected_columns.index <= xlim[1])]

        ylim = (selected_columns.min().min(), selected_columns.max().max())
        self.plot_window.axR.set_ylim(ylim)
        self.canvas.draw()

    def pan(self):
        super().pan()
        self.plot_window.reformatXAxis()
        self.update_xAxisLen()

    def zoom(self):
        super().zoom()
        self.plot_window.reformatXAxis()
        self.update_xAxisLen()

    def update_xAxisLen(self):
        ax1 = self.canvas.figure.gca()
        xlim = ax1.get_xlim()
        xAxisLen = xlim[1] - xlim[0]
        self.xAxisLenLabel.setText(f"xAxisLen: {xAxisLen:.2f}")
    
    def moveLeft(self):
        xlim = self.plot_window.axL.get_xlim()
        step = (xlim[1] - xlim[0]) * 0.25  # Move 25% of the current x-axis range
        self.plot_window.axL.set_xlim(xlim[0] - step, xlim[1] - step)
        self.canvas.draw()
        self.update_xAxisLen()

    def moveRight(self):
        xlim = self.plot_window.axL.get_xlim()
        step = (xlim[1] - xlim[0]) * 0.25  # Move 25% of the current x-axis range
        self.plot_window.axL.set_xlim(xlim[0] + step, xlim[1] + step)
        self.canvas.draw()
        self.update_xAxisLen()

class InteractivePlotWindow(QMainWindow):
    def __init__(self, df_axL, df_axL_Title = None, df_axR=None, df_axR_Title = None, WindowTitle = None):
        super().__init__()
        if WindowTitle == None:
            self.setWindowTitle("Interactive Plot")
        else:
            self.setWindowTitle(WindowTitle)

        # Store the DataFrame
        self.df_axL = df_axL
        self.df_axR = df_axR
        self.df_axL_Title = df_axL_Title
        self.df_axR_Title = df_axR_Title
        
        # Flag to check if it's the initial plot
        self.initial_plot = True

        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Create Figure and Canvas
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = CustomNavigationToolbar(self.canvas, self, plot_window=self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Create buttons dynamically
        if df_axR.empty:
            df_axRcolumns = 0
        else:
            df_axRcolumns = len(df_axR.columns)        
        self.series_visible = [True] * (len(self.df_axL.columns) + df_axRcolumns)  # Adjusted to include both df and df_ax2 columns
        checkbox_layout = QHBoxLayout()
        self.checkboxes = []
        for i, col in enumerate(df_axL.columns):
            checkbox = QCheckBox(f"{col}")
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.create_toggle_function(i))
            checkbox_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)
        if df_axR is not None and not df_axR.empty:
            for i, col in enumerate(df_axR.columns, start=len(df_axL.columns)):
                checkbox = QCheckBox(f"{col}")
                checkbox.setChecked(True)
                checkbox.stateChanged.connect(self.create_toggle_function(i))
                checkbox_layout.addWidget(checkbox)
                self.checkboxes.append(checkbox)
        layout.addLayout(checkbox_layout)

        # Initial plot
        self.plot()

    def create_toggle_function(self, index):
        def toggle():
            self.series_visible[index] = not self.series_visible[index]
            self.plot()
        return toggle

    def plot(self):
        # Save the axis title and labels
        title = self.axL.get_title() if hasattr(self, 'ax1') else ''
        xlabel = self.axL.get_xlabel() if hasattr(self, 'ax1') else ''
        ylabel = self.axL.get_ylabel() if hasattr(self, 'ax1') else ''

        if not self.initial_plot:
            self.axLxlim = self.axL.get_xlim()
            self.axLylim = self.axL.get_ylim()
            if self.df_axR is not None and not self.df_axR.empty:
                self.axRxlim = self.axR.get_xlim()
                self.axRylim = self.axR.get_ylim()

        # Clear the axes
        self.fig.clear()
        self.axL = self.fig.add_subplot(111)

        # Restore the axis title and labels
        self.axL.set_title(title)
        self.axL.set_xlabel(xlabel)
        self.axL.set_ylabel(ylabel)

        self.axL.grid(visible=True, which='major', axis='both', color='grey')
        self.axL.grid(visible=True, which='minor', axis='both', color='lightgrey')
        self.axL.tick_params(which='minor', labelcolor='lightgrey')
        self.axL.tick_params(axis='x', rotation=90, which='both')
        self.axL.set_ylabel(self.df_axL_Title)

        for i, col in enumerate(self.df_axL.columns):
            if self.series_visible[i]:
                self.axL.plot(self.df_axL.index, self.df_axL[col], label=col, alpha=0.5)

        handles, labels = self.axL.get_legend_handles_labels()

        self.axR = None
        if self.df_axR is not None and not self.df_axR.empty:
            self.axR = self.axL.twinx()
            for i, col in enumerate(self.df_axR.columns, start=len(self.df_axL.columns)):
                if self.series_visible[i]:
                    self.axR.plot(self.df_axL.index, self.df_axR[col], label=col, alpha=0.5)
            self.axR.set_ylabel(self.df_axR_Title)

            handles2, labels2 = self.axR.get_legend_handles_labels()
            # Add a separator in the legend
            # handles.append(plt.Line2D([0], [0], linestyle='--', color='black', label='--- Right Axis ---'))
            # labels.append('--- Right Axis ---')
            handles += handles2
            labels += labels2

        self.axL.legend(handles, labels)

        if self.initial_plot:
            self.initial_plot = False
            self.axL.autoscale(axis='both')
            self.axLxlim = self.axL.get_xlim()
            self.axLylim = self.axL.get_ylim()
            if self.df_axR is not None and not self.df_axR.empty:
                self.axRxlim = self.axR.get_xlim()
                self.axRylim = self.axR.get_ylim()
            self.fig.tight_layout()
            # self.fig.subplots_adjust(top=0.94,
            #                          bottom=0.155,
            #                          left=0.05,
            #                          right=0.975,
            #                          hspace=0.2,
            #                          wspace=0.2)
        else:
            self.axL.set_xlim(self.axLxlim)
            self.axL.set_ylim(self.axLylim)
            if self.df_axR is not None and not self.df_axR.empty:
                self.axR.set_xlim(self.axRxlim)
                self.axR.set_ylim(self.axRylim)

        # Apply x-axis formatting to both axL and axR
        self.reformatXAxis()

        self.canvas.draw()

    def apply_xaxis_formatting(self, ax):
        xlim = ax.get_xlim()
        xAxisLen = xlim[1] - xlim[0]

        if xAxisLen < 3 / 24:
            ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(24), interval=1))
            ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=range(60), interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter(r'%Y-%m-%d %H:%M'))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(r'%H:%M'))
        elif xAxisLen < 6 / 24:
            ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(24), interval=1))
            ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=range(60), interval=15))
            ax.xaxis.set_major_formatter(mdates.DateFormatter(r'%Y-%m-%d %H:%M'))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(r'%H:%M'))
        elif xAxisLen < 2:
            ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=range(1, 32), interval=1))
            ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(24), interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter(r'%Y-%m-%d %H:%M'))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(r'%H:%M'))
        elif xAxisLen < 7:
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=MO, interval=1))
            ax.xaxis.set_minor_locator(mdates.HourLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter(r'W%U-%m-%d %H:%M'))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(r'%Y-%m-%d %H:%M'))
        elif xAxisLen < 60:
            ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1, interval=1))
            ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=MO, interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter(r'%Y-%m-%d'))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(r'W%U-%m-%d'))
        elif xAxisLen < 367*1.5:
            ax.xaxis.set_major_locator(mdates.YearLocator(base=1,month=1))
            ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=1, interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter(r'%Y'))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(r'%Y-%m-%d'))
        else:
            ax.xaxis.set_major_locator(mdates.YearLocator(base=10,month=1))
            ax.xaxis.set_minor_locator(mdates.YearLocator(base=1,month=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter(r'%Y'))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(r'%Y'))
        return ax

    def reformatXAxis(self):
        self.axL = self.apply_xaxis_formatting(self.axL)
        if self.axR:
            self.axR = self.apply_xaxis_formatting(self.axR)

if __name__ == "__main__":
    # Load the DataFrame from the Excel file
    # excel_file_path = 'c:\\Users\\secn17444\\OneDrive - WSP O365\\Projekt\\Växjö\\5142-10347420\\PST\\Arbetsmaterial\\Flöden till Örsled PST och regn\\Örsled_2021-10-19_-_2021-10_23_version_2_CNI_bara rådata.xlsm'
    # df = pd.read_excel(excel_file_path, index_col='DateTime', parse_dates=True)

    # Path to your Excel file
    excel_file_path = r'c:\Users\secn17444\OneDrive - WSP O365\Projekt\Växjö\5142-10347420\PST\Arbetsmaterial\Flöden till Örsled PST och regn\Örsled_2021-10-19_-_2021-10_23_version_2_CNI_bara rådata.xlsm'

    # Read the Excel file
    df_axL = pd.read_excel(excel_file_path)
    df_axL.drop(columns=['AP220 Wessels  [l/s]'], inplace=True)
    # Convert 'date' column to datetime
    df_axL['DateTime'] = pd.to_datetime(df_axL['DateTime'])

    # Set 'date' column as the index
    df_axL.set_index('DateTime', inplace=True)
    
    df_axL['Summaflöde till Örsled PST  [m3/h]'] = df_axL['AP247 Damsrydh [m³/h]']+df_axL['AP229 Stärkelsen  [m³/h]']+df_axL['AP220 Wessels  [m3/h]']

    df_axR = pd.DataFrame(index=df_axL.index)
    df_axR['Pumpsumpkumsum [m3]'] = df_axL['Summaflöde till Örsled PST  [m3/h]'].cumsum() - df_axL['ASRL02 Örsled PST till Sundets ARV [m3/h]'].cumsum()

    dprint(df_axL.columns[:])
    dprint(df_axR.columns[:])

    app = QApplication(sys.argv)
    mainWin = InteractivePlotWindow(df_axL = df_axL,
                        df_axL_Title = 'Flöde [m3/h]', 
                        df_axR = df_axR, 
                        df_axR_Title = 'Kumsum volym [m³]',
                        WindowTitle='Örsled PST')
    mainWin.show()
    sys.exit(app.exec())
    sys.exit(app.exec())