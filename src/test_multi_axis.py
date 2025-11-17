# Test Script for Multi-Axis Plot Window

import pandas as pd
import numpy as np
from InteractivePlotWindowMultiAxis import InteractivePlotWindowMultiAxis
from PyQt6.QtWidgets import QApplication
import sys

# Create sample data with different units
np.random.seed(42)
dates = pd.date_range('2025-01-01', periods=100, freq='h')

df = pd.DataFrame({
    'Inflow [m3/h]': np.random.randn(100).cumsum() + 50,
    'Outflow [m3/h]': np.random.randn(100).cumsum() + 48,
    'Level [m]': np.random.randn(100).cumsum() * 0.1 + 10,
    'Temperature [°C]': np.random.randn(100).cumsum() * 0.5 + 20,
    'Pressure [kPa]': np.random.randn(100).cumsum() * 2 + 100
}, index=dates)

print("DataFrame shape:", df.shape)
print("\nColumn names:")
for col in df.columns:
    print(f"  - {col}")

# Create application and window
app = QApplication(sys.argv)
window = InteractivePlotWindowMultiAxis(df, WindowTitle="Multi-Unit Monitoring Test")
window.show()

print("\nUnits detected:")
for unit, cols in window.axis_groups.items():
    print(f"  {unit}: {cols}")

sys.exit(app.exec())
