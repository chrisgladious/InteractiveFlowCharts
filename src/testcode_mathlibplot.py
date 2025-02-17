import os
os.environ['TCL_LIBRARY'] = r'C:\Users\secn17444\pyver\Python313\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\secn17444\pyver\Python313\tcl\tk8.6'
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
import numpy as np

# Create figure and axis
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)  # Leave space for controls

# Generate sample data
x = np.linspace(0, 10, 100)
y = np.sin(x)
ax.plot(x, y)

# Add built-in toolbar
toolbar = plt.get_current_fig_manager().toolbar

# Create text boxes for axis limits
axbox_xmin = plt.axes([0.1, 0.05, 0.1, 0.05])  # (left, bottom, width, height)
axbox_xmax = plt.axes([0.25, 0.05, 0.1, 0.05])
axbox_ymin = plt.axes([0.4, 0.05, 0.1, 0.05])
axbox_ymax = plt.axes([0.55, 0.05, 0.1, 0.05])

textbox_xmin = TextBox(axbox_xmin, "Xmin:")
textbox_xmax = TextBox(axbox_xmax, "Xmax:")
textbox_ymin = TextBox(axbox_ymin, "Ymin:")
textbox_ymax = TextBox(axbox_ymax, "Ymax:")

# Button to apply limits
ax_button = plt.axes([0.7, 0.05, 0.15, 0.05])
button = Button(ax_button, "Apply Limits")

# Function to update limits
def set_limits(event):
    try:
       # Get current axis limits
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        # Only update if the field is not empty
        new_xmin = float(textbox_xmin.text) if textbox_xmin.text.strip() else xmin
        new_xmax = float(textbox_xmax.text) if textbox_xmax.text.strip() else xmax
        new_ymin = float(textbox_ymin.text) if textbox_ymin.text.strip() else ymin
        new_ymax = float(textbox_ymax.text) if textbox_ymax.text.strip() else ymax

        ax.set_xlim(new_xmin, new_xmax)
        ax.set_ylim(new_ymin, new_ymax)
        plt.draw()
    except ValueError:
        print("Invalid input! Please enter numerical values.")

button.on_clicked(set_limits)

plt.show()
