from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
import sys
import numpy as np
import pandas as pd

class PlotWindow(QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.setWindowTitle("Interactive PyQt Plot")

        # Store the DataFrame
        self.df = df

        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Create Figure and Canvas
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Create buttons dynamically
        self.series_visible = [True] * (len(df.columns) - 1)  # Assuming the first column is 'date'
        button_layout = QHBoxLayout()
        self.buttons = []
        for i, col in enumerate(df.columns[1:]):  # Skip the 'date' column
            button = QPushButton(f"Toggle {col}")
            button.clicked.connect(self.create_toggle_function(i))
            button_layout.addWidget(button)
            self.buttons.append(button)
        layout.addLayout(button_layout)

        # Initial plot
        self.plot()

    def create_toggle_function(self, index):
        def toggle():
            self.series_visible[index] = not self.series_visible[index]
            self.plot()
        return toggle

    def plot(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        for i, col in enumerate(self.df.columns[1:]):  # Skip the 'date' column
            if self.series_visible[i]:
                ax.plot(self.df['date'], self.df[col], label=col)

        ax.legend()
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Sample data
    data = {
        'date': pd.date_range(start='2021-01-01', periods=10, freq='D'),
        'series1': np.random.rand(10),
        'series2': np.random.rand(10),
        'series3': np.random.rand(10)  # Add more series as needed
    }
    df = pd.DataFrame(data)

    window = PlotWindow(df)
    window.show()
    sys.exit(app.exec())