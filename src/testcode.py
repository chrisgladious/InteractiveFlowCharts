import pandas as pd
import numpy as np

# Create a sample DataFrame
data = {
    'A': [1, 2, 3, 4],
    'B': [5, 6, 7, 8],
    'C': [9, 10, 11, 12],
    'D': [13, 14, 15, 16]
}
df = pd.DataFrame(data)

# Create a boolean array indicating which columns to select
series_visible = [True, False, True, False]

# Select columns based on the boolean array
selected_columns = df.loc[:, series_visible]

print(selected_columns.max())

quit()

# import tkinter
# print(tkinter.TkVersion)
# #print(tkinter.Tcl().eval('info patchlevel'))
# #pip install --upgrade --force-reinstall tk
# import os

# os.environ['TCL_LIBRARY'] = r'C:\Users\secn17444\pyver\Python313\tcl\tcl8.6'
# os.environ['TK_LIBRARY'] = r'C:\Users\secn17444\pyver\Python313\tcl\tk8.6'

# import tkinter
# tkinter.Tk().mainloop()  # Test if it works

import os

os.environ['TCL_LIBRARY'] = r'C:\Users\secn17444\pyver\Python313\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\secn17444\pyver\Python313\tcl\tk8.6'


import matplotlib.pyplot as plt

# Create a figure and axes
fig, ax = plt.subplots()
ax.plot([0, 1, 2, 3, 4], [10, 20, 25, 30, 40])  # Example data

# Enable built-in zoom, pan, and scroll
plt.show()

