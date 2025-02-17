from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
import sys
import numpy as np
import pandas as pd
import matplotlib.dates as mdates

class CustomNavigationToolbar(NavigationToolbar2QT):
    def __init__(self, canvas, parent=None, plot_window=None):
        super().__init__(canvas, parent)
        self.plot_window = plot_window
        self.addSeparator()
        self.addAction('Autoscale', self.autoscale)

    def autoscale(self):
        ax = self.canvas.figure.gca()
        ax.autoscale()
        self.canvas.draw()

    def pan(self):
        super().pan()
        self.plot_window.resetXAxis()

    def zoom(self):
        super().zoom()
        self.plot_window.resetXAxis()

class PlotWindow(QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.setWindowTitle("Interactive PyQt Plot")

        # Store the DataFrame
        self.df = df

        # Initialize the initial_plot attribute
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
        self.series_visible = [True] * len(df.columns)
        button_layout = QHBoxLayout()
        self.buttons = []
        for i, col in enumerate(df.columns):
            button = QPushButton(f"Toggle {col}")
            button.clicked.connect(self.create_toggle_function(i))
            button_layout.addWidget(button)
            self.buttons.append(button)
        layout.addLayout(button_layout)

        # Add a button to drop specific columns
        drop_button = QPushButton("Drop Specific Columns")
        drop_button.clicked.connect(self.drop_specific_columns)
        layout.addWidget(drop_button)

        # Initial plot
        self.plot()

    def create_toggle_function(self, index):
        def toggle():
            self.series_visible[index] = not self.series_visible[index]
            self.plot()
        return toggle

    def drop_specific_columns(self):
        columns_to_drop = ['AP247 Damsrydh [m³/h]', 'AP229 Stärkelsen  [m³/h]', 'AP220 Wessels  [l/s]']
        self.df.drop(columns=columns_to_drop, inplace=True, errors='ignore')
        self.series_visible = [True] * len(self.df.columns)
        self.plot()

    def plot(self):
        ax1 = self.fig.gca()
        if not self.initial_plot:
            xlim = ax1.get_xlim()
            ylim = ax1.get_ylim()

        self.fig.clear()
        ax1 = self.fig.add_subplot(111)
        xDateFormat = mdates.DateFormatter(r'%Y-%m-%d')
        xDateFormatWeekNum = mdates.DateFormatter(r'W%U-%m-%d')
        ax1.format_xdata = xDateFormat
        ax1.xaxis.set_major_formatter(xDateFormat)
        ax1.xaxis.set_minor_formatter(xDateFormatWeekNum)

        ax1.grid(visible=True, which='major', axis='both', color='grey')
        ax1.grid(visible=True, which='minor', axis='both', color='lightgrey')
        ax1.tick_params(which='minor', labelcolor='lightgrey')
        handles, labels = ax1.get_legend_handles_labels()
        ax1.legend(handles, labels, loc='upper left', bbox_to_anchor=(0, -0.12), fancybox=True,)

        # Set y-axis label
        ax1.set_ylabel('Flöde [m³/h]', color='blue')

        # Rotate x-axis tick labels
        ax1.tick_params(axis='x', rotation=90, which='both')

        for i, col in enumerate(self.df.columns[:]):
            if self.series_visible[i]:
                ax1.plot(self.df.index, self.df[col], label=col, alpha=0.5)

        ax1.legend()
        self.canvas.draw()

    def resetXAxis(self):
        ax1 = self.fig.gca()
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax1.xaxis.set_minor_locator(mdates.HourLocator(interval=1))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter(r'%Y-%m-%d'))
        ax1.xaxis.set_minor_formatter(mdates.DateFormatter(r'%H:%M'))
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Sample data
    data = {
        'AP247 Damsrydh [m³/h]': np.random.rand(10),
        'AP229 Stärkelsen  [m³/h]': np.random.rand(10),
        'AP220 Wessels  [l/s]': np.random.rand(10),
        'series4': np.random.rand(10)  # Add more series as needed
    }
    df = pd.DataFrame(data, index=pd.date_range(start='2021-01-01', periods=10, freq='D'))

    window = PlotWindow(df)
    window.show()
    sys.exit(app.exec())