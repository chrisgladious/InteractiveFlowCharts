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

def save_plot_settings(settings, filename='InteractivePlotWindow.json'):
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
            with open(base_file, 'r') as f:
                existing = json.load(f)
        except Exception:
            existing = {}
    
    if key is None:
        # Keep legacy flat format
        data_to_write = cleaned_settings
    else:
        # Ensure mapping format { key: settings }
        if isinstance(existing, dict) and 'axLxlim' in existing and 'axLylim' in existing:
            # Convert legacy flat content into a mapping under a default key
            existing = {'default': existing}
        elif not isinstance(existing, dict):
            existing = {}
        existing[key] = cleaned_settings
        data_to_write = existing
    
    try:
        with open(base_file, 'w', newline='\r\n') as f:
            json.dump(data_to_write, f, indent=4, separators=(',', ': '))
        print(f"Saved plot settings to {base_file}{('::' + key) if key else ''}")
    except Exception as e:
        print(f"Warning: could not save plot settings to {base_file}: {e}")

def load_plot_settings(filename='InteractivePlotWindow.json'):
    """Load settings from JSON.
    If filename contains '::KEY', load that profile from the shared JSON file.
    Returns None if not found.
    """
    base_file, key = _split_settings_filename_key(filename)
    try:
        with open(base_file, 'r') as f:
            data = json.load(f)
        # If no key requested, accept flat or return as-is
        if key is None:
            # Normalize series_visible booleans for flat content
            if isinstance(data, dict) and 'series_visible' in data and not any(isinstance(x, bool) for x in data['series_visible']):
                data['series_visible'] = [bool(x) for x in data['series_visible']]
            return data
        # Key requested: ensure mapping
        if isinstance(data, dict) and 'axLxlim' in data and 'axLylim' in data:
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
            "Minute",
            "Hour",
            "Day",
            "Week",
            "Month",
            "Year"
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
        self.addAction('Reset X', self.plot_window.resetXAxis)
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
            self.plot_window.manual_xaxis = False
            self.plot_window.manual_xaxis_mode = None
            self.manual_xaxis_btn.setText("Manual X-Axis")
            self.modeLabel.setText("Mode: Auto")
        self.plot_window.reformatXAxis()
        self.plot_window.canvas.draw()
        self.update_locator_info()

    def autoscale(self):
        ax1 = self.plot_window.axL
        ax1.autoscale(axis='both')
        self.canvas.draw()
        self.update_xAxisLen()
        self.plot_window.save_current_settings()

    def autoscaleLeftY(self):
        df_axL = self.plot_window.df_axL
        series_visibleLeftY = self.plot_window.series_visible[:len(df_axL.columns)]
        if not any(series_visibleLeftY):
            return
        # Get current x-axis limits
        xlim = self.plot_window.axL.get_xlim()
        xlim = [mdates.num2date(x).replace(tzinfo=None) for x in xlim]
        selected_columns = df_axL[(df_axL.index >= xlim[0]) & (df_axL.index <= xlim[1])]
        selected_columns = selected_columns.loc[:, series_visibleLeftY]
        if selected_columns.empty:
            return
        ylim = (selected_columns.min().min(), selected_columns.max().max())
        self.plot_window.axL.set_ylim(ylim)
        self.canvas.draw()
        self.plot_window.save_current_settings()

    def autoscaleRightY(self):
        # Guard if there is no right-axis data
        df_axR = self.plot_window.df_axR
        if df_axR is None or df_axR.empty:
            return
        # compute visible columns for right axis
        df_axL = self.plot_window.df_axL
        total_left = len(df_axL.columns)
        series_visibleRightY = self.plot_window.series_visible[total_left: total_left + len(df_axR.columns)]
        if not any(series_visibleRightY):
            return
        # Get current x-axis limits
        xlim = self.plot_window.axR.get_xlim()
        xlim = [mdates.num2date(x).replace(tzinfo=None) for x in xlim]
        selected_columns = df_axR[(df_axR.index >= xlim[0]) & (df_axR.index <= xlim[1])]
        selected_columns = selected_columns.loc[:, series_visibleRightY]
        if selected_columns.empty:
            return
        ylim = (selected_columns.min().min(), selected_columns.max().max())
        self.plot_window.axR.set_ylim(ylim)
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
        xlim = self.plot_window.axL.get_xlim()
        step = (xlim[1] - xlim[0]) * 0.25  # Move 25% of the current x-axis range
        self.plot_window.axL.set_xlim(xlim[0] - step, xlim[1] - step)
        self.canvas.draw()
        self.update_xAxisLen()
        self.plot_window.save_current_settings()

    def moveRight(self):
        xlim = self.plot_window.axL.get_xlim()
        step = (xlim[1] - xlim[0]) * 0.25  # Move 25% of the current x-axis range
        self.plot_window.axL.set_xlim(xlim[0] + step, xlim[1] + step)
        self.canvas.draw()
        self.update_xAxisLen()
        self.plot_window.save_current_settings()

