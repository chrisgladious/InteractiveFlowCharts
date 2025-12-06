import os
# os.chdir(r'C:\Users\secn17444\OneDrive - WSP O365\pyproj\flow_env\src')
import pandas as pd
import openpyxl

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QWidget, QLabel, QComboBox, QDialog, QDialogButtonBox, QSizePolicy
from PyQt6.QtGui import QKeySequence, QShortcut, QPalette, QColor
from PyQt6.QtCore import Qt
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

import json
import os

def _split_settings_filename_key(filename: str):
    """Return (base_filename, key) where key is None if not provided via '::'."""
    if isinstance(filename, str) and '::' in filename:
        base, key = filename.split('::', 1)
        base = base.strip()
        key = key.strip()
        return base, (key if key else None)
    return filename, None

def _is_legacy_flat_settings(data):
    """Detect if the settings dict is in legacy flat format (not keyed)."""
    return isinstance(data, dict) and 'axLxlim' in data and 'axLylim' in data

def save_plot_settings(settings, filename='InteractivePlotWindowMultiAxis.json'):
    """Save settings to JSON.
    If filename contains '::KEY', store under that KEY inside a shared JSON file.
    Backward compatible with flat JSON structure.
    """
    base_file, key = _split_settings_filename_key(filename)
    
    # Prepare cleaned settings
    cleaned_settings = {}
    for k, v in (settings or {}).items():
        if k == 'series_visible':
            cleaned_settings[k] = [1 if x else 0 for x in v]
        elif k == 'auto_update':
            # Store auto_update as boolean (1 or 0 integer)
            cleaned_settings[k] = 1 if v else 0
        elif isinstance(v, (list, tuple)):
            try:
                cleaned_settings[k] = [float(x) for x in v]
            except Exception:
                cleaned_settings[k] = list(v)
        else:
            try:
                cleaned_settings[k] = float(v) if v is not None else None
            except Exception:
                cleaned_settings[k] = v
    
    # Load existing
    existing = {}
    if os.path.exists(base_file):
        try:
            with open(base_file, 'r', encoding='utf-8-sig') as f:
                existing = json.load(f)
        except Exception:
            existing = {}
    
    if key is None:
        # Keep legacy flat format
        data_to_write = cleaned_settings
    else:
        # Ensure mapping format { key: settings }
        if _is_legacy_flat_settings(existing):
            # Convert legacy flat content into a mapping under a default key
            existing = {'default': existing}
        elif not isinstance(existing, dict):
            existing = {}
        existing[key] = cleaned_settings
        data_to_write = existing
    
    try:
        with open(base_file, 'w', newline='\r\n', encoding='utf-8-sig') as f:
            json.dump(data_to_write, f, indent=4, separators=(',', ': '), ensure_ascii=False)
        print(f"Saved plot settings to {base_file}{('::' + key) if key else ''}")
    except Exception as e:
        print(f"Warning: could not save plot settings to {base_file}: {e}")

