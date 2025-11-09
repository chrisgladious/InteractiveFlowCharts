"""
Calculate button text metrics for InteractivePlotWindow checkbox layout.
This script analyzes the relationship between button text lengths and the 
number of rows used in the checkbox grid layout.
"""

import pandas as pd
import math

def calculate_optimal_rows(column_names, max_chars_per_row=180, min_rows=1, max_rows=4):
    """
    Calculate optimal number of rows based on button text lengths.
    
    Parameters:
    column_names: list of column names (button texts)
    max_chars_per_row: maximum characters that can comfortably fit in one row
    min_rows: minimum number of rows (default 1)
    max_rows: maximum number of rows (default 4)
    
    Returns:
    int: recommended number of rows
    """
    if not column_names:
        return min_rows
    
    total_chars = sum(len(col) for col in column_names)
    num_buttons = len(column_names)
    
    # Calculate ideal rows based on total character length
    ideal_rows_by_chars = math.ceil(total_chars / max_chars_per_row)
    
    # Also consider spreading buttons more evenly if we have many buttons
    # Aim for roughly 6-8 buttons per row as a reasonable density
    ideal_buttons_per_row = 7
    ideal_rows_by_count = math.ceil(num_buttons / ideal_buttons_per_row)
    
    # Use the larger of the two (more conservative)
    recommended_rows = max(ideal_rows_by_chars, ideal_rows_by_count)
    
    # Clamp to min/max bounds
    recommended_rows = max(min_rows, min(max_rows, recommended_rows))
    
    return recommended_rows

