import json
import re

import pandas as pd
from rich.console import Console

console = Console()


def add_overall_percentage(df: pd.DataFrame):
    """
    Adds a new column 'Overall_Percentage' to the DataFrame,
    calculating the average of all columns containing '%' in their name.

    Args:
        df (pd.DataFrame): The input DataFrame, expected to have a student name
                           column (first column) and multiple percentage columns.

    Returns:
        pd.DataFrame: The DataFrame with the new 'Overall_Percentage' column.
                      Returns an empty DataFrame if the input is empty or no
                      percentage columns are found.
    """
    if df.empty:
        print("Input DataFrame is empty. Cannot calculate overall percentage.")
        return pd.DataFrame()

    df_with_overall = df.copy() # Work on a copy to avoid modifying the original DataFrame

    # Identify columns that contain '%' in their name (case-insensitive)
    # These are assumed to be the percentage columns to average.
    percentage_columns = df_with_overall.filter(regex=r'(?i)%')

    if percentage_columns.empty:
        print("No percentage columns found (columns with '%' in their name).")
        # You might want to return the original DataFrame or raise an error here
        return df_with_overall

    # Calculate the mean across rows (axis=1) for the identified percentage columns.
    # This computes the overall percentage for each student.
    df_with_overall['OVERALL%'] = percentage_columns.mean(axis=1)

    # Round the overall percentage to two decimal places for readability
    df_with_overall['OVERALL%'] = df_with_overall['OVERALL%'].round(2)

    return df_with_overall, "OVERALL%"


def normalize_columns_to_1_100(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes all numeric columns in a DataFrame to a range of 1 to 100.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: A new DataFrame with normalized values.
    """
    # Create a copy to avoid modifying the original DataFrame
    df_normalized = df.copy()

    # Get a list of all numeric columns
    numeric_cols = df_normalized.select_dtypes(include=['number']).columns

    for col in numeric_cols:
        col_min = df_normalized[col].min()
        col_max = df_normalized[col].max()
        if (col_min < 1 and col_max < 1):
            df_normalized[col] = round(df_normalized[col] * 100, 2)
        else:
            df_normalized[col] = round(df_normalized[col], 2)

        # # Handle the case where all values in the column vare the same (range is 0)
        # if col_max == col_min:
        #     # If all values are the same, they should all map to the middle of the new range
        #     df_normalized[col] = 50.5
        # else:
        #     # df_normalized[col] = ((df_normalized[col] - col_min) / (col_max - col_min)) * 99 + 1

    return df_normalized

def clean_key(key: str) -> str:
    return re.sub(r'[^A-Za-z0-9]', '', str(key))


def get_low_attendance_students(df: pd.DataFrame, min_percentage: float):
    """
    Extracts names of students and their percentages with attendance
    less than min_percentage for each percentage column.

    Args:
        df (pd.DataFrame): The input DataFrame. The first column is assumed to be
                           student names, and other columns with '%' are
                           assumed to be attendance percentages.
        min_percentage (float): The minimum required attendance percentage.

    Returns:
        str: A JSON string with column names as keys and a nested JSON object
             (student names as keys, percentages as values) as values.
    """
    try:
        subjects = []
        if df.empty:
            return json.dumps({}), subjects, "Empty Dataframe"

        # Assuming the first column is always the student name
        student_name_column = df.columns[0]

        # Remove the Total classes row
        # Create a boolean mask to identify rows where the first column
        # is NOT equal to "Total" (case-sensitive)
        mask = ~df[student_name_column].str.contains('Total', case=False, na=False)

        # Use the mask to filter the DataFrame
        df = df[mask]

        # Identify percentage columns (case-insensitive for '%')
        # Normalize the numeric columns
        df = normalize_columns_to_1_100(df)
        percentage_columns = df.filter(regex=r'(?i)%').columns.tolist()
        if student_name_column in percentage_columns:
            percentage_columns.remove(student_name_column)

        low_attendance_summary = {}

        # Iterate through each identified percentage column
        for col in percentage_columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Filter rows where attendance is less than the min percentage
                low_attendance_df = df[df[col] < min_percentage]

                # Create a dictionary for the current subject
                subject_summary = {}
                for _, row in low_attendance_df.iterrows():
                    student_name = row[student_name_column]
                    percentage = row[col]
                    # Populate the inner dictionary
                    subject_summary[student_name] = percentage

                # Add the subject's dictionary to the main summary
                col = clean_key(col)
                subjects.append(col)
                low_attendance_summary[col] = subject_summary
            else:
                print(f"Warning: Column '{col}' is not numeric and will be skipped.")

        return json.dumps(low_attendance_summary, indent=4), subjects, "success"
    except Exception as e:
        console.print(f"Error in finding low attendance students : {e}", style="bold red")
        return json.dumps({}), subjects, "Failed to find low attendance students"
