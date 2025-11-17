# Multi-Axis Implementation Status

## Created Files
1. **InteractivePlotWindowMultiAxis.py** - Copy of original with initial modifications
2. **MultiAxisDesign.md** - Design document explaining the approach
3. **MultiAxisImplementationStatus.md** - This status document

## Completed Changes

### 1. Modified `__init__` signature (line ~401)
- **Old**: `__init__(self, df_axL, df_axL_Title=None, df_axR=None, df_axR_Title=None, ...)`
- **New**: `__init__(self, df_data, WindowTitle=None, initial_visible=None, settings_file=None)`
- Changed from 2 DataFrames (left/right) to single DataFrame with all series
- Added automatic unit detection and grouping

### 2. Added `_extract_units_and_group()` method (line ~786)
- Extracts units from column names using regex pattern `\[([^\]]+)\]$`
- Groups series by their unit
- Returns:
  - `axis_groups`: dict mapping unit -> list of series names
  - `series_units`: dict mapping series name -> unit
- Series without `[unit]` in name go to 'default' axis

### 3. Updated instance variables (line ~420-430)
- Added: `self.df_data` - single DataFrame
- Added: `self.axis_groups` - groups of series by unit
- Added: `self.series_units` - mapping of series to units
- Added: `self.unit_list` - list of all units
- Changed: `self.toggle_states` - dict per unit instead of left/right booleans
- Removed: `self.df_axL`, `self.df_axR`, `self.df_axL_Title`, `self.df_axR_Title`

## Still TODO (Major Work Required)

### Critical - Must Fix for Basic Functionality

1. **Update references to `self.df_axL` and `self.df_axR`** (lines ~470-570)
   - Currently still references old DataFrame structure
   - Need to change to use `self.df_data` and `self.axis_groups`
   - Affects: color palette generation, series setup, checkbox creation

2. **Rewrite `plot()` method** (line ~1200+)
   - Currently creates only axL and axR
   - Need to create multiple axes using `twinx()` chain
   - Position spines for 3rd+ axes using `set_position(('outward', 60 * (i-1)))`
   - Plot each series on its corresponding axis

3. **Update checkbox layout** (line ~600+)
   - Currently has left/right columns
   - Need to group by unit with labels
   - Consider multi-column layout or scrollable area for many units

4. **Fix toggle functions** (line ~841+)
   - Currently references left/right state
   - Need to update for unit-based grouping
   - Update toggle button creation

### Settings Management

5. **Update `save_current_settings()`** (line ~790)
   - Save axis limits for each unit
   - Save unit grouping information
   - Maintain backward compatibility option

6. **Update `load_plot_settings()`** function (line ~100)
   - Load axis limits for all units
   - Handle migration from 2-axis format

### UI and Interaction

7. **Update autoscale functions** (lines ~308-354)
   - `autoscale()` - scale all axes
   - Add `autoscaleByUnit(unit)` for individual axes
   - Update toolbar buttons

8. **Update crosshair** (line ~1030+)
   - Change checks from `[self.axL, self.axR]` to `list(self.axes.values())`
   - Update coordinate display for all axes

9. **Update measurement tool** (line ~1570+)
   - Handle measurements across different axes
   - Show Y-value for all units in annotation

10. **Update zoom functions** (line ~1530+)
    - `zoom_in_x()` and `zoom_out_x()` should work with all axes

### Custom Coordinate Display

11. **Update `_custom_format_coord()`** method
    - Display Y-values for all axes
    - Format: "X: value | Unit1: Y1 | Unit2: Y2 | ..."

## Testing Plan

### Phase 1: Basic Functionality
- [ ] Can create window with single-unit DataFrame
- [ ] Can create window with 2-unit DataFrame
- [ ] Can create window with 3+ unit DataFrame
- [ ] All series plot correctly on their axes
- [ ] Checkboxes show/hide series properly

### Phase 2: Interactions
- [ ] Zoom and pan work correctly
- [ ] X-axis controls work (zoom in/out, reset)
- [ ] Autoscale works for each axis
- [ ] Crosshair displays correct Y-values

### Phase 3: Advanced Features
- [ ] Measurement tool works across axes
- [ ] Settings save/load correctly
- [ ] Dark mode works
- [ ] Series formatting works
- [ ] Toggle unit groups works

### Phase 4: Edge Cases
- [ ] DataFrame with no units (all default)
- [ ] Mixed units and non-units
- [ ] Single series
- [ ] Many series (10+ units)

## Example Usage (Target)

```python
import pandas as pd
from InteractivePlotWindowMultiAxis import InteractivePlotWindow

# Create sample data
df = pd.DataFrame({
    'Inflow [m3/h]': np.random.randn(100).cumsum(),
    'Outflow [m3/h]': np.random.randn(100).cumsum(),
    'Level [m]': np.random.randn(100).cumsum() + 10,
    'Temperature [°C]': np.random.randn(100).cumsum() + 20,
    'Pressure [kPa]': np.random.randn(100).cumsum() + 100
}, index=pd.date_range('2025-01-01', periods=100, freq='H'))

# Create window
window = InteractivePlotWindow(df, WindowTitle="Multi-Unit Monitoring")
window.show()
```

## Estimated Work

- **Total methods to update**: ~30-40
- **New methods needed**: ~5-10
- **Testing iterations**: 5-10
- **Estimated time**: 4-8 hours of focused development

## Next Steps

1. Fix the immediate initialization issues (df_axL/df_axR references)
2. Implement multi-axis plotting in `plot()` method
3. Update checkbox layout
4. Test basic functionality
5. Iterate through remaining features

## Notes

- Keep original `InteractivePlotWindow.py` unchanged for comparison
- Consider adding backward compatibility mode to read old 2-axis format
- May want to add axis color coding to match checkboxes
- Consider max useful number of axes (probably 4-5 before it's too crowded)
