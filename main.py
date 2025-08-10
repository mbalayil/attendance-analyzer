#!/usr/bin/env python3

import json

import gradio as gr
import pandas as pd
from rich.console import Console

from helper import get_header_info, summarize_attendance_sheet_with_gemini

# Global variables
uploaded_df = None
subject_names = []
header_rows = []
subject_row = 0 
response_data = ""
console = Console()

def column_rename(column_name):
    return "-".join([word for i, word in enumerate(column_name) if "Unnamed" not in word])

def get_initial_info(df):
    try:
        # Call the summarization function with the DataFrame
        r = get_header_info(df)
        if ("error" in r.lower()) or ("fail" in r.lower()):
            return "error"
    except Exception as e:
        console.print(f"Gemini API call error :{e}", style="bold red")
        return "error"

    return r

def summarize(df, subjects):
    """
    Takes a pandas dataframe, pass the dataframe to the Gemini API and get the response.

    Args:
        df : Pandas dataframe.

    Returns:
        str: Give list of students with less than 75% attendance subjectwise and in total
    """
    try:
        # Call the summarization function with the DataFrame
        r = summarize_attendance_sheet_with_gemini(df, subjects)
        if ("error" in r.lower()) or ("fail" in r.lower()):
            return "error"
    except Exception:
        console.print("Gemini API call error")
        return "error"

    return r

def process_file(file_obj):
    global uploaded_df
    global subject_names
    global summarization
    global subject_row, header_rows
    if file_obj is None:
        return pd.DataFrame({"Error": ["No file uploaded."]}), gr.update(choices=[])

    file_path = file_obj.name
    # try:
    # First read to get subject names
    df = pd.read_excel(file_path)
    response_data = get_initial_info(df)
    print(response_data)
    header_info = json.loads(
        response_data[response_data.find("{") : response_data.rfind("}") + 1].strip()
    )
    print("&"*100)
    print(header_info["header rows list"])
    header_rows = header_info["header rows list"]
    header_rows = [(h-1) for h in header_rows]
    print(header_info["subject header row"])
    subject_row = header_info["subject header row"]
    print("&"*100)
    subject_names = df.iloc[subject_row-2].dropna().tolist()
    # subject_names = [s.upper() for s in subject_names]
    # subject_names = [str(s).strip().upper() for s in subject_names]
    subject_names = [str(s).strip().upper() for s in subject_names if pd.notna(s)]
    subject_names.append("OVERALL")
    print(subject_names)
    response_data = summarize_attendance_sheet_with_gemini(df, subject_names)
    print(response_data)
    summarization = json.loads(
        response_data[response_data.find("{") : response_data.rfind("}") + 1].strip()
    )
    print(summarization)

    # Second read with headers
    df = pd.read_excel(file_path, header=header_rows)
    df = df.fillna(0)
    df.columns = [column_rename(col) for col in df.columns]
    uploaded_df = df

    return uploaded_df, gr.update(choices=subject_names, value=subject_names[0] if subject_names else None)

def select(subject):
    if summarization[subject]:
        return summarization[subject]
    else:
        return "No information available"

if __name__ == '__main__':
    with gr.Blocks() as app:
        gr.Markdown("# Attendance Analyzer")
        gr.Markdown("Upload an Excel file (.xlsx or .xls) to view its contents.")

        file_input = gr.File(label="Upload Excel", file_types=[".xlsx", ".xls"])
        process_file_butn = gr.Button("Submit")
        output_preview = gr.DataFrame(label="Excel Preview")
        subject_selector = gr.Dropdown(label="Select subjects", choices=[])
        process_file_butn.click(fn=process_file, inputs=[file_input], outputs=[output_preview, subject_selector])

        output_textbox = gr.Textbox(label="Students with less than 75% attendance")
        subject_selector.change(select, inputs=subject_selector, outputs=output_textbox)

        print("&"*100)
        print(subject_names)
        print("&"*100)

    app.launch()