class InteractivePlotWindow(QMainWindow):
    def __init__(self, df_axL, df_axL_Title = None, df_axR=None, df_axR_Title = None, WindowTitle = None, initial_visible=None, settings_file=None):
        super().__init__()
        if WindowTitle is None:
            self.setWindowTitle("Interactive Plot")
        else:
            self.setWindowTitle(WindowTitle)

        # Store the DataFrames (ensure df_axR is a DataFrame if None)
        self.df_axL = df_axL
        self.df_axR = df_axR if df_axR is not None else pd.DataFrame()
        self.df_axL_Title = df_axL_Title
        self.df_axR_Title = df_axR_Title
        
        # Settings file path (default or custom)
        self.settings_file = settings_file if settings_file is not None else 'InteractivePlotWindow.json'
        
        # Flag to check if it's the initial plot
        self.initial_plot = True

        # Manual/auto x-axis state
        self.manual_xaxis = False
        self.manual_xaxis_mode = None

        # Auto-update state for series visibility
        self.auto_update = True

        # Dark mode state
        self.dark_mode = False

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
        left_cols = list(self.df_axL.columns)
        right_cols = list(self.df_axR.columns) if (self.df_axR is not None and not self.df_axR.empty) else []
        all_cols = left_cols + right_cols

        # Try to load saved settings before setting up visibility and checkboxes
        self.saved_settings = load_plot_settings(self.settings_file)
        
        # Set up initial visibility state
        if self.saved_settings and 'series_visible' in self.saved_settings and len(self.saved_settings['series_visible']) == len(all_cols):
            # Use saved visibility if available and matches column count
            self.series_visible = [bool(x) for x in self.saved_settings['series_visible']]
        else:
            # Fall back to initial_visible parameter
            if initial_visible is None:
                self.series_visible = [True] * len(all_cols)
            elif isinstance(initial_visible, (list, tuple)) and len(initial_visible) == len(all_cols):
                # Convert numeric 1/0 or booleans to booleans
                self.series_visible = [bool(x) for x in initial_visible]
            else:
                # Treat initial_visible as list of column names to show
                try:
                    visible_set = set(initial_visible)
                    self.series_visible = [ (col in visible_set) for col in all_cols ]
                except Exception:
                    # fallback to all True
                    self.series_visible = [True] * len(all_cols)

        # Initialize checkboxes list
        self.checkboxes = []
        
        # Add auto-update toggle and manual update button at the top
        control_layout = QHBoxLayout()
        self.auto_update_checkbox = QCheckBox("Auto-update chart")
        self.auto_update_checkbox.setChecked(True)
        self.auto_update_checkbox.stateChanged.connect(self.toggle_auto_update)
        control_layout.addWidget(self.auto_update_checkbox)
        
        self.manual_update_btn = QPushButton("Update Chart")
        self.manual_update_btn.clicked.connect(self.manual_update_chart)
        self.manual_update_btn.setEnabled(False)  # Initially disabled since auto-update is on
        control_layout.addWidget(self.manual_update_btn)
        
        self.dark_mode_btn = QPushButton("Dark Mode")
        self.dark_mode_btn.setCheckable(True)
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        control_layout.addWidget(self.dark_mode_btn)
        
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Build checkboxes below the chart with left and right sections in framed boxes
        from PyQt6.QtWidgets import QGridLayout, QFrame
        
        # Create horizontal layout for left and right framed sections
        series_layout = QHBoxLayout()
        
        # Number of columns per row in the grid
        num_cols_per_row = 8
        
        # LEFT AXIS SECTION (Blue frame)
        if len(left_cols) > 0:
            left_frame = QFrame()
            left_frame.setStyleSheet("""
                QFrame {
                    background-color: #e8f4f8;
                    border: 2px solid #0066cc;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
            left_layout = QGridLayout(left_frame)
            left_layout.setSpacing(2)
            left_layout.setContentsMargins(5, 5, 5, 5)
            
            for i, col in enumerate(left_cols):
                row = i // num_cols_per_row
                col_pos = i % num_cols_per_row
                checkbox = QCheckBox(f"{col}")
                checkbox.setStyleSheet("""
                    QCheckBox { 
                        background-color: transparent; 
                        color: #003366;
                        spacing: 5px;
                    }
                    QCheckBox::indicator {
                        width: 13px;
                        height: 13px;
                        border: 2px solid #003366;
                        border-radius: 3px;
                        background-color: white;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #0066cc;
                        border: 2px solid #003366;
                    }
                """)
                checkbox.blockSignals(True)
                checkbox.setChecked(bool(self.series_visible[i]))
                checkbox.blockSignals(False)
                checkbox.stateChanged.connect(self.create_toggle_function(i))
                left_layout.addWidget(checkbox, row, col_pos)
                self.checkboxes.append(checkbox)
            
            # Set size policy to minimize vertical expansion
            left_frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
            series_layout.addWidget(left_frame)
        
        # RIGHT AXIS SECTION (Orange frame)
        if len(right_cols) > 0:
            right_frame = QFrame()
            right_frame.setStyleSheet("""
                QFrame {
                    background-color: #fff5e6;
                    border: 2px solid #cc6600;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
            right_layout = QGridLayout(right_frame)
            right_layout.setSpacing(2)
            right_layout.setContentsMargins(5, 5, 5, 5)
            
            for i, col in enumerate(right_cols):
                row = i // num_cols_per_row
                col_pos = i % num_cols_per_row
                checkbox = QCheckBox(f"{col}")
                checkbox.setStyleSheet("""
                    QCheckBox { 
                        background-color: transparent; 
                        color: #663300;
                        spacing: 5px;
                    }
                    QCheckBox::indicator {
                        width: 13px;
                        height: 13px;
                        border: 2px solid #663300;
                        border-radius: 3px;
                        background-color: white;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #cc6600;
                        border: 2px solid #663300;
                    }
                """)
                checkbox.blockSignals(True)
                checkbox.setChecked(bool(self.series_visible[len(left_cols) + i]))
                checkbox.blockSignals(False)
                checkbox.stateChanged.connect(self.create_toggle_function(len(left_cols) + i))
                right_layout.addWidget(checkbox, row, col_pos)
                self.checkboxes.append(checkbox)
            
            # Set size policy to minimize vertical expansion
            right_frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
            series_layout.addWidget(right_frame)

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

    def closeEvent(self, event):
        """Save settings when window is closed"""
        self.save_current_settings()
        super().closeEvent(event)

    def save_current_settings(self):
        """Save current axis limits and other settings"""
        if not hasattr(self, 'axL'):
            return
            
        settings = {
            'axLxlim': list(self.axL.get_xlim()),
            'axLylim': list(self.axL.get_ylim()),
            'series_visible': self.series_visible
        }
        
        if self.df_axR is not None and not self.df_axR.empty and self.axR is not None:
            settings.update({
                'axRxlim': list(self.axR.get_xlim()),
                'axRylim': list(self.axR.get_ylim())
            })
            
        save_plot_settings(settings, self.settings_file)

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

    def toggle_auto_update(self, state):
        """Toggle auto-update mode for series visibility changes."""
        self.auto_update = bool(state)
        self.manual_update_btn.setEnabled(not self.auto_update)
        
    def manual_update_chart(self):
        """Manually trigger chart update when auto-update is disabled."""
        self.plot()
        self.save_current_settings()

    def toggle_dark_mode(self):
        """Toggle between light and dark mode for the chart."""
        self.dark_mode = self.dark_mode_btn.isChecked()
        
    def _custom_format_coord(self, x, y):
        """Custom coordinate formatter that always shows date as YYYY-MM-DD HH:MM"""
        # CRITICAL: Must be set on BOTH axL and axR (if present) since the top-most
        # axis (axR from twinx) handles mouse events and coordinate display
        
        # Always format as YYYY-MM-DD HH:MM regardless of x-axis mode
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
        
        # y parameter is the mouse y-coordinate in the axis that's handling the event
        # If axR exists, it's on top and handles events, so y is in right-axis scale
        # We need to transform it to left-axis scale for yL
        yL = y
        yR = None
        
        if self.df_axR is not None and not self.df_axR.empty and hasattr(self, 'axR') and self.axR is not None:
            # When right axis exists, y is in right-axis coordinates
            # Transform to left axis coordinates
            try:
                # Get the y-limits of both axes
                ylim_R = self.axR.get_ylim()
                ylim_L = self.axL.get_ylim()
                
                # Normalize y from right axis scale (0 to 1)
                y_norm = (y - ylim_R[0]) / (ylim_R[1] - ylim_R[0])
                
                # Transform to left axis scale
                yL = ylim_L[0] + y_norm * (ylim_L[1] - ylim_L[0])
                yR = y  # Original y is already in right-axis scale
            except Exception:
                yL = y
                yR = None
        
        # Return formatted string with explicit x= prefix to ensure it's clear
        if yR is not None:
            return f"x={xstr}  yL={yL:.2f}  yR={yR:.2f}"
        else:
            return f"x={xstr}  y={yL:.2f}"

    def on_mouse_press(self, event):
        """Handle mouse button press - start drawing crosshair."""
        if event.inaxes in [self.axL, self.axR] and event.xdata is not None and event.ydata is not None:
            self.mouse_pressed = True
            self.update_crosshair(event)

    def on_mouse_release(self, event):
        """Handle mouse button release - stop updating crosshair but keep it visible."""
        self.mouse_pressed = False

    def on_mouse_move(self, event):
        """Update crosshair position when mouse moves while button is pressed."""
        if self.mouse_pressed and event.inaxes in [self.axL, self.axR]:
            self.update_crosshair(event)

    def update_crosshair(self, event):
        """Draw or update crosshair at the current mouse position."""
        if event.xdata is None or event.ydata is None:
            return
        
        # Remove old crosshair lines if they exist
        if self.crosshair_vline is not None:
            self.crosshair_vline.remove()
        if self.crosshair_hline is not None:
            self.crosshair_hline.remove()
        if self.crosshair_hline_right is not None:
            self.crosshair_hline_right.remove()
        
        # Create new crosshair lines at current position
        self.crosshair_vline = self.axL.axvline(event.xdata, color='red', linestyle='--', linewidth=0.8, alpha=0.8, zorder=100)
        
        # Create horizontal line on the appropriate axis
        if event.inaxes == self.axR:
            self.crosshair_hline_right = self.axR.axhline(event.ydata, color='red', linestyle='--', linewidth=0.8, alpha=0.8, zorder=100)
            self.crosshair_hline = None
        else:
            self.crosshair_hline = self.axL.axhline(event.ydata, color='red', linestyle='--', linewidth=0.8, alpha=0.8, zorder=100)
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
        # Save the axis title and labels
        title = self.axL.get_title() if hasattr(self, 'axL') else ''
        xlabel = self.axL.get_xlabel() if hasattr(self, 'axL') else ''
        ylabel = self.axL.get_ylabel() if hasattr(self, 'axL') else ''

        if not self.initial_plot:
            try:
                self.axLxlim = self.axL.get_xlim()
                self.axLylim = self.axL.get_ylim()
                if self.df_axR is not None and not self.df_axR.empty and self.axR is not None:
                    self.axRxlim = self.axR.get_xlim()
                    self.axRylim = self.axR.get_ylim()
            except Exception:
                pass

        # Clear the axes
        self.fig.clear()
        self.axL = self.fig.add_subplot(111)

        # Set custom coordinate formatter on left axis
        # NOTE: This will be overridden if we create a right axis (twinx), 
        # so we must also set it on axR later
        self.axL.format_coord = self._custom_format_coord

        # Restore the axis title and labels
        self.axL.set_title(title)
        self.axL.set_xlabel(xlabel)
        self.axL.set_ylabel(ylabel)

        self.axL.grid(visible=True, which='major', axis='both', color='grey')
        self.axL.grid(visible=True, which='minor', axis='both', color='lightgrey')
        self.axL.tick_params(which='minor', labelcolor='lightgrey')
        self.axL.tick_params(axis='x', rotation=90, which='both')
        if self.df_axL_Title:
            self.axL.set_ylabel(self.df_axL_Title)

        # Generate a color cycle for all series (left + right)
        # Use darker colors for better visibility on white background
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors
        total_series = len(self.df_axL.columns) + (len(self.df_axR.columns) if self.df_axR is not None and not self.df_axR.empty else 0)
        
        # Create darker color palette by using Set1, Dark2, and tab10 which have more saturated colors
        if total_series <= 9:
            colors = [plt.cm.Set1(i) for i in range(total_series)]
        elif total_series <= 17:
            colors = [plt.cm.Set1(i % 9) for i in range(9)] + [plt.cm.Dark2(i % 8) for i in range(total_series - 9)]
        else:
            # For more series, combine Set1, Dark2, and tab10
            colors = ([plt.cm.Set1(i % 9) for i in range(9)] + 
                     [plt.cm.Dark2(i % 8) for i in range(8)] +
                     [plt.cm.tab10(i % 10) for i in range(max(0, total_series - 17))])
        color_index = 0

        # Plot left-axis columns
        for i, col in enumerate(self.df_axL.columns):
            if self.series_visible[i]:
                self.axL.plot(self.df_axL.index, self.df_axL[col], label=col, alpha=0.5, color=colors[color_index])
            color_index += 1

        handles, labels = self.axL.get_legend_handles_labels()

        # Reset right axis
        self.axR = None
        if self.df_axR is not None and not self.df_axR.empty:
            self.axR = self.axL.twinx()
            # CRITICAL: Set format_coord on axR too since it's on top and handles mouse events
            self.axR.format_coord = self._custom_format_coord
            
            # Add separator between left and right axis series in legend
            if handles:  # Only add separator if there are left axis items
                from matplotlib.lines import Line2D
                separator = Line2D([0], [0], color='none', label='─────────────')
                handles.append(separator)
                labels.append('─────────────')
            
            for i, col in enumerate(self.df_axR.columns, start=len(self.df_axL.columns)):
                if self.series_visible[i]:
                    # align on left x index (assumes same index or compatible)
                    self.axR.plot(self.df_axL.index, self.df_axR[col], label=col, alpha=0.5, color=colors[color_index])
                color_index += 1
            if self.df_axR_Title:
                self.axR.set_ylabel(self.df_axR_Title)

            handles2, labels2 = self.axR.get_legend_handles_labels()
            handles += handles2
            labels += labels2

        self.axL.legend(handles, labels)

        if self.initial_plot:
            self.initial_plot = False
            # If we have saved settings, use them
            if self.saved_settings:
                try:
                    # Restore axis limits
                    self.axL.set_xlim(self.saved_settings['axLxlim'])
                    self.axL.set_ylim(self.saved_settings['axLylim'])
                    if self.df_axR is not None and not self.df_axR.empty and self.axR is not None:
                        self.axR.set_xlim(self.saved_settings.get('axRxlim', self.saved_settings['axLxlim']))
                        self.axR.set_ylim(self.saved_settings['axRylim'])
                except Exception as e:
                    print(f"Warning: Could not restore all saved settings: {e}")
                    self.axL.autoscale(axis='both')
            else:
                self.axL.autoscale(axis='both')
            
            try:
                self.axLxlim = self.axL.get_xlim()
                self.axLylim = self.axL.get_ylim()
                if self.df_axR is not None and not self.df_axR.empty and self.axR is not None:
                    self.axRxlim = self.axR.get_xlim()
                    self.axRylim = self.axR.get_ylim()
            except Exception:
                pass
        else:
            try:
                self.axL.set_xlim(self.axLxlim)
                self.axL.set_ylim(self.axLylim)
                if self.df_axR is not None and not self.df_axR.empty and self.axR is not None:
                    self.axR.set_xlim(self.axRxlim)
                    self.axR.set_ylim(self.axRylim)
            except Exception:
                pass

        # Apply x-axis formatting to both axL and axR
        self.reformatXAxis()
        
        # CRITICAL: Re-apply the custom coordinate formatter after formatting
        # The reformatXAxis() may reset format_coord, so we MUST set it again
        # Set on BOTH axes since axR (if present) is on top and handles mouse events
        self.axL.format_coord = self._custom_format_coord
        if self.axR is not None:
            self.axR.format_coord = self._custom_format_coord
        
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
        self.axL = self.apply_xaxis_formatting(self.axL)
        if self.axR:
            self.axR = self.apply_xaxis_formatting(self.axR)

    def resetXAxis(self):
        """Reset X-axis to show all data."""
        self.axL.autoscale(axis='x')
        if self.axR:
            self.axR.autoscale(axis='x')
        self.reformatXAxis()
        self.canvas.draw()
        if hasattr(self, 'toolbar'):
            self.toolbar.update_xAxisLen()
            self.toolbar.update_locator_info()
        self.save_current_settings()


if __name__ == "__main__":
    # Load the DataFrame from the Excel file
    # excel_file_path = 'c:\\Users\\secn17444\\OneDrive - WSP O365\\Projekt\\Växjö\\5142-10347420\\PST\\Arbetsmaterial\\Flöden till Örsled PST och regn\\Örsled_2021-10-19_-_2021-10_23_version_2_CNI_bara rådata.xlsm'
    # df = pd.read_excel(excel_file_path, index_col='DateTime', parse_dates=True)

    # Path to your Excel file
    excel_file_path = r'c:\Users\chrini\Documents\Projekt\Örsled PST\Flöden till Örsled PST och regn\Örsled_2021-10-19_-_2021-10_23_version_2_CNI_bara rådata.xlsm'  #Tidigare: c:\Users\secn17444\OneDrive - WSP O365\Projekt\Växjö\5142-10347420\PST\Arbetsmaterial\Flöden till Örsled PST och regn\Örsled_2021-10-19_-_2021-10_23_version_2_CNI_bara rådata.xlsm'

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