def load_plot_settings(filename='InteractivePlotWindowMultiAxis.json'):
    """Load settings from JSON.
    If filename contains '::KEY', load that profile from the shared JSON file.
    Returns None if not found.
    """
    base_file, key = _split_settings_filename_key(filename)
    try:
        with open(base_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        # If no key requested, accept flat or return as-is
        if key is None:
            # Normalize series_visible booleans for flat content
            if isinstance(data, dict) and 'series_visible' in data and not any(isinstance(x, bool) for x in data['series_visible']):
                data['series_visible'] = [bool(x) for x in data['series_visible']]
            return data
        # Key requested: ensure mapping
        if _is_legacy_flat_settings(data):
            # Legacy flat file but a key was requested; no keyed profile exists yet
            return None
        if isinstance(data, dict) and key in data:
            prof = data[key]
            if isinstance(prof, dict) and 'series_visible' in prof:
                prof['series_visible'] = [bool(x) for x in prof['series_visible']]
            return prof
        print(f"No saved settings found for key '{key}' in {base_file}")
        return None
    except FileNotFoundError:
        print(f'No saved settings found at {base_file}')
        return None
    except Exception as e:
        print(f'Warning: could not load plot settings from {base_file}: {e}')
        return None

class ManualXAxisDialog(QDialog):
    def __init__(self, parent=None, current_mode=None):
        super().__init__(parent)
        self.setWindowTitle("Manual X-Axis Mode")
        self.combo = QComboBox(self)
        self.combo.addItems([
            "Year",
            "Month",
            "Week",
            "Day",
            "Hour",
            "Minute",
        ])
        if current_mode is not None:
            idx = self.combo.findText(current_mode)
            if idx >= 0:
                self.combo.setCurrentIndex(idx)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select manual x-axis mode:"))
        layout.addWidget(self.combo)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_mode(self):
        return self.combo.currentText()

class SeriesFormatDialog(QDialog):
    """Dialog for configuring series line style, marker, marker size, and color."""
    def __init__(self, parent=None, series_name="", current_format=None, current_color=None):
        super().__init__(parent)
        self.setWindowTitle(f"Format Series: {series_name}")
        self.selected_color = current_color
        
        # Default values
        if current_format is None:
            current_format = {'linestyle': '-', 'marker': '', 'markersize': 3}
        
        layout = QVBoxLayout(self)
        
        # Color selection
        from PyQt6.QtWidgets import QHBoxLayout
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_btn = QPushButton("Choose Color")
        if current_color is not None:
            # Convert RGBA tuple to hex for display
            r = int(current_color[0] * 255)
            g = int(current_color[1] * 255)
            b = int(current_color[2] * 255)
            color_hex = f'#{r:02x}{g:02x}{b:02x}'
            self.color_btn.setStyleSheet(f"background-color: {color_hex}; color: white;")
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        layout.addLayout(color_layout)
        
        # Line style selection
        layout.addWidget(QLabel("Line Style:"))
        self.linestyle_combo = QComboBox(self)
        self.linestyle_combo.addItems([
            "Solid (-)",
            "Dashed (--)",
            "Dash-dot (-.)",
            "Dotted (:)",
            "None"
        ])
        linestyle_map = {'-': 0, '--': 1, '-.': 2, ':': 3, '': 4}
        self.linestyle_combo.setCurrentIndex(linestyle_map.get(current_format.get('linestyle', '-'), 0))
        layout.addWidget(self.linestyle_combo)
        
        # Marker selection
        layout.addWidget(QLabel("Marker:"))
        self.marker_combo = QComboBox(self)
        self.marker_combo.addItems([
            "None",
            "Circle (o)",
            "Square (s)",
            "Triangle (^)",
            "Diamond (D)",
            "Plus (+)",
            "Cross (x)",
            "Star (*)",
            "Point (.)"
        ])
        marker_map = {'': 0, 'o': 1, 's': 2, '^': 3, 'D': 4, '+': 5, 'x': 6, '*': 7, '.': 8}
        self.marker_combo.setCurrentIndex(marker_map.get(current_format.get('marker', ''), 0))
        layout.addWidget(self.marker_combo)
        
        # Marker size
        from PyQt6.QtWidgets import QSpinBox
        layout.addWidget(QLabel("Marker Size:"))
        self.markersize_spin = QSpinBox(self)
        self.markersize_spin.setRange(1, 20)
        self.markersize_spin.setValue(int(current_format.get('markersize', 3)))
        layout.addWidget(self.markersize_spin)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def choose_color(self):
        """Open color picker dialog."""
        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor
        
        # Convert current color to QColor if available
        initial_color = QColor(255, 255, 255)
        if self.selected_color is not None:
            r = int(self.selected_color[0] * 255)
            g = int(self.selected_color[1] * 255)
            b = int(self.selected_color[2] * 255)
            initial_color = QColor(r, g, b)
        
        color = QColorDialog.getColor(initial_color, self, "Choose Series Color")
        if color.isValid():
            # Store as RGBA tuple (0-1 range) to match matplotlib format
            self.selected_color = (color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0, 1.0)
            color_hex = f'#{color.red():02x}{color.green():02x}{color.blue():02x}'
            self.color_btn.setStyleSheet(f"background-color: {color_hex}; color: white;")
    
    def get_format(self):
        """Return selected format as dict."""
        linestyle_values = ['-', '--', '-.', ':', '']
        marker_values = ['', 'o', 's', '^', 'D', '+', 'x', '*', '.']
        
        return {
            'linestyle': linestyle_values[self.linestyle_combo.currentIndex()],
            'marker': marker_values[self.marker_combo.currentIndex()],
            'markersize': self.markersize_spin.value()
        }
    
    def get_color(self):
        """Return selected color as RGBA tuple."""
        return self.selected_color


class ReorderAxesDialog(QDialog):
    """Dialog for reordering axes with move left/right/make primary buttons."""
    def __init__(self, parent=None, unit_list=None):
        super().__init__(parent)
        self.setWindowTitle("Reorder Axes")
        self.parent_window = parent
        self.unit_list = unit_list if unit_list else []
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Reorder axes by moving units left or right:"))
        
        # Create list widget with move buttons for each unit
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QHBoxLayout
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        
        # Populate list with units
        self.refresh_list()
        
        layout.addWidget(self.list_widget)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.move_left_btn = QPushButton("← Move Left")
        self.move_left_btn.clicked.connect(self.move_left)
        button_layout.addWidget(self.move_left_btn)
        
        self.move_right_btn = QPushButton("Move Right →")
        self.move_right_btn.clicked.connect(self.move_right)
        button_layout.addWidget(self.move_right_btn)
        
        self.make_primary_btn = QPushButton("⭐ Make Primary")
        self.make_primary_btn.clicked.connect(self.make_primary)
        button_layout.addWidget(self.make_primary_btn)
        
        layout.addLayout(button_layout)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.update_button_states()
        self.list_widget.currentRowChanged.connect(self.update_button_states)
    
    def refresh_list(self):
        """Refresh the list widget with current unit order."""
        self.list_widget.clear()
        for idx, unit in enumerate(self.unit_list):
            if idx == 0:
                self.list_widget.addItem(f"⭐ {unit} (Primary)")
            else:
                self.list_widget.addItem(f"   {unit}")
    
    def update_button_states(self):
        """Enable/disable buttons based on selection."""
        current_row = self.list_widget.currentRow()
        self.move_left_btn.setEnabled(current_row > 0)
        self.move_right_btn.setEnabled(0 <= current_row < len(self.unit_list) - 1)
        self.make_primary_btn.setEnabled(current_row > 0)
    
    def move_left(self):
        """Move selected unit left."""
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            unit = self.unit_list[current_row]
            self.parent_window.reorder_unit(unit, -1)
            self.refresh_list()
            self.list_widget.setCurrentRow(current_row - 1)
    
    def move_right(self):
        """Move selected unit right."""
        current_row = self.list_widget.currentRow()
        if 0 <= current_row < len(self.unit_list) - 1:
            unit = self.unit_list[current_row]
            self.parent_window.reorder_unit(unit, 1)
            self.refresh_list()
            self.list_widget.setCurrentRow(current_row + 1)
    
    def make_primary(self):
        """Make selected unit the primary axis."""
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            unit = self.unit_list[current_row]
            self.parent_window.move_unit_to_primary(unit)
            self.refresh_list()
            self.list_widget.setCurrentRow(0)


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
        self.move_left_action = self.addAction('<', self.moveLeft)
        self.move_left_action.setToolTip(r'Move left 25% of the current x-axis range')
        self.addSeparator()
        self.move_right_action = self.addAction('>', self.moveRight)
        self.move_right_action.setToolTip(r'Move right 25% of the current x-axis range')
        self.addSeparator()
        self.reset_x_action = self.addAction('Reset X', self.plot_window.resetXAxis)
        self.reset_x_action.setToolTip('Reset X-axis to min <-> max')
        self.addSeparator()
        self.zoom_in_action = self.addAction('><', self.plot_window.zoom_in_x)
        self.zoom_in_action.setToolTip('Zoom in X-axis')
        self.addSeparator()
        self.zoom_out_action = self.addAction('<>', self.plot_window.zoom_out_x)
        self.zoom_out_action.setToolTip('Zoom out X-axis')
        self.addSeparator()
        
        # Add Measure button
        self.measure_btn = QPushButton("Measure")
        self.measure_btn.setCheckable(True)
        self.measure_btn.clicked.connect(self.plot_window.toggle_measure_mode)
        self.addWidget(self.measure_btn)
        self.addSeparator()

        # Add Manual/Auto X-Axis toggle button
        self.manual_xaxis_btn = QPushButton("Manual X-Axis")
        self.manual_xaxis_btn.setCheckable(True)
        self.manual_xaxis_btn.clicked.connect(self.toggle_manual_xaxis)
        self.addWidget(self.manual_xaxis_btn)

        # Add keyboard shortcuts
        self.shortcut_pan = QShortcut(QKeySequence("P"), self)
        self.shortcut_pan.activated.connect(self.pan)

        self.shortcut_zoom = QShortcut(QKeySequence("Z"), self)
        self.shortcut_zoom.activated.connect(self.zoom)

        # Add QLabel to display xAxisLen
        self.xAxisLenLabel = QLabel("xAxisLen: N/A")
        self.addWidget(self.xAxisLenLabel)
        self.addSeparator()

        # Add QLabel to display mode (Auto/Manual)
        self.modeLabel = QLabel("Mode: Auto")
        self.addWidget(self.modeLabel)
        self.addSeparator()

        # Add QLabel to display locator settings
        self.locatorLabel = QLabel("Locator: N/A")
        self.addWidget(self.locatorLabel)

    def toggle_manual_xaxis(self):
        if self.manual_xaxis_btn.isChecked():
            # Show dialog to select manual mode
            dlg = ManualXAxisDialog(self, getattr(self.plot_window, 'manual_xaxis_mode', None))
            if dlg.exec() == QDialog.DialogCode.Accepted:
                mode = dlg.get_mode()
                self.plot_window.manual_xaxis_mode = mode
                self.plot_window.manual_xaxis = True
                self.manual_xaxis_btn.setText("Auto X-Axis")
                self.modeLabel.setText(f"Mode: Manual ({mode})")
            else:
                # Cancelled, revert button
                self.manual_xaxis_btn.setChecked(False)
                return
        else:
            # Switching back to Auto mode
            self.plot_window.manual_xaxis = False
            self.plot_window.manual_xaxis_mode = None
            self.manual_xaxis_btn.setText("Manual X-Axis")
            self.manual_xaxis_btn.setChecked(False)  # Ensure button is unchecked
            self.modeLabel.setText("Mode: Auto")
        self.plot_window.reformatXAxis()
        self.plot_window.canvas.draw()
        self.update_locator_info()

    def autoscale(self):
        """Autoscale both X and Y axes for all units."""
        if hasattr(self.plot_window, 'axes') and self.plot_window.axes:
            primary_axis = list(self.plot_window.axes.values())[0]
            primary_axis.autoscale(axis='both')
            self.canvas.draw()
            self.update_xAxisLen()
            self.plot_window.save_current_settings()

    def autoscaleLeftY(self):
        """Autoscale Y-axis for the primary (first) unit."""
        if not hasattr(self.plot_window, 'axes') or not self.plot_window.axes:
            return
        
        # Get the first unit (primary/left axis)
        first_unit = self.plot_window.unit_list[0] if self.plot_window.unit_list else None
        if not first_unit or first_unit not in self.plot_window.axes:
            return
            
        axis = self.plot_window.axes[first_unit]
        unit_cols = self.plot_window.axis_groups[first_unit]
        all_cols = list(self.plot_window.df_data.columns)
        
        # Find which series are visible for this unit
        visible_series = []
        for col in unit_cols:
            series_idx = all_cols.index(col)
            if series_idx < len(self.plot_window.series_visible) and self.plot_window.series_visible[series_idx]:
                visible_series.append(col)
        
        if not visible_series:
            return
        
        # Get current x-axis limits
        xlim = axis.get_xlim()
        xlim = [mdates.num2date(x).replace(tzinfo=None) for x in xlim]
        
        # Select data within x-range for visible series
        selected_data = self.plot_window.df_data[visible_series]
        selected_data = selected_data[(selected_data.index >= xlim[0]) & (selected_data.index <= xlim[1])]
        
        if selected_data.empty:
            return
        
        # Calculate Y limits with some padding
        y_min = selected_data.min().min()
        y_max = selected_data.max().max()
        y_range = y_max - y_min
        padding = y_range * 0.05  # 5% padding
        
        axis.set_ylim(y_min - padding, y_max + padding)
        self.canvas.draw()
        self.plot_window.save_current_settings()

    def autoscaleRightY(self):
        """Autoscale Y-axis for all secondary (right-side) units."""
        if not hasattr(self.plot_window, 'axes') or not self.plot_window.axes:
            return
        
        # Get all units except the first one (all right-side axes)
        right_units = self.plot_window.unit_list[1:] if len(self.plot_window.unit_list) > 1 else []
        
        if not right_units:
            return
        
        all_cols = list(self.plot_window.df_data.columns)
        
        # Autoscale each right-side axis
        for unit in right_units:
            # Skip units that don't have an axis (all series hidden)
            if unit not in self.plot_window.axes:
                continue
                
            axis = self.plot_window.axes[unit]
            unit_cols = self.plot_window.axis_groups[unit]
            
            # Find which series are visible for this unit
            visible_series = []
            for col in unit_cols:
                series_idx = all_cols.index(col)
                if series_idx < len(self.plot_window.series_visible) and self.plot_window.series_visible[series_idx]:
                    visible_series.append(col)
            
            if not visible_series:
                continue
            
            # Get current x-axis limits
            xlim = axis.get_xlim()
            xlim = [mdates.num2date(x).replace(tzinfo=None) for x in xlim]
            
            # Select data within x-range for visible series
            selected_data = self.plot_window.df_data[visible_series]
            selected_data = selected_data[(selected_data.index >= xlim[0]) & (selected_data.index <= xlim[1])]
            
            if selected_data.empty:
                continue
            
            # Calculate Y limits with some padding
            y_min = selected_data.min().min()
            y_max = selected_data.max().max()
            y_range = y_max - y_min
            padding = y_range * 0.05  # 5% padding
            
            axis.set_ylim(y_min - padding, y_max + padding)
        
        self.canvas.draw()
        self.plot_window.save_current_settings()

    def pan(self):
        super().pan()
        self.plot_window.reformatXAxis()
        self.update_xAxisLen()
        self.update_locator_info()
        self.plot_window.save_current_settings()

    def zoom(self):
        super().zoom()
        self.plot_window.reformatXAxis()
        self.update_xAxisLen()
        self.update_locator_info()
        self.plot_window.save_current_settings()

    def update_xAxisLen(self):
        ax1 = self.canvas.figure.gca()
        xlim = ax1.get_xlim()
        xAxisLen = xlim[1] - xlim[0]
        if hasattr(self, 'xAxisLenLabel') and self.xAxisLenLabel is not None:
            self.xAxisLenLabel.setText(f"xAxisLen: {xAxisLen:.2f}")

    def update_locator_info(self):
        """Update the locator label with current major/minor locator settings"""
        if hasattr(self, 'locatorLabel') and self.locatorLabel is not None:
            if hasattr(self.plot_window, 'current_locator_info'):
                self.locatorLabel.setText(self.plot_window.current_locator_info)
            else:
                self.locatorLabel.setText("Locator: N/A")
    
    def moveLeft(self):
        if hasattr(self.plot_window, 'axes') and self.plot_window.axes:
            primary_axis = list(self.plot_window.axes.values())[0]
            xlim = primary_axis.get_xlim()
            step = (xlim[1] - xlim[0]) * 0.25  # Move 25% of the current x-axis range
            primary_axis.set_xlim(xlim[0] - step, xlim[1] - step)
            self.canvas.draw()
            self.update_xAxisLen()
            self.plot_window.save_current_settings()

    def moveRight(self):
        if hasattr(self.plot_window, 'axes') and self.plot_window.axes:
            primary_axis = list(self.plot_window.axes.values())[0]
            xlim = primary_axis.get_xlim()
            step = (xlim[1] - xlim[0]) * 0.25  # Move 25% of the current x-axis range
            primary_axis.set_xlim(xlim[0] + step, xlim[1] + step)
            self.canvas.draw()
            self.update_xAxisLen()
            self.plot_window.save_current_settings()

class InteractivePlotWindowMultiAxis(QMainWindow):
    def __init__(self, df_data, WindowTitle=None, initial_visible=None, settings_file=None):
        """
        Multi-axis interactive plot window.
        
        Args:
            df_data: DataFrame with all series. Column names should end with [unit] for automatic axis grouping.
                     Example: "Flow [m3/h]", "Level [m]", "Temp [°C]"
            WindowTitle: Window title string
            initial_visible: List of initially visible series names
            settings_file: Path to JSON settings file
        """
        super().__init__()
        if WindowTitle is None:
            self.setWindowTitle("Interactive Plot - Multi Axis")
        else:
            self.setWindowTitle(WindowTitle)

        # Store the DataFrame
        self.df_data = df_data if df_data is not None else pd.DataFrame()
        
        # Extract units from column names and group series by unit
        self.axis_groups, self.series_units = self._extract_units_and_group()
        self.unit_list = list(self.axis_groups.keys())
        
        # Settings file path (default or custom)
        self.settings_file = settings_file if settings_file is not None else 'InteractivePlotWindowMultiAxis.json'
        
        # Flag to check if it's the initial plot
        self.initial_plot = True

        # Manual/auto x-axis state
        self.manual_xaxis = False
        self.manual_xaxis_mode = None

        # Auto-update state for series visibility
        self.auto_update = False

        # Dark mode state
        self.dark_mode = False
        
        # Crosshair enabled state
        self.crosshair_enabled = False
        
        # Measurement tool state
        self.measure_enabled = False
        self.measure_start_point = None
        self.measure_end_point = None
        self.measure_line = None
        self.measure_annotation = None
        self.measure_start_marker = None
        self.measure_end_marker = None
        self.measure_start_crosshair_h = None
        self.measure_start_crosshair_v = None
        self.measure_end_crosshair_h = None
        self.measure_end_crosshair_v = None

        # Toggle button states per unit
        self.toggle_states = {unit: True for unit in self.unit_list}
        self.toggle_all_state = True  # State for toggle all button

        # Persistent axis limits for all units (even when hidden)
        # This ensures limits are preserved when axes are hidden/shown
        self.unit_xlims = {}
        self.unit_ylims = {}

        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Create Figure and Canvas
        # Use constrained_layout and tighter subplot margins to reduce border whitespace
        self.fig = Figure(constrained_layout=True)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = CustomNavigationToolbar(self.canvas, self, plot_window=self)

        # Determine columns and initial visibility
        all_cols = list(self.df_data.columns)

        # Generate default color palette for all series
        import matplotlib.pyplot as plt
        total_series = len(all_cols)
        
        if total_series <= 9:
            default_colors = [plt.cm.Set1(i) for i in range(total_series)]
        elif total_series <= 17:
            default_colors = [plt.cm.Set1(i % 9) for i in range(9)] + [plt.cm.Dark2(i % 8) for i in range(total_series - 9)]
        else:
            default_colors = ([plt.cm.Set1(i % 9) for i in range(9)] + 
                     [plt.cm.Dark2(i % 8) for i in range(8)] +
                     [plt.cm.tab10(i % 10) for i in range(max(0, total_series - 17))])

        # Try to load saved settings before setting up visibility and checkboxes
        self.saved_settings = load_plot_settings(self.settings_file)
        
        # Load saved axis limits for all units (including potentially hidden ones)
        if self.saved_settings:
            for unit in self.unit_list:
                xlim_key = f'xlim_{unit}'
                ylim_key = f'ylim_{unit}'
                if xlim_key in self.saved_settings:
                    self.unit_xlims[unit] = self.saved_settings[xlim_key]
                if ylim_key in self.saved_settings:
                    self.unit_ylims[unit] = self.saved_settings[ylim_key]
        
        # Load saved colors or use defaults
        self.series_colors = []
        saved_colors = self.saved_settings.get('series_colors', []) if self.saved_settings else []
        for i in range(total_series):
            if i < len(saved_colors) and saved_colors[i] is not None:
                # Convert saved color (list) back to tuple
                self.series_colors.append(tuple(saved_colors[i]))
            else:
                self.series_colors.append(default_colors[i])
        
        # Restore auto_update state from settings if available
        if self.saved_settings and 'auto_update' in self.saved_settings:
            self.auto_update = bool(self.saved_settings['auto_update'])
        
        # Initialize series formatting and visibility with robust name-based matching
        # Default format: line with no markers
        default_format = {'linestyle': '-', 'marker': '', 'markersize': 3}

        saved_formats_list = None
        if isinstance(self.saved_settings, dict):
            saved_formats_list = self.saved_settings.get('series_formats', None)

        # Build name->format map if possible
        saved_by_name = {}
        if isinstance(saved_formats_list, list):
            for item in saved_formats_list:
                if isinstance(item, dict) and 'series_name' in item:
                    saved_by_name[item['series_name']] = item

        # Prepare containers
        self.series_formats = []
        self.series_visible = []

        for i, col in enumerate(all_cols):
            # Pick saved entry by name, else by index if lengths match, else None
            saved_entry = None
            if col in saved_by_name:
                saved_entry = saved_by_name[col]
            elif isinstance(saved_formats_list, list) and i < len(saved_formats_list):
                saved_entry = saved_formats_list[i]

            # Visibility: prefer per-entry 'visible', else old 'series_visible', else True
            if isinstance(saved_entry, dict) and 'visible' in saved_entry:
                self.series_visible.append(bool(saved_entry.get('visible', 1)))
            elif isinstance(self.saved_settings, dict) and isinstance(self.saved_settings.get('series_visible'), list) and i < len(self.saved_settings['series_visible']):
                self.series_visible.append(bool(self.saved_settings['series_visible'][i]))
            else:
                # Fall back to initial_visible parameter
                if initial_visible is None:
                    self.series_visible.append(True)
                elif isinstance(initial_visible, (list, tuple)) and i < len(initial_visible):
                    self.series_visible.append(bool(initial_visible[i]))
                else:
                    try:
                        visible_set = set(initial_visible)
                        self.series_visible.append(col in visible_set)
                    except Exception:
                        self.series_visible.append(True)

            # Format: compose from saved or default
            if isinstance(saved_entry, dict):
                clean_fmt = {
                    'linestyle': saved_entry.get('linestyle', default_format['linestyle']),
                    'marker': saved_entry.get('marker', default_format['marker']),
                    'markersize': int(saved_entry.get('markersize', default_format['markersize'])),
                }
                self.series_formats.append(clean_fmt)
            else:
                self.series_formats.append(default_format.copy())

        # Initialize checkboxes list
        self.checkboxes = []
        
        # Add auto-update toggle and manual update button at the top
        control_layout = QHBoxLayout()
        self.auto_update_checkbox = QCheckBox("Auto-update chart")
        self.auto_update_checkbox.setChecked(self.auto_update)  # Use the restored value
        self.auto_update_checkbox.stateChanged.connect(self.toggle_auto_update)
        control_layout.addWidget(self.auto_update_checkbox)
        
        self.manual_update_btn = QPushButton("Update Chart")
        self.manual_update_btn.clicked.connect(self.manual_update_chart)
        self.manual_update_btn.setEnabled(not self.auto_update)  # Set based on restored value
        control_layout.addWidget(self.manual_update_btn)
        
        self.dark_mode_btn = QPushButton("Dark Mode")
        self.dark_mode_btn.setCheckable(True)
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        control_layout.addWidget(self.dark_mode_btn)
        
        self.toggle_all_btn = QPushButton("Toggle All")
        self.toggle_all_btn.clicked.connect(self.toggle_all_series)
        control_layout.addWidget(self.toggle_all_btn)
        
        self.crosshair_btn = QPushButton("Crosshair")
        self.crosshair_btn.setCheckable(True)
        self.crosshair_btn.setChecked(False)
        self.crosshair_btn.clicked.connect(self.toggle_crosshair)
        control_layout.addWidget(self.crosshair_btn)
        
        self.reorder_axes_btn = QPushButton("Reorder Axes")
        self.reorder_axes_btn.clicked.connect(self.show_reorder_axes_dialog)
        control_layout.addWidget(self.reorder_axes_btn)
        
        self.scale_m3_btn = QPushButton("Scale m³ to m*m²")
        self.scale_m3_btn.clicked.connect(self.scale_m3_to_match_mm2)
        control_layout.addWidget(self.scale_m3_btn)
        
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Build checkboxes grouped by unit in framed boxes
        from PyQt6.QtWidgets import QGridLayout, QFrame
        from calculate_button_text_metrics import calculate_optimal_rows
        import math
        
        # Create horizontal layout for unit sections
        series_layout = QHBoxLayout()

        # Define colors for different units (cycle through these)
        unit_colors = [
            ('#e8f4f8', '#0066cc', '#003366'),  # Blue
            ('#fff5e6', '#cc6600', '#663300'),  # Orange
            ('#e8f8e8', '#00cc66', '#003300'),  # Green
            ('#f8e8f8', '#cc00cc', '#660066'),  # Purple
            ('#f8f8e8', '#cccc00', '#666600'),  # Yellow
        ]
        
        # Create a frame for each unit group
        for unit_idx, unit in enumerate(self.unit_list):
            unit_cols = self.axis_groups[unit]
            if len(unit_cols) == 0:
                continue
                
            # Calculate optimal number of rows for this unit using pixel width
            num_rows = self._calculate_rows_by_pixel_width(unit_cols, available_width_per_column=400)
            num_cols = math.ceil(len(unit_cols) / num_rows)
            
            # Get color scheme for this unit (cycle through colors)
            bg_color, border_color, text_color = unit_colors[unit_idx % len(unit_colors)]
            
            # Create frame for this unit
            unit_frame = QFrame()
            unit_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 2px solid {border_color};
                    border-radius: 5px;
                    padding: 5px;
                }}
            """)
            # Add context menu to unit frame for reordering
            unit_frame.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            unit_frame.customContextMenuRequested.connect(lambda pos, u=unit: self.show_unit_context_menu(pos, u, unit_frame))
            
            unit_layout = QGridLayout(unit_frame)
            unit_layout.setSpacing(2)
            unit_layout.setContentsMargins(5, 5, 5, 5)
            
            # Add checkboxes for this unit's series
            for i, col in enumerate(unit_cols):
                # Find the index of this column in all_cols
                series_idx = all_cols.index(col)
                
                row = i % num_rows
                col_pos = i // num_rows
                checkbox = QCheckBox(f"{col}")
                
                # Get series color and convert to hex
                series_color_hex = self._rgba_to_hex(self.series_colors[series_idx])
                
                checkbox.setStyleSheet(f"""
                    QCheckBox {{ 
                        background-color: transparent; 
                        color: {text_color};
                        spacing: 5px;
                    }}
                    QCheckBox::indicator {{
                        width: 13px;
                        height: 13px;
                        border: 2px solid {series_color_hex};
                        border-radius: 3px;
                        background-color: white;
                    }}
                    QCheckBox::indicator:checked {{
                        background-color: {series_color_hex};
                        border: 2px solid {series_color_hex};
                    }}
                """)
                
                # Tooltip with basic info and stats
                try:
                    s = self.df_data[col]
                    tip_lines = [f"{col}", f"Unit: {unit}"]
                    if pd.api.types.is_numeric_dtype(s):
                        nn = int(s.count())
                        s_valid = s.dropna()
                        if not s_valid.empty:
                            s_min = s_valid.min()
                            s_max = s_valid.max()
                            tip_lines += [
                                f"Non-null: {nn:,}",
                                f"Min: {s_min:.6g}",
                                f"Max: {s_max:.6g}"
                            ]
                        else:
                            tip_lines += [f"Non-null: {nn:,}"]
                    else:
                        tip_lines += [f"Type: {str(s.dtype)}", f"Non-null: {int(s.count()):,}"]
                    checkbox.setToolTip("\n".join(tip_lines))
                except Exception:
                    checkbox.setToolTip(f"{col} ({unit})")
                
                checkbox.blockSignals(True)
                checkbox.setChecked(bool(self.series_visible[series_idx]))
                checkbox.blockSignals(False)
                checkbox.stateChanged.connect(self.create_toggle_function(series_idx))
                checkbox.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                checkbox.customContextMenuRequested.connect(self.create_format_menu(series_idx, col))
                unit_layout.addWidget(checkbox, row, col_pos)
                self.checkboxes.append(checkbox)
            
            # Set size policy
            unit_frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
            series_layout.addWidget(unit_frame, stretch=num_cols)

        layout.addLayout(series_layout)
        
        # Initialize crosshair state (click-to-place)
        self.crosshair_vline = None
        self.crosshair_hline = None
        self.crosshair_hline_right = None
        self.mouse_pressed = False
        
        # Connect mouse events for click-and-drag crosshair
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # Initial plot
        self.plot()

    def _extract_units_and_group(self):
        """
        Extract units from column names and group series by unit.
        Column names should end with [unit], e.g., "Flow [m3/h]"
        
        Returns:
            axis_groups: dict mapping unit -> list of series names
            series_units: dict mapping series name -> unit
        """
        axis_groups = {}
        series_units = {}
        
        for col in self.df_data.columns:
            # Try to extract unit from [unit] pattern at end of name
            match = re.search(r'\[([^\]]+)\]\s*', col) #End of string: re.search(r'\[([^\]]+)\]\s*$', col)
            if match:
                unit = match.group(1).strip()
            else:
                unit = 'default'  # Series without unit go to default axis
            
            if unit not in axis_groups:
                axis_groups[unit] = []
            axis_groups[unit].append(col)
            series_units[col] = unit
        
        return axis_groups, series_units

    def closeEvent(self, event):
        """Save settings when window is closed"""
        self.save_current_settings()
        super().closeEvent(event)

    def save_current_settings(self):
        """Save current axis limits and other settings"""
        if not hasattr(self, 'axes'):
            return
        
        # Update unit_xlims and unit_ylims with current visible axes
        for unit, axis in self.axes.items():
            self.unit_xlims[unit] = list(axis.get_xlim())
            self.unit_ylims[unit] = list(axis.get_ylim())
        
        # Build series_formats with names and visibility for readability
        all_cols = list(self.df_data.columns)
        
        series_formats_with_names = []
        for i, fmt in enumerate(self.series_formats):
            name = all_cols[i] if i < len(all_cols) else f"Series {i}"
            visible_val = 1 if (i < len(self.series_visible) and self.series_visible[i]) else 0
            # Build dict with desired key order: series_name first, then visible, then known style keys
            ordered = {
                'series_name': name,
                'visible': visible_val,
            }
            # Preferred order for style keys
            for key in ['linestyle', 'marker', 'markersize']:
                if key in fmt:
                    ordered[key] = fmt[key]
            # Append any other keys from fmt that aren't already included
            for key, value in fmt.items():
                if key not in ordered:
                    ordered[key] = value
            series_formats_with_names.append(ordered)
        
        # Save series colors as lists (tuples aren't JSON serializable)
        series_colors_list = [list(color) if color is not None else None for color in self.series_colors]
            
        settings = {
            'auto_update': self.auto_update,
            'series_formats': series_formats_with_names,
            'series_colors': series_colors_list
        }
        
        # Save axis limits for ALL units (including hidden ones)
        # Use persistent dictionaries that maintain limits even when axes are hidden
        for unit in self.unit_list:
            if unit in self.unit_xlims:
                settings[f'xlim_{unit}'] = self.unit_xlims[unit]
            if unit in self.unit_ylims:
                settings[f'ylim_{unit}'] = self.unit_ylims[unit]
            
        save_plot_settings(settings, self.settings_file)

    def _rgba_to_hex(self, rgba_tuple):
        """Convert matplotlib RGBA tuple (0-1 range) to hex color string."""
        r = int(rgba_tuple[0] * 255)
        g = int(rgba_tuple[1] * 255)
        b = int(rgba_tuple[2] * 255)
        return f'#{r:02x}{g:02x}{b:02x}'

    def _update_checkbox_colors(self):
        """Update checkbox border colors to match current series_colors after reordering."""
        all_cols = list(self.df_data.columns)
        
        # Find which unit each series belongs to for text color
        unit_colors = [
            ('#e8f4f8', '#0066cc', '#003366'),  # Blue
            ('#f8e8f8', '#cc0066', '#660033'),  # Pink/Magenta
            ('#e8f8e8', '#00cc66', '#006633'),  # Green
            ('#f8f4e8', '#cc6600', '#663300'),  # Orange
            ('#f0e8f8', '#6600cc', '#330066'),  # Purple
            ('#e8f8f4', '#00cccc', '#006666'),  # Cyan
        ]
        
        for i, checkbox in enumerate(self.checkboxes):
            if i < len(all_cols) and i < len(self.series_colors):
                col = all_cols[i]
                series_color_hex = self._rgba_to_hex(self.series_colors[i])
                
                # Find which unit this series belongs to
                unit = self.series_units.get(col, 'default')
                unit_idx = self.unit_list.index(unit) if unit in self.unit_list else 0
                bg_color, border_color, text_color = unit_colors[unit_idx % len(unit_colors)]
                
                # Update the checkbox stylesheet with the correct series color
                checkbox.setStyleSheet(f"""
                    QCheckBox {{ 
                        background-color: transparent; 
                        color: {text_color};
                        spacing: 5px;
                    }}
                    QCheckBox::indicator {{
                        width: 13px;
                        height: 13px;
                        border: 2px solid {series_color_hex};
                        border-radius: 3px;
                        background-color: white;
                    }}
                    QCheckBox::indicator:checked {{
                        background-color: {series_color_hex};
                        border: 2px solid {series_color_hex};
                    }}
                """)

    def _calculate_rows_by_pixel_width(self, series_names, available_width_per_column=500):
        """Calculate optimal rows based on estimated pixel width of labels.
        
        Args:
            series_names: List of series names to display
            available_width_per_column: Target width per column in pixels (default 400)
        
        Returns:
            Number of rows needed (constrained between 2 and 6)
        """
        from PyQt6.QtGui import QFontMetrics
        from PyQt6.QtWidgets import QApplication
        
        # Get default font metrics
        font = QApplication.font()
        metrics = QFontMetrics(font)
        
        # Estimate width for each series name (checkbox + padding + text)
        total_width = 0
        max_width = 0
        for name in series_names:
            # 20px for checkbox, 10px spacing, text width, 20px right padding
            text_width = metrics.horizontalAdvance(name)
            item_width = 20 + 10 + text_width + 20
            total_width += item_width
            max_width = max(max_width, item_width)
        
        # Calculate how many columns we can fit
        # Start by assuming we want items around available_width_per_column wide
        estimated_columns = max(1, int(total_width / (available_width_per_column * len(series_names))))
        estimated_columns = max(1, estimated_columns)
        
        # Calculate rows needed for this number of columns
        import math
        calculated_rows = math.ceil(len(series_names) / estimated_columns)
        
        # If we have very long labels, ensure we don't make rows too tall
        # by limiting columns if a single item is very wide
        if max_width > available_width_per_column * 1.5:
            # Force more rows to accommodate wide labels
            calculated_rows = max(calculated_rows, 4)
        
        # Constrain to reasonable range
        return max(2, min(6, calculated_rows))

    def create_toggle_function(self, index):
        # Accept the state argument from stateChanged signal and set the visibility directly.
        def toggle(state):
            # state is an int/Qt.Checked; convert to boolean
            self.series_visible[index] = bool(state)
            # Only re-plot and save if auto-update is enabled
            if self.auto_update:
                self.plot()
                self.save_current_settings()
        return toggle
    
    def create_format_menu(self, index, series_name):
        """Create a context menu handler for formatting a series."""
        def show_format_dialog(pos):
            from PyQt6.QtWidgets import QMenu
            menu = QMenu()
            format_action = menu.addAction("Format Line/Marker/Color...")
            action = menu.exec(self.checkboxes[index].mapToGlobal(pos))
            
            if action == format_action:
                # Show format dialog with current color
                current_color = self.series_colors[index] if index < len(self.series_colors) else None
                dlg = SeriesFormatDialog(self, series_name, self.series_formats[index], current_color)
                if dlg.exec() == QDialog.DialogCode.Accepted:
                    self.series_formats[index] = dlg.get_format()
                    # Update color if changed
                    new_color = dlg.get_color()
                    if new_color is not None and index < len(self.series_colors):
                        self.series_colors[index] = new_color
                    # Update checkbox color immediately
                    self._update_checkbox_colors()
                    if self.auto_update:
                        self.plot()
                        self.save_current_settings()
        return show_format_dialog

    def show_unit_context_menu(self, pos, unit, widget):
        """Show context menu for unit group to allow reordering."""
        from PyQt6.QtWidgets import QMenu
        menu = QMenu()
        
        current_idx = self.unit_list.index(unit)
        
        # Add menu options
        if current_idx > 0:
            move_left_action = menu.addAction(f"← Move '{unit}' Left")
        else:
            move_left_action = None
            
        if current_idx < len(self.unit_list) - 1:
            move_right_action = menu.addAction(f"Move '{unit}' Right →")
        else:
            move_right_action = None
        
        if len(self.unit_list) > 1:
            menu.addSeparator()
            make_primary_action = menu.addAction(f"⭐ Make '{unit}' Primary Axis (Left)")
        else:
            make_primary_action = None
        
        # Show menu and handle action
        action = menu.exec(widget.mapToGlobal(pos))
        
        if action == move_left_action:
            self.reorder_unit(unit, -1)
        elif action == move_right_action:
            self.reorder_unit(unit, 1)
        elif action == make_primary_action:
            self.move_unit_to_primary(unit)
    
    def show_reorder_axes_dialog(self):
        """Show dialog for reordering axes."""
        dialog = ReorderAxesDialog(self, self.unit_list)
        dialog.exec()
    
    def scale_m3_to_match_mm2(self):
        """Scale the [m3] axis to have the same range as [m*m2] axis, starting from minimum visible value."""
        from PyQt6.QtWidgets import QMessageBox
        m3_unit = 'm3'
        mm2_unit = 'm*m2'
        message_lines = []
        message_lines.append(f"=== Scaling {m3_unit} axis to match {mm2_unit} axis ===\n")

        # Show all available axes and their names
        axes_keys = list(self.axes.keys())
        axes_keys_str = ', '.join([repr(k) for k in axes_keys])
        message_lines.append(f"Available axes: {axes_keys_str}\n")

        # Try to match axis names robustly (case/whitespace-insensitive)
        def normalize(s):
            return s.replace(' ', '').replace('\u200b', '').lower() if isinstance(s, str) else s

        axes_map = {normalize(k): k for k in axes_keys}
        m3_key = axes_map.get(normalize(m3_unit))
        mm2_key = axes_map.get(normalize(mm2_unit))

        if not m3_key or not mm2_key:
            error_msg = f"ERROR: Cannot scale - could not find both '{m3_unit}' and '{mm2_unit}' axes.\n"
            error_msg += f"Available axes: {axes_keys_str}\n"
            QMessageBox.warning(self, "Scaling Error", error_msg)
            print(error_msg)
            return

        m3_axis = self.axes[m3_key]
        mm2_axis = self.axes[mm2_key]
        
        # Get the axes
        m3_axis = self.axes[m3_unit]
        mm2_axis = self.axes[mm2_unit]
        
        # Get current limits before scaling
        m3_ymin_old, m3_ymax_old = m3_axis.get_ylim()
        m3_range_old = m3_ymax_old - m3_ymin_old
        message_lines.append("BEFORE scaling:")
        message_lines.append(f"  {m3_unit} axis: min={m3_ymin_old:.2f}, max={m3_ymax_old:.2f}, range={m3_range_old:.2f}")
        
        # Get current limits of mm2 axis (this is the reference)
        mm2_ymin, mm2_ymax = mm2_axis.get_ylim()
        mm2_range = mm2_ymax - mm2_ymin
        message_lines.append(f"  {mm2_unit} axis: min={mm2_ymin:.2f}, max={mm2_ymax:.2f}, range={mm2_range:.2f}\n")
        
        # Find minimum value in visible m3 series
        all_cols = list(self.df_data.columns)
        m3_cols = self.axis_groups[m3_unit]
        
        m3_min = float('inf')
        has_visible_data = False
        
        for col in m3_cols:
            series_idx = all_cols.index(col)
            if self.series_visible[series_idx]:
                # Get visible data (considering current x-axis limits)
                xlim = m3_axis.get_xlim()
                xlim_dt = [mdates.num2date(x).replace(tzinfo=None) for x in xlim]
                mask = (self.df_data.index >= xlim_dt[0]) & (self.df_data.index <= xlim_dt[1])
                visible_data = self.df_data.loc[mask, col].dropna()
                
                if len(visible_data) > 0:
                    has_visible_data = True
                    col_min = visible_data.min()
                    message_lines.append(f"  Series '{col}': min={col_min:.2f}")
                    m3_min = min(m3_min, col_min)
        
        if not has_visible_data:
            error_msg = f"ERROR: No visible data in {m3_unit} series"
            QMessageBox.warning(self, "Scaling Error", error_msg)
            print(error_msg)
            return
        
        message_lines.append(f"\nMinimum value across all visible {m3_unit} series: {m3_min:.2f}\n")
        
        # Set m3 axis limits: start at minimum value, span same range as mm2
        m3_ymin = m3_min
        m3_ymax = m3_ymin + mm2_range
        
        message_lines.append("AFTER scaling:")
        message_lines.append(f"  {m3_unit} axis: min={m3_ymin:.2f}, max={m3_ymax:.2f}, range={mm2_range:.2f}")
        message_lines.append(f"  {mm2_unit} axis: min={mm2_ymin:.2f}, max={mm2_ymax:.2f}, range={mm2_range:.2f} (unchanged)\n")
        message_lines.append(f"✓ Both axes now have the same range: {mm2_range:.2f}")
        
        m3_axis.set_ylim(m3_ymin, m3_ymax)
        
        # Update persistent limits
        self.unit_ylims[m3_unit] = [m3_ymin, m3_ymax]
        
        # Redraw and save
        self.canvas.draw()
        self.save_current_settings()
        
        # Show success message
        full_message = "\n".join(message_lines)
        print(full_message)
        QMessageBox.information(self, "Scaling Complete", full_message)
    
    def show_axis_context_menu(self, global_pos, unit):

        """Show context menu when right-clicking on an axis in the plot area."""
        from PyQt6.QtWidgets import QMenu
        menu = QMenu()
        
        current_idx = self.unit_list.index(unit)
        
        # Add menu options
        if current_idx > 0:
            move_left_action = menu.addAction(f"← Move '{unit}' Axis Left")
        else:
            move_left_action = None
            
        if current_idx < len(self.unit_list) - 1:
            move_right_action = menu.addAction(f"Move '{unit}' Axis Right →")
        else:
            move_right_action = None
        
        if len(self.unit_list) > 1:
            menu.addSeparator()
            make_primary_action = menu.addAction(f"⭐ Make '{unit}' Primary Axis (Left)")
        else:
            make_primary_action = None
        
        # Show menu at the given global position
        action = menu.exec(global_pos)
        
        if action == move_left_action:
            self.reorder_unit(unit, -1)
        elif action == move_right_action:
            self.reorder_unit(unit, 1)
        elif action == make_primary_action:
            self.move_unit_to_primary(unit)
    
    def reorder_unit(self, unit, direction):
        """Move a unit left (-1) or right (+1) in the axis order."""
        current_idx = self.unit_list.index(unit)
        new_idx = current_idx + direction
        
        # Validate new index
        if new_idx < 0 or new_idx >= len(self.unit_list):
            return
        
        # Swap units in the list
        self.unit_list[current_idx], self.unit_list[new_idx] = self.unit_list[new_idx], self.unit_list[current_idx]
        
        # Rebuild UI and replot
        self.rebuild_ui()
    
    def move_unit_to_primary(self, unit):
        """Move a unit to be the primary (leftmost) axis."""
        current_idx = self.unit_list.index(unit)
        
        if current_idx == 0:
            return  # Already primary
        
        # Move unit to front of list
        self.unit_list.pop(current_idx)
        self.unit_list.insert(0, unit)
        
        # Rebuild UI and replot
        self.rebuild_ui()
    
    def rebuild_ui(self):
        """Rebuild the UI with updated unit order."""
        # Get the main layout
        layout = self.central_widget.layout()
        
        # Find and remove only the series checkbox layout (should be the last layout)
        # The layout order is: control_layout, toolbar, canvas, series_layout
        # We want to keep control_layout, toolbar, and canvas, and only remove/rebuild series_layout
        last_item = None
        last_item_index = -1
        
        for i in range(layout.count()):
            item = layout.itemAt(i)
            # Look for a layout (not a widget) that's not the first one (control_layout)
            if item and item.layout() and not item.widget() and i > 0:
                last_item = item
                last_item_index = i
        
        # Remove the series layout if found
        if last_item and last_item_index >= 0:
            item = layout.takeAt(last_item_index)
            if item.layout():
                # Clear all widgets from the layout
                self._clear_layout(item.layout())
                # Delete the layout itself
                item.layout().deleteLater()
        
        # Rebuild checkboxes with new unit order
        self.checkboxes = []
        all_cols = list(self.df_data.columns)
        
        # Build checkboxes grouped by unit in framed boxes
        from PyQt6.QtWidgets import QGridLayout, QFrame
        from calculate_button_text_metrics import calculate_optimal_rows
        import math
        
        # Create horizontal layout for unit sections
        series_layout = QHBoxLayout()

        # Define colors for different units (cycle through these)
        unit_colors = [
            ('#e8f4f8', '#0066cc', '#003366'),  # Blue
            ('#fff5e6', '#cc6600', '#663300'),  # Orange
            ('#e8f8e8', '#00cc66', '#003300'),  # Green
            ('#f8e8f8', '#cc00cc', '#660066'),  # Purple
            ('#f8f8e8', '#cccc00', '#666600'),  # Yellow
        ]
        
        # Create a frame for each unit group
        for unit_idx, unit in enumerate(self.unit_list):
            unit_cols = self.axis_groups[unit]
            if len(unit_cols) == 0:
                continue
                
            # Calculate optimal number of rows for this unit using pixel width
            num_rows = self._calculate_rows_by_pixel_width(unit_cols, available_width_per_column=400)
            num_cols = math.ceil(len(unit_cols) / num_rows)
            
            # Get color scheme for this unit (cycle through colors)
            bg_color, border_color, text_color = unit_colors[unit_idx % len(unit_colors)]
            
            # Create frame for this unit
            unit_frame = QFrame()
            unit_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 2px solid {border_color};
                    border-radius: 5px;
                    padding: 5px;
                }}
            """)
            # Add context menu to unit frame for reordering
            unit_frame.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            unit_frame.customContextMenuRequested.connect(lambda pos, u=unit: self.show_unit_context_menu(pos, u, unit_frame))
            
            unit_layout = QGridLayout(unit_frame)
            unit_layout.setSpacing(2)
            unit_layout.setContentsMargins(5, 5, 5, 5)
            
            # Add checkboxes for this unit's series
            for i, col in enumerate(unit_cols):
                # Find the index of this column in all_cols
                series_idx = all_cols.index(col)
                
                row = i % num_rows
                col_pos = i // num_rows
                checkbox = QCheckBox(f"{col}")
                
                # Get series color and convert to hex
                series_color_hex = self._rgba_to_hex(self.series_colors[series_idx])
                
                checkbox.setStyleSheet(f"""
                    QCheckBox {{ 
                        background-color: transparent; 
                        color: {text_color};
                        spacing: 5px;
                    }}
                    QCheckBox::indicator {{
                        width: 13px;
                        height: 13px;
                        border: 2px solid {series_color_hex};
                        border-radius: 3px;
                        background-color: white;
                    }}
                    QCheckBox::indicator:checked {{
                        background-color: {series_color_hex};
                        border: 2px solid {series_color_hex};
                    }}
                """)
                
                # Tooltip with basic info and stats
                try:
                    s = self.df_data[col]
                    tip_lines = [f"{col}", f"Unit: {unit}"]
                    if pd.api.types.is_numeric_dtype(s):
                        nn = int(s.count())
                        s_valid = s.dropna()
                        if not s_valid.empty:
                            s_min = s_valid.min()
                            s_max = s_valid.max()
                            tip_lines += [
                                f"Non-null: {nn:,}",
                                f"Min: {s_min:.6g}",
                                f"Max: {s_max:.6g}"
                            ]
                        else:
                            tip_lines += [f"Non-null: {nn:,}"]
                    else:
                        tip_lines += [f"Type: {str(s.dtype)}", f"Non-null: {int(s.count()):,}"]
                    checkbox.setToolTip("\n".join(tip_lines))
                except Exception:
                    checkbox.setToolTip(f"{col} ({unit})")
                
                checkbox.blockSignals(True)
                checkbox.setChecked(bool(self.series_visible[series_idx]))
                checkbox.blockSignals(False)
                checkbox.stateChanged.connect(self.create_toggle_function(series_idx))
                checkbox.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                checkbox.customContextMenuRequested.connect(self.create_format_menu(series_idx, col))
                unit_layout.addWidget(checkbox, row, col_pos)
                self.checkboxes.append(checkbox)
            
            # Set size policy
            unit_frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
            series_layout.addWidget(unit_frame, stretch=num_cols)

        # Add the checkbox layout back to the main layout
        layout.addLayout(series_layout)
        
        # Replot with new axis order
        self.plot()
        
        # Update checkbox colors to match new plot colors
        self._update_checkbox_colors()
        
        self.save_current_settings()
    
    def _clear_layout(self, layout):
        """Recursively clear all widgets and sub-layouts from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
                item.layout().deleteLater()

    def toggle_auto_update(self, state):
        """Toggle auto-update mode for series visibility changes."""
        self.auto_update = bool(state)
        self.manual_update_btn.setEnabled(not self.auto_update)
        self.save_current_settings()  # Save the state immediately
        
    def manual_update_chart(self):
        """Manually trigger chart update when auto-update is disabled."""
        self.plot()
        self.save_current_settings()

    def toggle_all_series(self):
        """Toggle all series on/off."""
        # Determine the new state based on current toggle state
        new_state = self.toggle_all_state
        
        # Apply to all series
        for i in range(len(self.series_visible)):
            self.series_visible[i] = new_state
            if i < len(self.checkboxes):
                self.checkboxes[i].blockSignals(True)
                self.checkboxes[i].setChecked(new_state)
                self.checkboxes[i].blockSignals(False)
        
        # Flip the state for next time
        self.toggle_all_state = not self.toggle_all_state
        
        if self.auto_update:
            self.plot()
            self.save_current_settings()

    def toggle_crosshair(self):
        """Toggle crosshair on/off."""
        self.crosshair_enabled = self.crosshair_btn.isChecked()
        
        # If disabling, clear any existing crosshair
        if not self.crosshair_enabled:
            self.clear_crosshair()
    
    def clear_crosshair(self):
        """Remove crosshair lines from the plot."""
        if self.crosshair_vline is not None:
            try:
                self.crosshair_vline.remove()
            except ValueError:
                pass
            self.crosshair_vline = None
        if self.crosshair_hline is not None:
            try:
                self.crosshair_hline.remove()
            except ValueError:
                pass
            self.crosshair_hline = None
        if self.crosshair_hline_right is not None:
            try:
                self.crosshair_hline_right.remove()
            except ValueError:
                pass
            self.crosshair_hline_right = None
        self.canvas.draw_idle()

    def toggle_dark_mode(self):
        """Toggle between light and dark mode for the chart."""
        self.dark_mode = self.dark_mode_btn.isChecked()
        
    def _custom_format_coord(self, x, y):
        """Custom coordinate formatter that shows date and y-values for all visible axes"""
        
        # Format X coordinate as YYYY-MM-DD HH:MM
        xstr = ""
        try:
            dt = mdates.num2date(x)
            # Remove timezone information if present
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            xstr = dt.strftime('%Y-%m-%d %H:%M')
        except Exception as e:
            # Fallback: try manual conversion
            try:
                from datetime import datetime, timedelta
                # Matplotlib date is days since 0001-01-01 UTC
                dt = datetime.fromordinal(int(x)) + timedelta(days=x%1) - timedelta(days=366)
                xstr = dt.strftime('%Y-%m-%d %H:%M')
            except Exception as e2:
                xstr = f"{x:.2f}"
        
        # Get Y coordinates for all axes with visible series
        y_parts = []
        if hasattr(self, 'axes') and hasattr(self, 'unit_list') and hasattr(self, 'axis_groups'):
            # Find the calling axis by checking which axis this format_coord belongs to
            calling_axis = None
            for unit, axis in self.axes.items():
                if axis.format_coord == self._custom_format_coord:
                    # Check if we're being called from this specific axis instance
                    # The 'y' parameter is already in this axis's coordinate system
                    # We need to find which axis it is
                    calling_axis = axis
                    calling_unit = unit
                    break
            
            # For twinned axes, we need to convert between coordinate systems
            # Get mouse event position if available
            try:
                # Get the last mouse event from the canvas
                if hasattr(self.canvas, 'get_tk_widget'):
                    # Try to get display coordinates
                    pass
            except:
                pass
            
            # For each unit with visible series, calculate its Y coordinate
            for unit in self.unit_list:
                # Skip units that don't have an axis (all series hidden)
                if unit not in self.axes:
                    continue
                    
                axis = self.axes[unit]
                
                # Check if this unit has any visible series
                unit_has_visible = False
                if hasattr(self, 'series_visible'):
                    unit_cols = self.axis_groups[unit]
                    all_cols = list(self.df_data.columns)
                    for col in unit_cols:
                        series_idx = all_cols.index(col)
                        if series_idx < len(self.series_visible) and self.series_visible[series_idx]:
                            unit_has_visible = True
                            break
                
                if unit_has_visible:
                    try:
                        # If this is the calling axis, use y directly
                        if axis == calling_axis:
                            y_val = y
                        else:
                            # Transform: data coords from calling_axis -> display -> data coords in this axis
                            # Get display coordinates from calling axis
                            display_point = calling_axis.transData.transform((x, y))
                            # Transform back to this axis's data coordinates
                            data_point = axis.transData.inverted().transform(display_point)
                            y_val = data_point[1]
                        
                        y_parts.append(f"{unit}={y_val:.2f}")
                    except Exception as e:
                        # If transformation fails, skip this axis
                        pass
        
        if y_parts:
            return f"x={xstr}  {' | '.join(y_parts)}"
        else:
            return f"x={xstr}  y={y:.2f}"

    def make_format_coord(self, calling_axis, calling_unit):
        def _format_coord(x, y):
            import matplotlib.dates as mdates
            # Format X coordinate as YYYY-MM-DD HH:MM
            try:
                dt = mdates.num2date(x)
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                xstr = dt.strftime('%Y-%m-%d %H:%M')
            except Exception:
                xstr = f"{x:.2f}"

            y_parts = []
            for unit, axis in self.axes.items():
                # Only show units with visible series
                unit_has_visible = False
                unit_cols = self.axis_groups[unit]
                all_cols = list(self.df_data.columns)
                for col in unit_cols:
                    series_idx = all_cols.index(col)
                    if series_idx < len(self.series_visible) and self.series_visible[series_idx]:
                        unit_has_visible = True
                        break
                if not unit_has_visible:
                    continue

                try:
                    if axis == calling_axis:
                        y_val = y
                    else:
                        # Transform: data coords from calling_axis -> display -> data coords in this axis
                        display_point = calling_axis.transData.transform((x, y))
                        data_point = axis.transData.inverted().transform(display_point)
                        y_val = data_point[1]
                    y_parts.append(f"{unit}={y_val:.2f}")
                except Exception:
                    pass

            if y_parts:
                return f"x={xstr}  {' | '.join(y_parts)}"
            else:
                return f"x={xstr}  y={y:.2f}"
        return _format_coord

    def on_mouse_press(self, event):
        """Handle mouse button press - start drawing crosshair or set measurement point."""
        if event.inaxes not in list(self.axes.values()) or event.xdata is None or event.ydata is None:
            return
        
        # Handle measurement mode
        if self.measure_enabled:
            if self.measure_start_point is None:
                # Start a new measurement: clear any previous graphics
                self.clear_measurement()                
                # First click - set start point
                self.measure_start_point = (event.xdata, event.ydata, event.inaxes)
                self.draw_measure_marker(event.xdata, event.ydata, event.inaxes, is_start=True)
            else:
                # Second click - set end point and show measurement
                self.measure_end_point = (event.xdata, event.ydata, event.inaxes)
                self.draw_measure_line()
            return
        
        # Handle crosshair mode
        if self.crosshair_enabled:
            self.mouse_pressed = True
            self.update_crosshair(event)

    def on_mouse_release(self, event):
        """Handle mouse button release - stop updating crosshair but keep it visible."""
        self.mouse_pressed = False

    def on_mouse_move(self, event):
        """Update crosshair position when mouse moves while button is pressed, or show preview line for measurement."""
        # Check if event is in any of our axes
        in_any_axis = event.inaxes in self.axes.values() if self.axes else False
        
        # Show crosshair in regular crosshair mode (when mouse button is pressed)
        if self.crosshair_enabled and self.mouse_pressed and in_any_axis:
            self.update_crosshair(event)
        
        # Show crosshair and preview line during measurement mode
        if self.measure_enabled and in_any_axis and event.xdata is not None and event.ydata is not None:
            # Show crosshair in measurement mode only if crosshair is also enabled
            if self.crosshair_enabled:
                self.update_crosshair(event)
            
            # Show preview line after first click
            if self.measure_start_point is not None and self.measure_end_point is None:
                self.draw_measure_preview(event)

    def update_crosshair(self, event):
        """Draw or update crosshair at the current mouse position."""
        if event.xdata is None or event.ydata is None:
            return
        
        # Remove old crosshair lines if they exist
        if self.crosshair_vline is not None:
            try:
                self.crosshair_vline.remove()
            except ValueError:
                pass
            self.crosshair_vline = None
        if self.crosshair_hline is not None:
            try:
                self.crosshair_hline.remove()
            except ValueError:
                pass
            self.crosshair_hline = None
        if self.crosshair_hline_right is not None:
            try:
                self.crosshair_hline_right.remove()
            except ValueError:
                pass
            self.crosshair_hline_right = None
        
        # Create new crosshair lines at current position
        # Vertical line on primary axis (shared X-axis)
        primary_axis = list(self.axes.values())[0]
        self.crosshair_vline = primary_axis.axvline(event.xdata, color='red', linestyle='--', linewidth=0.8, alpha=0.8, zorder=100)
        
        # Horizontal line on the axis where the mouse is
        self.crosshair_hline = event.inaxes.axhline(event.ydata, color='red', linestyle='--', linewidth=0.8, alpha=0.8, zorder=100)
        self.crosshair_hline_right = None
        
        self.canvas.draw_idle()

    def toggle_dark_mode(self):
        if self.dark_mode:
            plt.style.use('dark_background')
            self.dark_mode_btn.setText("Light Mode")
            
            # Set Windows 11 dark mode title bar
            try:
                import ctypes
                HWND = self.winId().__int__()
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                value = ctypes.c_int(1)  # 1 for dark mode, 0 for light
                ctypes.windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
            except Exception as e:
                print(f"Could not set Windows dark mode title bar: {e}")
            
            # Set figure and canvas background to dark
            self.fig.patch.set_facecolor('#202020')
            self.canvas.setStyleSheet("background-color: #202020;")
            
            # Create dark palette
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.ColorRole.Window, QColor(43, 43, 43))
            dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.ColorRole.Base, QColor(60, 60, 60))
            dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(43, 43, 43))
            dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 60))
            dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
            dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
            self.setPalette(dark_palette)
            
            # Set dark theme stylesheet for the entire window including toolbar
            dark_stylesheet = """
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QToolBar {
                    background-color: #2b2b2b;
                    border: none;
                    spacing: 3px;
                }
                QPushButton {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #4c4c4c;
                }
                QPushButton:pressed {
                    background-color: #2c2c2c;
                }
                QPushButton:checked {
                    background-color: #0d5a8f;
                }
                QCheckBox {
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QToolButton {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 3px;
                    border-radius: 2px;
                }
                QToolButton:hover {
                    background-color: #4c4c4c;
                }
                QToolButton:pressed {
                    background-color: #2c2c2c;
                }
                QLineEdit {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 2px;
                }
                QComboBox {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 2px;
                }
                QComboBox:hover {
                    background-color: #4c4c4c;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QSpinBox {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
            """
            self.setStyleSheet(dark_stylesheet)
            # Force update all widgets in the toolbar
            if hasattr(self, 'toolbar'):
                # Apply styling to toolbar and all its child widgets
                toolbar_stylesheet = """
                    QToolBar {
                        background-color: #2b2b2b;
                        border: none;
                        spacing: 3px;
                    }
                    QToolBar QToolButton {
                        background-color: #3c3c3c;
                        color: #ffffff;
                        border: 1px solid #555555;
                        padding: 3px;
                    }
                    QToolBar QToolButton:hover {
                        background-color: #4c4c4c;
                    }
                    QToolBar QLabel {
                        color: #ffffff;
                        background-color: #2b2b2b;
                    }
                    QToolBar QPushButton {
                        background-color: #3c3c3c;
                        color: #ffffff;
                        border: 1px solid #555555;
                        padding: 3px;
                    }
                    QToolBar QPushButton:hover {
                        background-color: #4c4c4c;
                    }
                """
                self.toolbar.setStyleSheet(toolbar_stylesheet)
        else:
            plt.style.use('default')
            self.dark_mode_btn.setText("Dark Mode")
            
            # Set Windows 11 light mode title bar
            try:
                import ctypes
                HWND = self.winId().__int__()
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                value = ctypes.c_int(0)  # 0 for light mode
                ctypes.windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
            except Exception as e:
                print(f"Could not set Windows light mode title bar: {e}")
            
            # Reset figure and canvas background to light
            self.fig.patch.set_facecolor('white')
            self.canvas.setStyleSheet("background-color: white;")
            
            # Reset to default light theme and palette
            self.setPalette(QApplication.style().standardPalette())
            self.setStyleSheet("")
            
            # Reset toolbar style
            if hasattr(self, 'toolbar'):
                self.toolbar.setStyleSheet("")
                self.toolbar.setPalette(QApplication.style().standardPalette())
        
        self.plot()
        self.save_current_settings()
    
    def plot(self):
        # Save the axis title and labels (from primary axis if exists)
        title = ''
        xlabel = ''
        if hasattr(self, 'axes') and len(self.axes) > 0:
            primary_axis = list(self.axes.values())[0]
            title = primary_axis.get_title()
            xlabel = primary_axis.get_xlabel()

        # Save axis limits before clearing
        if not self.initial_plot and hasattr(self, 'axes'):
            # Save current axis limits to persistent dictionaries
            for unit, axis in self.axes.items():
                self.unit_xlims[unit] = axis.get_xlim()
                self.unit_ylims[unit] = axis.get_ylim()

        # Clear the figure
        self.fig.clear()
        
        # Create axes for each unit
        self.axes = {}
        
        # Use stored series colors (already loaded from settings or defaults)
        # No need to regenerate colors here
        
        # Pre-determine which units have visible series
        all_cols = list(self.df_data.columns)
        units_with_visible_series = set()
        for unit in self.unit_list:
            unit_cols = self.axis_groups[unit]
            for col in unit_cols:
                series_idx = all_cols.index(col)
                if self.series_visible[series_idx]:
                    units_with_visible_series.add(unit)
                    break  # Found at least one visible series in this unit
        
        # Create axes only for units with visible series
        if len(self.unit_list) > 0:
            # Get list of units that actually need axes
            visible_units = [unit for unit in self.unit_list if unit in units_with_visible_series]
            
            if len(visible_units) > 0:
                # Create primary axis for first visible unit
                first_unit = visible_units[0]
                self.axes[first_unit] = self.fig.add_subplot(111)
                # self.axes[first_unit].format_coord = self._custom_format_coord
                self.axes[first_unit].format_coord = self.make_format_coord(self.axes[first_unit], first_unit)
                self.axes[first_unit].set_title(title)
                self.axes[first_unit].set_xlabel(xlabel)
                self.axes[first_unit].set_ylabel(first_unit)
                self.axes[first_unit].grid(visible=True, which='major', axis='both', color='grey')
                self.axes[first_unit].grid(visible=True, which='minor', axis='both', color='lightgrey')
                self.axes[first_unit].tick_params(which='minor', labelcolor='lightgrey')
                self.axes[first_unit].tick_params(axis='x', rotation=90, which='both')
                
                # Create twin axes only for additional visible units
                for i, unit in enumerate(visible_units[1:], 1):
                    self.axes[unit] = self.axes[first_unit].twinx()
                    # self.axes[unit].format_coord = self._custom_format_coord
                    self.axes[unit].format_coord = self.make_format_coord(self.axes[unit], unit)
                    self.axes[unit].set_ylabel(unit)
                    
                    # Position spine for 2nd+ visible axes (offset from right edge)
                    if i > 1:
                        self.axes[unit].spines['right'].set_position(('outward', 60 * (i - 1)))
        
        # Plot all series on their respective axes
        handles_list = []
        labels_list = []
        
        # Track if we've added the separator after the first unit
        separator_added = False
        
        for unit_idx, unit in enumerate(self.unit_list):
            # Skip units that don't have an axis (no visible series)
            if unit not in self.axes:
                continue
                
            unit_cols = self.axis_groups[unit]
            axis = self.axes[unit]
            
            for col in unit_cols:
                series_idx = all_cols.index(col)
                fmt = self.series_formats[series_idx]
                
                # Use stored color from self.series_colors
                # This ensures consistent colors that persist across reorderings and restarts
                series_color = self.series_colors[series_idx] if series_idx < len(self.series_colors) else (0, 0, 0, 1)
                
                if self.series_visible[series_idx]:
                    line = axis.plot(self.df_data.index, self.df_data[col], label=col, alpha=0.5, 
                                   color=series_color,
                                   linestyle=fmt['linestyle'], marker=fmt['marker'], 
                                   markersize=fmt['markersize'])[0]
                    handles_list.append(line)
                    labels_list.append(col)
            
            # Add separator only after the first unit (between left and right axes)
            if unit_idx == 0 and len(self.unit_list) > 1 and not separator_added:
                if len([h for h in handles_list if h.get_label() != '─────────────']) > 0:
                    from matplotlib.lines import Line2D
                    separator = Line2D([0], [0], color='none', label='─────────────')
                    handles_list.append(separator)
                    labels_list.append('─────────────')
                    separator_added = True

        # Add legend with all handles to primary axis
        # This ensures series from all axes (including twin axes) appear in the legend
        if len(self.axes) > 0 and handles_list:
            primary_axis = list(self.axes.values())[0]
            primary_axis.legend(handles=handles_list, labels=labels_list)

        # Restore or set axis limits
        if self.initial_plot:
            self.initial_plot = False
            # Use saved limits from settings or autoscale
            for unit, axis in self.axes.items():
                if unit in self.unit_xlims and unit in self.unit_ylims:
                    try:
                        axis.set_xlim(self.unit_xlims[unit])
                        axis.set_ylim(self.unit_ylims[unit])
                    except Exception as e:
                        print(f"Warning: Could not restore limits for {unit}: {e}")
                        axis.autoscale(axis='both')
                else:
                    axis.autoscale(axis='both')
        else:
            # Restore from persistent dictionaries (handles hidden axes correctly)
            # Get x-limits from first available unit with saved limits
            shared_xlim = None
            for unit in self.unit_list:
                if unit in self.unit_xlims:
                    shared_xlim = self.unit_xlims[unit]
                    break
            
            for unit, axis in self.axes.items():
                # X-axis is shared, so use the same x-limits for all axes
                if shared_xlim is not None:
                    try:
                        axis.set_xlim(shared_xlim)
                    except Exception:
                        pass
                elif unit in self.unit_xlims:
                    try:
                        axis.set_xlim(self.unit_xlims[unit])
                    except Exception:
                        pass
                
                # Y-axis limits are per-unit
                if unit in self.unit_ylims:
                    try:
                        axis.set_ylim(self.unit_ylims[unit])
                    except Exception:
                        pass
                else:
                    # Only autoscale Y-axis for new units without saved limits
                    axis.autoscale(axis='y', enable=True)

        # Apply x-axis formatting to all axes
        self.reformatXAxis()
        
        # CRITICAL: Re-apply the custom coordinate formatter after formatting
        # for axis in self.axes.values(): # Not used since switching from self.axes[unit].format_coord = self._custom_format_coord to self.axes[unit].format_coord = self.make_format_coord(self.axes[unit], unit)
        #     axis.format_coord = self._custom_format_coord
        
        # Update toolbar labels
        if hasattr(self, 'toolbar'):
            self.toolbar.update_xAxisLen()
            self.toolbar.update_locator_info()

        self.canvas.draw()

    def apply_xaxis_formatting(self, ax):
        # Determine the mode: either manual or automatic based on xAxisLen
        if getattr(self, 'manual_xaxis', False) and getattr(self, 'manual_xaxis_mode', None):
            mode = self.manual_xaxis_mode
            is_manual = True
        else:
            # Automatic mode: determine mode from axis length
            xlim = ax.get_xlim()
            xAxisLen = xlim[1] - xlim[0]
            is_manual = False
            
            if xAxisLen < 3 / 24:
                mode = "Minute"
            elif xAxisLen < 6 / 24:
                mode = "Hour"
            elif xAxisLen < 2:
                mode = "Day"
            elif xAxisLen < 14:
                mode = "Week"
            elif xAxisLen < 60:
                mode = "Month"
            elif xAxisLen < 367*1.5:
                mode = "Year"
            else:
                mode = "Decade"
        
        # Apply locators and formatters based on mode
        if mode == "Minute":
            ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=range(60), interval=1))
            ax.xaxis.set_minor_locator(mdates.SecondLocator(bysecond=range(60), interval=10))
            ax.xaxis.set_major_formatter(mdates.DateFormatter(r'%Y-%m-%d %H:%M'))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(r'%M:%S'))
            self.current_locator_info = "Major: Minute/1, Minor: Second/10" + ("" if is_manual else " (Auto)")
            
        elif mode == "Hour":
            ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(24), interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter(r'%Y-%m-%d %H:%M'))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(r'%H:%M'))
            # Check if auto mode needs different intervals
            if not is_manual:
                xlim = ax.get_xlim()
                xAxisLen = xlim[1] - xlim[0]
                if xAxisLen < 6 / 24:
                    ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=range(60), interval=15))
                    self.current_locator_info = "Major: Hour/1, Minor: Minute/15 (Auto)"
                else:
                    ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=range(60), interval=1))
                    self.current_locator_info = "Major: Hour/1, Minor: Minute/1 (Auto)"
            else:
                ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=range(60), interval=1))
                self.current_locator_info = "Major: Hour/1, Minor: Minute/1"
            
        elif mode == "Day":
            ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=range(1, 32), interval=1))
            ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(24), interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter(r'%Y-%m-%d'))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(r'%H:%M'))
            
            # Add hourly grid lines
            ax.grid(True, which='major', axis='x', color='grey', linestyle='-', linewidth=1)
            ax.grid(True, which='minor', axis='x', color='lightgrey', linestyle='-', linewidth=0.5)
            
            self.current_locator_info = "Major: Day/1, Minor: Hour/1, Grid: Hours" + ("" if is_manual else " (Auto)")
            
        elif mode == "Week":
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=MO, interval=1))
            ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter(r'W%U-%m-%d'))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(r'%Y-%m-%d'))
            
            # Manually draw 3-hour grid lines first (lightest, independent of tick locators)
            from datetime import datetime, timedelta
            xlim = ax.get_xlim()
            
            # Convert xlim to datetime
            start_date = mdates.num2date(xlim[0]).replace(tzinfo=None)
            end_date = mdates.num2date(xlim[1]).replace(tzinfo=None)
            
            # Round start to nearest 3-hour mark
            start_hour = (start_date.hour // 3) * 3
            current = start_date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            
            # Draw vertical lines every 3 hours (very light)
            while current <= end_date:
                ax.axvline(x=mdates.date2num(current), color='#e8e8e8', linestyle='-', linewidth=0.3, alpha=0.7, zorder=1)
                current += timedelta(hours=3)
            
            # Add major (weekly) and minor (daily) grid lines on top
            ax.grid(True, which='major', axis='x', color='grey', linestyle='-', linewidth=1)
            ax.grid(True, which='minor', axis='x', color='#a0a0a0', linestyle='-', linewidth=0.6, alpha=0.8)
            
            self.current_locator_info = "Major: Week/1, Minor: Day/1, Grid: 3hrs+Days" + ("" if is_manual else " (Auto)")
            
        elif mode == "Month":
            ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1, interval=1))
            ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=MO, interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter(r'%Y-%m'))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(r'W%U-%m-%d'))
            
            # Enable enhanced grid for month mode (both manual and auto)
            ax.grid(True, which='major', axis='x', color='grey', linestyle='-', linewidth=1)
            ax.grid(True, which='minor', axis='x', color='lightgrey', linestyle='-', linewidth=0.5)
            
            # Add very light vertical grid lines for days
            day_locator = mdates.DayLocator(interval=1)
            ax.xaxis.set_minor_locator(day_locator)
            ax.grid(True, which='minor', axis='x', color='#e0e0e0', linestyle='-', linewidth=0.3, alpha=0.7)
            
            self.current_locator_info = "Major: Month/1, Minor: Day/1, Grid: Days" + ("" if is_manual else " (Auto)")
            
        elif mode == "Year":
            ax.xaxis.set_major_locator(mdates.YearLocator(base=1, month=1))
            ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=1, interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter(r'%Y'))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(r'%Y-%m'))
            self.current_locator_info = "Major: Year/1, Minor: Month/1" + ("" if is_manual else " (Auto)")
            
        elif mode == "Decade":
            ax.xaxis.set_major_locator(mdates.YearLocator(base=10, month=1))
            ax.xaxis.set_minor_locator(mdates.YearLocator(base=1, month=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter(r'%Y'))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter(r'%Y'))
            self.current_locator_info = "Major: Year/10, Minor: Year/1 (Auto)"
            
        return ax

    def reformatXAxis(self):
        for unit, axis in self.axes.items():
            self.apply_xaxis_formatting(axis)

    def resetXAxis(self):
        """Reset X-axis to show all data with tight bounds (no margins)."""
        # Get the actual data range from the dataframe
        if self.df_data is not None and not self.df_data.empty:
            x_min = mdates.date2num(self.df_data.index.min())
            x_max = mdates.date2num(self.df_data.index.max())
            
            # Set tight limits with no margin on all axes
            for axis in self.axes.values():
                axis.set_xlim(x_min, x_max)
        else:
            # Fallback to autoscale if no data
            for axis in self.axes.values():
                axis.autoscale(axis='x')
        
        self.reformatXAxis()
        self.canvas.draw()
        if hasattr(self, 'toolbar'):
            self.toolbar.update_xAxisLen()
            self.toolbar.update_locator_info()
        self.save_current_settings()
    
    def zoom_in_x(self):
        """Zoom in on X-axis by 50% (keep Y-axis unchanged)."""
        if not hasattr(self, 'axes') or len(self.axes) == 0:
            return
            
        primary_axis = list(self.axes.values())[0]
        x_min, x_max = primary_axis.get_xlim()
        x_center = (x_min + x_max) / 2
        x_range = x_max - x_min
        new_range = x_range * 0.5  # Zoom in by 50%
        
        for axis in self.axes.values():
            axis.set_xlim(x_center - new_range/2, x_center + new_range/2)
        
        self.reformatXAxis()
        self.canvas.draw()
        if hasattr(self, 'toolbar'):
            self.toolbar.update_xAxisLen()
            self.toolbar.update_locator_info()
    
    def zoom_out_x(self):
        """Zoom out on X-axis by 50% (keep Y-axis unchanged)."""
        if not hasattr(self, 'axes') or len(self.axes) == 0:
            return
            
        primary_axis = list(self.axes.values())[0]
        x_min, x_max = primary_axis.get_xlim()
        x_center = (x_min + x_max) / 2
        x_range = x_max - x_min
        new_range = x_range * 1.5  # Zoom out by 50%
        
        # Get data limits to prevent zooming out beyond data range
        if self.df_data is not None and not self.df_data.empty:
            data_min = mdates.date2num(self.df_data.index.min())
            data_max = mdates.date2num(self.df_data.index.max())
            
            new_x_min = max(data_min, x_center - new_range/2)
            new_x_max = min(data_max, x_center + new_range/2)
        else:
            new_x_min = x_center - new_range/2
            new_x_max = x_center + new_range/2
        
        for axis in self.axes.values():
            axis.set_xlim(new_x_min, new_x_max)
        
        self.reformatXAxis()
        self.canvas.draw()
        if hasattr(self, 'toolbar'):
            self.toolbar.update_xAxisLen()
            self.toolbar.update_locator_info()
    
    def toggle_measure_mode(self):
        """Toggle measurement mode on/off."""
        self.measure_enabled = not self.measure_enabled
        
        if self.measure_enabled:
            self.toolbar.measure_btn.setText("Measure (ON)")
            # Clear any existing measurement and reset state
            self.clear_measurement()
            # Hide regular crosshair when measurement mode is active
            if self.crosshair_vline is not None:
                self.crosshair_vline.remove()
                self.crosshair_vline = None
            if self.crosshair_hline is not None:
                self.crosshair_hline.remove()
                self.crosshair_hline = None
            self.canvas.draw_idle()
        else:
            self.toolbar.measure_btn.setText("Measure")
            # Clear measurement when disabled
            self.clear_measurement()
            # Also clear the regular crosshair
            if self.crosshair_vline is not None:
                self.crosshair_vline.remove()
                self.crosshair_vline = None
            if self.crosshair_hline is not None:
                self.crosshair_hline.remove()
                self.crosshair_hline = None
            self.canvas.draw_idle()
    
    def clear_measurement(self):
        """Clear all measurement graphics."""
        if hasattr(self, 'measure_line') and self.measure_line is not None:
            try:
                self.measure_line.remove()
            except ValueError:
                pass
            self.measure_line = None
        if hasattr(self, 'measure_annotation') and self.measure_annotation is not None:
            try:
                self.measure_annotation.remove()
            except ValueError:
                pass
            self.measure_annotation = None
        if hasattr(self, 'measure_start_marker') and self.measure_start_marker is not None:
            try:
                self.measure_start_marker.remove()
            except ValueError:
                pass
            self.measure_start_marker = None
        if hasattr(self, 'measure_end_marker') and self.measure_end_marker is not None:
            try:
                self.measure_end_marker.remove()
            except ValueError:
                pass
            self.measure_end_marker = None
        if hasattr(self, 'measure_start_crosshair_h') and self.measure_start_crosshair_h is not None:
            try:
                self.measure_start_crosshair_h.remove()
            except ValueError:
                pass
            self.measure_start_crosshair_h = None
        if hasattr(self, 'measure_start_crosshair_v') and self.measure_start_crosshair_v is not None:
            try:
                self.measure_start_crosshair_v.remove()
            except ValueError:
                pass
            self.measure_start_crosshair_v = None
        if hasattr(self, 'measure_end_crosshair_h') and self.measure_end_crosshair_h is not None:
            try:
                self.measure_end_crosshair_h.remove()
            except ValueError:
                pass
            self.measure_end_crosshair_h = None
        if hasattr(self, 'measure_end_crosshair_v') and self.measure_end_crosshair_v is not None:
            try:
                self.measure_end_crosshair_v.remove()
            except ValueError:
                pass
            self.measure_end_crosshair_v = None
        self.measure_start_point = None
        self.measure_end_point = None
        self.canvas.draw_idle()
    
    def draw_measure_marker(self, x, y, axis, is_start=True):
        """Draw a marker at the measurement point with crosshair lines."""
        color = 'green' if is_start else 'blue'
        marker_style = 'o' if is_start else 's'
        
        if is_start:
            if self.measure_start_marker is not None:
                self.measure_start_marker.remove()
            if self.measure_start_crosshair_h is not None:
                self.measure_start_crosshair_h.remove()
            if self.measure_start_crosshair_v is not None:
                self.measure_start_crosshair_v.remove()
            
            self.measure_start_marker = axis.plot(x, y, marker=marker_style, color=color, 
                                                   markersize=8, zorder=200)[0]
            # Draw crosshair lines
            self.measure_start_crosshair_h = axis.axhline(y, color=color, linestyle=':', 
                                                           linewidth=1, alpha=0.5, zorder=150)
            self.measure_start_crosshair_v = axis.axvline(x, color=color, linestyle=':', 
                                                           linewidth=1, alpha=0.5, zorder=150)
        else:
            if self.measure_end_marker is not None:
                self.measure_end_marker.remove()
            if self.measure_end_crosshair_h is not None:
                self.measure_end_crosshair_h.remove()
            if self.measure_end_crosshair_v is not None:
                self.measure_end_crosshair_v.remove()
            
            self.measure_end_marker = axis.plot(x, y, marker=marker_style, color=color, 
                                                 markersize=8, zorder=200)[0]
            # Draw crosshair lines
            self.measure_end_crosshair_h = axis.axhline(y, color=color, linestyle=':', 
                                                         linewidth=1, alpha=0.5, zorder=150)
            self.measure_end_crosshair_v = axis.axvline(x, color=color, linestyle=':', 
                                                         linewidth=1, alpha=0.5, zorder=150)
        
        self.canvas.draw_idle()
    
    def draw_measure_preview(self, event):
        """Draw a preview line while moving mouse before second click."""
        if self.measure_line is not None:
            try:
                self.measure_line.remove()
            except ValueError:
                pass
            self.measure_line = None
        if self.measure_annotation is not None:
            try:
                self.measure_annotation.remove()
            except ValueError:
                pass
            self.measure_annotation = None
        
        x_start, y_start, axis_start = self.measure_start_point
        x_end, y_end = event.xdata, event.ydata
        
        # Apply Shift key constraint
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QApplication
        modifiers = QApplication.keyboardModifiers()
        
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            # Lock to horizontal or vertical based on which distance is larger
            dx = abs(x_end - x_start)
            dy = abs(y_end - y_start)
            
            if dx > dy:
                # Lock to horizontal (same Y)
                y_end = y_start
            else:
                # Lock to vertical (same X)
                x_end = x_start
        
        # Draw preview line on the start axis
        self.measure_line = axis_start.plot([x_start, x_end], [y_start, y_end], 
                                          color='orange', linestyle='--', linewidth=1.5, 
                                          alpha=0.7, zorder=150)[0]
        
        self.canvas.draw_idle()
    
    def draw_measure_line(self):
        """Draw the final measurement line and display measurements."""
        x_start, y_start, axis_start = self.measure_start_point
        x_end, y_end, axis_end = self.measure_end_point
        
        # Clear any preview
        if self.measure_line is not None:
            self.measure_line.remove()
        if self.measure_annotation is not None:
            self.measure_annotation.remove()
        
        # Draw end marker
        self.draw_measure_marker(x_end, y_end, axis_end, is_start=False)
        
        # Determine which axis to draw the line on
        if axis_start == axis_end:
            draw_axis = axis_start
        else:
            # Mixed axes - use primary axis
            draw_axis = list(self.axes.values())[0] if len(self.axes) > 0 else axis_start
        
        # Draw measurement line on the appropriate axis
        self.measure_line = draw_axis.plot([x_start, x_end], [y_start, y_end], 
                                          color='blue', linestyle='-', linewidth=2, 
                                          alpha=0.8, zorder=150)[0]
        
        # Calculate measurements
        from datetime import timedelta
        
        # Time difference
        dt_start = mdates.num2date(x_start)
        dt_end = mdates.num2date(x_end)
        time_diff = dt_end - dt_start
        
        # Format time difference
        total_seconds = abs(time_diff.total_seconds())
        if total_seconds < 3600:
            time_str = f"{total_seconds/60:.1f} min"
        elif total_seconds < 86400:
            time_str = f"{total_seconds/3600:.2f} h"
        else:
            time_str = f"{total_seconds/86400:.2f} days"
        
        # Format datetime strings
        dt_start_str = dt_start.strftime('%Y-%m-%d %H:%M')
        dt_end_str = dt_end.strftime('%Y-%m-%d %H:%M')
        
        # Build measurement text starting with time
        measurement_lines = [f"ΔTime: {dt_end_str} - {dt_start_str} = {time_str}"]
        
        # Calculate Y differences for all axes
        # Get display coordinates for the measurement points
        y_start_display = axis_start.transData.transform((x_start, y_start))[1]
        y_end_display = axis_end.transData.transform((x_end, y_end))[1]
        
        # Calculate delta Y for each axis/unit
        for unit, axis in self.axes.items():
            # Convert display coordinates back to this axis's data coordinates
            y_start_data = axis.transData.inverted().transform((0, y_start_display))[1]
            y_end_data = axis.transData.inverted().transform((0, y_end_display))[1]
            dy = y_end_data - y_start_data
            
            # Add to measurement text with format: Δunit = y_end - y_start = delta
            measurement_lines.append(f"Δ{unit} = {y_end_data:.2f} - {y_start_data:.2f} = {dy:.2f}")
        
        measurement_text = "\n".join(measurement_lines)
        
        # Add annotation at midpoint on the same axis as the line
        x_mid = (x_start + x_end) / 2
        y_mid = (y_start + y_end) / 2
        
        self.measure_annotation = draw_axis.annotate(
            measurement_text,
            xy=(x_mid, y_mid),
            xytext=(10, 10),
            textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8),
            fontsize=9,
            zorder=200
        )
        
        self.canvas.draw_idle()
        
        # Reset for next measurement
        self.measure_start_point = None
        self.measure_end_point = None
        


if __name__ == "__main__":
    import pandas as pd
    from InteractivePlotWindowMultiAxis import InteractivePlotWindowMultiAxis
    level = np.random.randint(100, size=(100))
    volume = level.cumsum()
    # Create sample data
    df = pd.DataFrame({
        'Inflow [m3/h]': np.random.randn(100).cumsum(),
        'Inflow [m3]': np.random.randn(100).cumsum(),
        'Level [m]': level,
        'Volume [m*m2]': volume,        
        'Temperature [°C]': np.random.randn(100).cumsum() + 20,
        'Pressure [kPa]': np.random.randn(100).cumsum() + 100
        }, index=pd.date_range('2025-01-01', periods=100, freq='h'))
    app = QApplication(sys.argv)
    mainWin = QMainWindow()

    # Create window
    mainWin = InteractivePlotWindowMultiAxis(df, WindowTitle="Multi-Unit Monitoring")
    mainWin.show()
    sys.exit(app.exec())