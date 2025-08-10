#!/usr/bin/env python3

import json

import gradio as gr
import pandas as pd
from pandas.errors import EmptyDataError
from rich.console import Console

from helper import get_header_info, summarize_attendance_sheet_with_gemini

# Global variables
uploaded_df = None
subject_names = []
header_rows = []
subject_row = 0 
response_data = ""
summarization = {}
console = Console()

def column_rename(column_name):
    if isinstance(column_name, tuple):
        return "-".join([word for i, word in enumerate(column_name) if "Unnamed" not in word])
    return str(column_name)

def process_file(file_obj):
    global uploaded_df, subject_names, summarization
    
    print("*"*100)
    if file_obj is None:
        return pd.DataFrame({"Error": ["No file uploaded."]}), gr.update(choices=[])

    file_path = file_obj.name
    try:
        # First read to get subject names and header info
        try:
            df_initial = pd.read_excel(file_path)
        except EmptyDataError:
            return pd.DataFrame({"Error": ["The uploaded file is empty."]}), gr.update(choices=[])
        except Exception as e:
            return pd.DataFrame({"Error": [f"Failed to read file: {e}"]}), gr.update(choices=[])
        console.print("Excel file read", style="bold purple")

        # Get header info from Gemini
        response_data = get_header_info(df_initial)
        # print(response_data)
        if "error" in response_data.lower() or "fail" in response_data.lower():
                console.print(f"Error getting initial header info from Gemini: {response_data}", style="bold red")
                return pd.DataFrame({"Error": [response_data]}), gr.update(choices=[])
        console.print("Got header info from Gemini", style="bold purple")

        # Safely parse the JSON structure
        try:
            json_str = response_data[response_data.find("{"):response_data.rfind("}") + 1].strip()
            header_info = json.loads(json_str)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            console.print(f"Error parsing Gemini response for header info: {e}", style="bold red")
            return pd.DataFrame({"Error": [f"Gemini response parsing failed for header info: {e}"]}), gr.update(choices=[])

        header_rows = header_info.get("header rows list", [])
        try:
            if not header_rows:
                header_rows = list(header_info.items())[0]
        except Exception:
            pass
        if not header_rows:
            return pd.DataFrame({"Error": ["Could not determine header rows from Gemini."]}), gr.update(choices=[])
        console.print(f"Header rows: {header_rows}", style="bold green")

        subject_row = header_info.get("subject header row", 0)
        try:
            if not subject_row:
                subject_row = list(header_info.items())[1]
        except Exception:
            pass
        if subject_row == 0:
            return pd.DataFrame({"Error": ["Could not determine subject header row from Gemini."]}), gr.update(choices=[])
        console.print(f"Subject row: {subject_row}", style="bold green")
        console.print("successfully parsed header information", style="bold purple")

        # Second read with the correct headers
        df_final = pd.read_excel(file_path, header=[h - 1 for h in header_rows])
        df_final.columns = [column_rename(col) for col in df_final.columns]
        df_final = df_final.fillna(0)
        uploaded_df = df_final

        # Get subject names
        try:
            subject_names = df_initial.iloc[subject_row-2].dropna().tolist()
            subject_names = [str(s).strip().upper() for s in subject_names if pd.notna(s)]
            # subject_names = [str(s).strip().upper() for s in df_initial.iloc[subject_row - 2].dropna().tolist() if pd.notna(s)]
            if not subject_names:
                return pd.DataFrame({"Error": ["Could not extract subject names."]}), gr.update(choices=[])
            subject_names.append("OVERALL")
            console.print(f"Subject Names: {subject_names}", style="bold green")
        except IndexError:
            return pd.DataFrame({"Error": ["Subject row not found or out of bounds."]}), gr.update(choices=[])
        console.print("Obtained subject names", style="bold purple")

        # Summarize attendance with Gemini
        response_data_summary = summarize_attendance_sheet_with_gemini(uploaded_df, subject_names)
        if "error" in response_data_summary.lower() or "fail" in response_data_summary.lower():
            console.print(f"Error summarizing attendance with Gemini: {response_data_summary}", style="bold red")
            return pd.DataFrame({"Error": [response_data_summary]}), gr.update(choices=[])
        console.print("Obtained final summary of attendance from Gemini", style="bold purple")
            
        try:
            json_str_summary = response_data_summary[response_data_summary.find("{"):response_data_summary.rfind("}") + 1].strip()
            summarization = json.loads(json_str_summary)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            console.print(f"Error parsing Gemini response for summarization: {e}", style="bold red")
            return pd.DataFrame({"Error": [f"Gemini response parsing failed for summarization: {e}"]}), gr.update(choices=[])
        console.print("Successfully parsed final summary of attendance", style="bold purple")
        print("*"*100)

        return uploaded_df, gr.update(choices=subject_names, value=subject_names[0] if subject_names else None)
    except Exception as e:
        console.print(f"An unexpected error occurred during file processing: {e}", style="bold red")
        return pd.DataFrame({"Error": ["An unexpected error occurred. Please retry"]}), gr.update(choices=[])


def select(subject):
    """Displays the list of students for the selected subject."""
    if not summarization or subject not in summarization:
        return "No information available for this subject."
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
    app.launch()
