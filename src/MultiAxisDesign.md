# Multi-Axis Plot Window Design

## Overview
Extension of InteractivePlotWindow to support multiple Y-axes based on units extracted from series names.

## Unit Detection
- Series names should end with `[unit]` e.g., `"Flow [m3/h]"`, `"Level [m]"`, `"Rate [l/h]"`
- Extract unit using regex: `\[([^\]]+)\]$`
- Group series by their unit
- Create one Y-axis per unique unit

## Architecture Changes

### 1. Data Structure
Instead of:
- `df_axL` (left axis DataFrame)
- `df_axR` (right axis DataFrame)

Use:
- `df_data` (single DataFrame with all series)
- `axis_groups` (dict mapping unit -> list of series names)
- `axes` (dict mapping unit -> matplotlib axis object)

### 2. Axis Creation
```python
# Detect units from column names
def extract_unit(column_name):
    match = re.search(r'\[([^\]]+)\]$', column_name)
    return match.group(1) if match else 'default'

# Group columns by unit
axis_groups = {}
for col in df.columns:
    unit = extract_unit(col)
    if unit not in axis_groups:
        axis_groups[unit] = []
    axis_groups[unit].append(col)

# Create axes (matplotlib supports twinx() chaining)
axes = {}
units = list(axis_groups.keys())
axes[units[0]] = fig.add_subplot(111)  # Primary axis

for i, unit in enumerate(units[1:], 1):
    axes[unit] = axes[units[0]].twinx()
    # Offset spine position for 3rd+ axes
    if i > 1:
        axes[unit].spines['right'].set_position(('outward', 60 * (i-1)))
```

### 3. Checkbox Layout
- Group checkboxes by unit
- Add unit label above each group
- Maintain left/right column layout (or adapt to multi-column)

### 4. Settings Management
- Save/load axis limits for each unit
- Save/load series visibility for all series
- Maintain backward compatibility with existing 2-axis format

## Implementation Plan

1. **Phase 1**: Parse units and create axis groups
2. **Phase 2**: Modify plot creation to handle multiple axes
3. **Phase 3**: Update checkbox layout with unit grouping
4. **Phase 4**: Adjust autoscale, zoom, measurement tools for multi-axis
5. **Phase 5**: Update settings save/load
6. **Phase 6**: Testing and refinement

## Example Usage
```python
import pandas as pd

df = pd.DataFrame({
    'Inflow [m3/h]': [...],
    'Outflow [m3/h]': [...],
    'Level [m]': [...],
    'Temperature [°C]': [...],
    'Pressure [kPa]': [...]
})

window = InteractivePlotWindowMultiAxis(df, WindowTitle="Multi-Unit Plot")
```

This would create 4 Y-axes:
- Left: m3/h
- Right 1: m
- Right 2: °C
- Right 3: kPa
