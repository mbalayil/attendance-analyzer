#!/usr/bin/env python3

import json
import os
import time

import pandas as pd
import requests
from rich.console import Console

console = Console()

def get_prompt_initial(csv_content):
    prompt = f"""
    You are a data analyst.

    **Input:** Raw CSV content representing attendance of students in different subjects
    CSV:
    {csv_content}

    **Task:**
    1. Find the header row numbers of the dataframe
    2. Find the row number of main subject headings in the dataframe

    **Output as JSON - keys being header rows, main subject heading row and **
    **Sample output**
     "header rows list": 5, 6, 7 (found in Task 1)
     "subject header row": 6 (found in Task 2)
    """
    return prompt


def get_prompt(csv_content, subjects):
    prompt = f"""
    You are a data analyst.

    **Input:** Raw CSV content representing attendance of students in different subjects.
    CSV:
    {csv_content}
    Subjects: {subjects}

    **Task:**
    Formula to calculate percentage of attendance in a subject = (Total classes attended by student / Total classes in that subject) * 100
    1. Find the list of all students with less than 75 percentage attendance in each subject including theory and practical.
    2. Find the list of all students with less than 75 percentage attendance total (in all subjects combined) including theory and practical.

    **Output as JSON - keys being subject names, values being the names of students and their attendance percentage:**
    **Give the key name for overall attendance details as "Overall". Overall attendance for each student is the sum of the attendance in all subjects
    **Total number of classes for each category is also mentioned in the data**
    **Percentage to be rounded to 2 decimal places**
    **Sample output**
     "subject 1":"name 1":"percentage 1", "name 2":"percentage 2",
     "subject 2":"name 1":"percentage 1", "name 2":"percentage 2", "name 3":"percentage 3",
     ...
     "subject n":"name 1":"percentage 1",
     "OVERALL":"name 1":"percentage 1",
    """
    return prompt

def _call_gemini_api(prompt, max_retries=3, retry_delay_seconds=5):
    """A helper function to handle the Gemini API call with retries and error handling."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "error: GEMINI_API_KEY environment variable not set."

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    
    for attempt in range(max_retries):
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=30)
            response.raise_for_status()  # Raise HTTPError for bad responses
            result = response.json()

            if result and result.get("candidates") and len(result["candidates"]) > 0:
                generated_text = result["candidates"][0].get("content", {}).get("parts", [{}])[0].get("text", "No summary found.")
                return generated_text
            else:
                return f"error: Unexpected API response structure: {json.dumps(result, indent=2)}"

        except requests.HTTPError as http_err:
            if http_err.response.status_code >= 500 and attempt < max_retries - 1:
                console.print(f"Attempt {attempt + 1}/{max_retries}: Server error ({http_err.response.status_code}). Retrying...", style="yellow")
                time.sleep(retry_delay_seconds)
            else:
                return f"error: Gemini API request failed: {http_err}"
        except (requests.ConnectionError, requests.Timeout) as err:
            if attempt < max_retries - 1:
                console.print(f"Attempt {attempt + 1}/{max_retries}: Connection error. Retrying...", style="yellow")
                time.sleep(retry_delay_seconds)
            else:
                return f"error: Connection or timeout error after {attempt + 1} attempts: {err}"
        except json.JSONDecodeError:
            return f"error: Failed to decode JSON response from Gemini. Response text: {response.text}"
        except Exception as e:
            return f"error: An unexpected error occurred during API call: {e}"

    return "error: Failed to get a response after multiple retries."

def get_header_info(df: pd.DataFrame) -> str:
    """Takes a DataFrame, converts to CSV, and calls Gemini for header info."""
    if df.empty:
        return "error: Input DataFrame is empty."
    csv_content = df.to_csv(index=False)
    prompt = get_prompt_initial(csv_content)
    return _call_gemini_api(prompt)

def summarize_attendance_sheet_with_gemini(df: pd.DataFrame, subjects: list) -> str:
    """Takes a DataFrame and subjects, converts to CSV, and calls Gemini for attendance summary."""
    if df.empty or not subjects:
        return "error: Input DataFrame is empty or subjects list is empty."
    csv_content = df.to_csv(index=False)
    prompt = get_prompt(csv_content, subjects)
    return _call_gemini_api(prompt)