def analyze_button_layout(df_left, df_right=None):
    """
    Analyze button text lengths and layout metrics.
    
    Parameters:
    df_left: DataFrame for left axis
    df_right: DataFrame for right axis (optional)
    """
    # Get column names (button texts)
    left_cols = list(df_left.columns) if df_left is not None else []
    right_cols = list(df_right.columns) if df_right is not None and not df_right.empty else []
    
    # Calculate text lengths
    left_lengths = [len(col) for col in left_cols]
    right_lengths = [len(col) for col in right_cols]
    
    # Calculate optimal rows for each side
    # Use a minimum of 2 rows to match the visual design constraint in InteractivePlotWindow
    optimal_rows_left = calculate_optimal_rows(left_cols, min_rows=2, max_rows=4)
    optimal_rows_right = calculate_optimal_rows(right_cols, min_rows=2, max_rows=4)
    
    # Current layout parameters from InteractivePlotWindow.py
    num_rows = 2  # Fixed at 2 rows (will be replaced by optimal calculation)
    
    # Calculate derived layout metrics
    left_num_buttons = len(left_cols)
    right_num_buttons = len(right_cols)
    
    left_num_cols = math.ceil(left_num_buttons / num_rows) if left_num_buttons > 0 else 0
    right_num_cols = math.ceil(right_num_buttons / num_rows) if right_num_buttons > 0 else 0
    
    # Statistics
    print("=" * 80)
    print("BUTTON TEXT LENGTH ANALYSIS")
    print("=" * 80)
    print()
    
    # LEFT AXIS
    print("LEFT AXIS (Blue Frame)")
    print("-" * 80)
    print(f"Number of buttons: {left_num_buttons}")
    print(f"Number of rows (fixed): {num_rows}")
    print(f"Number of columns (calculated): {left_num_cols}")
    print()
    print("Button text lengths:")
    for i, (col, length) in enumerate(zip(left_cols, left_lengths)):
        row = i % num_rows
        col_pos = i // num_rows
        print(f"  [{i}] Row {row}, Col {col_pos}: '{col}' (length: {length})")
    
    if left_lengths:
        print()
        print(f"Total characters (left): {sum(left_lengths)}")
        print(f"Average length (left): {sum(left_lengths) / len(left_lengths):.1f}")
        print(f"Min length (left): {min(left_lengths)}")
        print(f"Max length (left): {max(left_lengths)}")
        print(f"Median length (left): {sorted(left_lengths)[len(left_lengths)//2]}")
    
    print()
    print()
    
    # RIGHT AXIS
    print("RIGHT AXIS (Orange Frame)")
    print("-" * 80)
    print(f"Number of buttons: {right_num_buttons}")
    print(f"Number of rows (fixed): {num_rows}")
    print(f"Number of columns (calculated): {right_num_cols}")
    print()
    print("Button text lengths:")
    for i, (col, length) in enumerate(zip(right_cols, right_lengths)):
        row = i % num_rows
        col_pos = i // num_rows
        print(f"  [{i}] Row {row}, Col {col_pos}: '{col}' (length: {length})")
    
    if right_lengths:
        print()
        print(f"Total characters (right): {sum(right_lengths)}")
        print(f"Average length (right): {sum(right_lengths) / len(right_lengths):.1f}")
        print(f"Min length (right): {min(right_lengths)}")
        print(f"Max length (right): {max(right_lengths)}")
        print(f"Median length (right): {sorted(right_lengths)[len(right_lengths)//2]}")
    
    print()
    print()
    
    # COMBINED ANALYSIS
    print("COMBINED ANALYSIS")
    print("-" * 80)
    all_lengths = left_lengths + right_lengths
    if all_lengths:
        print(f"Total buttons (both axes): {len(all_lengths)}")
        print(f"Total characters (all buttons): {sum(all_lengths)}")
        print(f"Average length (all buttons): {sum(all_lengths) / len(all_lengths):.1f}")
        print(f"Overall min length: {min(all_lengths)}")
        print(f"Overall max length: {max(all_lengths)}")
    
    print()
    print()
    
    # LAYOUT EFFICIENCY METRICS
    print("LAYOUT EFFICIENCY METRICS")
    print("-" * 80)
    print(f"Current fixed rows: {num_rows}")
    print(f"Left frame: {left_num_buttons} buttons ÷ {num_rows} rows = {left_num_cols} columns needed")
    print(f"Right frame: {right_num_buttons} buttons ÷ {num_rows} rows = {right_num_cols} columns needed")
    print()
    
    # Show optimal recommendations
    print("RECOMMENDED OPTIMAL ROWS:")
    print(f"  Left frame: {optimal_rows_left} rows (based on {sum(left_lengths)} total chars)")
    print(f"    → Results in {left_num_cols} columns")
    print(f"  Right frame: {optimal_rows_right} rows (based on {sum(right_lengths)} total chars)")
    print(f"    → Results in {right_num_cols} columns")
    print()
    print(f"FRAME WIDTH ALLOCATION:")
    print(f"  Left:Right ratio = {left_num_cols}:{right_num_cols}")
    if left_num_cols > 0 and right_num_cols > 0:
        total_cols = left_num_cols + right_num_cols
        left_percent = (left_num_cols / total_cols) * 100
        right_percent = (right_num_cols / total_cols) * 100
        print(f"  Left frame will occupy ~{left_percent:.0f}% of horizontal space")
        print(f"  Right frame will occupy ~{right_percent:.0f}% of horizontal space")
    print()
    
    if optimal_rows_left != num_rows or optimal_rows_right != num_rows:
        print("⚠️  RECOMMENDATION: Current fixed 2-row layout may not be optimal!")
        print(f"   Consider using {optimal_rows_left} rows for left and {optimal_rows_right} rows for right")
        if optimal_rows_left == optimal_rows_right:
            print(f"   Or use a unified {optimal_rows_left} rows for both sides")
    else:
        print("✓  Current 2-row layout appears appropriate for the data")
    
    print()
    
    # Calculate theoretical optimal row count based on text lengths
    if left_lengths:
        total_left_chars = sum(left_lengths)
        avg_left_chars_per_button = total_left_chars / len(left_lengths)
        print(f"Left axis average characters per button: {avg_left_chars_per_button:.1f}")
        print(f"  - If each row can fit ~150 chars, optimal rows: {math.ceil(total_left_chars / 150)}")
        print(f"  - If each row can fit ~180 chars, optimal rows: {math.ceil(total_left_chars / 180)}")
        print(f"  - If each row can fit ~200 chars, optimal rows: {math.ceil(total_left_chars / 200)}")
    
    if right_lengths:
        total_right_chars = sum(right_lengths)
        avg_right_chars_per_button = total_right_chars / len(right_lengths)
        print(f"Right axis average characters per button: {avg_right_chars_per_button:.1f}")
        print(f"  - If each row can fit ~150 chars, optimal rows: {math.ceil(total_right_chars / 150)}")
        print(f"  - If each row can fit ~180 chars, optimal rows: {math.ceil(total_right_chars / 180)}")
        print(f"  - If each row can fit ~200 chars, optimal rows: {math.ceil(total_right_chars / 200)}")
    
    print()
    print("Note: Updated implementation can calculate optimal rows dynamically.")
    print("      Layout fills VERTICALLY (row 0, then row 1, etc., then next column).")
    print()
    print("=" * 80)
    
    return {
        'left': {
            'num_buttons': left_num_buttons,
            'num_cols': left_num_cols,
            'lengths': left_lengths,
            'total_chars': sum(left_lengths) if left_lengths else 0,
            'avg_length': sum(left_lengths) / len(left_lengths) if left_lengths else 0,
            'optimal_rows': optimal_rows_left
        },
        'right': {
            'num_buttons': right_num_buttons,
            'num_cols': right_num_cols,
            'lengths': right_lengths,
            'total_chars': sum(right_lengths) if right_lengths else 0,
            'avg_length': sum(right_lengths) / len(right_lengths) if right_lengths else 0,
            'optimal_rows': optimal_rows_right
        },
        'num_rows': num_rows,
        'optimal_rows_left': optimal_rows_left,
        'optimal_rows_right': optimal_rows_right
    }


if __name__ == "__main__":
    print("This module provides button text analysis functions.")
    print("Import it in your notebook and call analyze_button_layout(df_axL, df_axR)")
    print()
    print("Main functions:")
    print("  - calculate_optimal_rows(column_names, max_chars_per_row=180, min_rows=1, max_rows=4)")
    print("      Calculate optimal row count based on text lengths")
    print()
    print("  - analyze_button_layout(df_left, df_right=None)")
    print("      Full analysis with recommendations")
    print()
    print("Example usage:")
    print("  from calculate_button_text_metrics import calculate_optimal_rows")
    print("  optimal_rows = calculate_optimal_rows(['Series A', 'Series B', 'Long Series Name C'])")
    print(f"  # Returns: recommended number of rows")
