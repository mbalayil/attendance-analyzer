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

    **Input:** Raw CSV content representing attendance of students in different subjects
    CSV:
    {csv_content}
    Subjects: {subjects}

    **Task:**
    1. Find the list of all students with less than 75 percent attendance in each subject including theory and practical.
    2. Find the list of all students with less than 75 percent attendance total (in all subjects combined) including theory and practical.

    **Output as JSON - keys being subject names, values being the names of students and their attendance percentage:**
    **Give the key name for overall attendance details as "Overall". Overall attendance for each student is the sum of the attendance in all subjects
    **Total number of classes for each category is also mentioned in the data**
    **Sample output**
     "subject 1":"name 1":"percentage 1", "name 2":"percentage 2",
     "subject 2":"name 1":"percentage 1", "name 2":"percentage 2", "name 3":"percentage 3",
     ...
     "subject n":"name 1":"percentage 1",
     "OVERALL":"name 1":"percentage 1",
    """
    return prompt


def get_header_info(df: pd.DataFrame) -> str:
    """
    Takes a pandas DataFrame containing attendance data, converts it to a CSV string,
    sends it to the Gemini API for summarization, and returns the header information.

    Args:
        df (pd.DataFrame): The pandas DataFrame containing the timesheet data.

    Returns:
        str: Details of the header info.
    """
    # Convert the DataFrame to CSV content string
    # index=False prevents writing the DataFrame index as a column in the CSV string
    csv_content = df.to_csv(index=False)

    # Gemini API configuration
    api_key = os.getenv("GEMINI_API_KEY")
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    # Craft the prompt for Gemini
    prompt = get_prompt_initial(csv_content)

    # Prepare the payload for the API request
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    max_retries = 3  # Maximum number of retries
    retry_delay_seconds = 5  # Delay between retries in seconds

    # Send request to Gemini
    print("Sending request to Gemini API...")
    for attempt in range(max_retries):
        console.print(f"Attempt#: {attempt}", style="bold red")
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            result = response.json()

            # Extract the generated text from the response
            if result and result.get("candidates") and len(result["candidates"]) > 0:
                generated_text = (
                    result["candidates"][0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "No summary found.")
                )
                console.print(f"Text Generated in attempt#: {attempt}", style="bold green")
                # console.print(f"Text Generated: {generated_text}", style="bold blue")
                return generated_text
            else:
                return f"Error: Unexpected API response structure: {json.dumps(result, indent=2)}"

        except requests.HTTPError as http_err:
            # Check for 503 Service Unavailable or other server errors (5xx)
            if http_err.response.status_code >= 500 and attempt < max_retries - 1:
                print(
                    f"Attempt {attempt + 1}/{max_retries}: Server error ({http_err.response.status_code}). Retrying in {retry_delay_seconds} seconds..."
                )
                time.sleep(retry_delay_seconds)
            else:
                # Re-raise the error if it's not a server error or if max retries reached
                return f"Error connecting to Gemini API after {attempt + 1} attempts: {http_err}"
        except requests.ConnectionError as conn_err:
            # Handle network-related errors (e.g., DNS failure, refused connection)
            if attempt < max_retries - 1:
                print(
                    f"Attempt {attempt + 1}/{max_retries}: Connection error. Retrying in {retry_delay_seconds} seconds..."
                )
                time.sleep(retry_delay_seconds)
            else:
                return f"Error connecting to Gemini API after {attempt + 1} attempts: {conn_err}"
        except requests.Timeout as timeout_err:
            # Handle request timeouts
            if attempt < max_retries - 1:
                print(
                    f"Attempt {attempt + 1}/{max_retries}: Timeout error. Retrying in {retry_delay_seconds} seconds..."
                )
                time.sleep(retry_delay_seconds)
            else:
                return f"Error connecting to Gemini API after {attempt + 1} attempts: {timeout_err}"
        except json.JSONDecodeError:
            return f"Error decoding JSON response: {response.text}"
        except Exception as e:
            # Catch any other unexpected errors
            return f"An unexpected error occurred during API call: {e}"
    return "Failed to get a summary after multiple retries."  # Should ideally not be reached if max_retries is handled correctly


def summarize_attendance_sheet_with_gemini(df: pd.DataFrame, subjects: list) -> str:
    """
    Takes a pandas DataFrame containing attendance data, converts it to a CSV string,
    sends it to the Gemini API for summarization, and returns the summarized
    activities as a string.

    Args:
        df (pd.DataFrame): The pandas DataFrame containing the timesheet data.
        subjects (list): The list of subjects.

    Returns:
        str: Details of the students with less attendance summarized by Gemini,
             or an error message if the API call fails.
    """
    # Convert the DataFrame to CSV content string
    # index=False prevents writing the DataFrame index as a column in the CSV string
    csv_content = df.to_csv(index=False)

    # Gemini API configuration
    api_key = os.getenv("GEMINI_API_KEY")
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    # Craft the prompt for Gemini
    prompt = get_prompt(csv_content, subjects)

    # Prepare the payload for the API request
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    max_retries = 3  # Maximum number of retries
    retry_delay_seconds = 5  # Delay between retries in seconds

    # Send request to Gemini
    print("Sending request to Gemini API...")
    for attempt in range(max_retries):
        console.print(f"Attempt#: {attempt}", style="bold red")
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            result = response.json()

            # Extract the generated text from the response
            if result and result.get("candidates") and len(result["candidates"]) > 0:
                generated_text = (
                    result["candidates"][0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "No summary found.")
                )
                console.print(f"Text Generated in attempt#: {attempt}", style="bold green")
                # console.print(f"Text Generated: {generated_text}", style="bold blue")
                return generated_text
            else:
                return f"Error: Unexpected API response structure: {json.dumps(result, indent=2)}"

        except requests.HTTPError as http_err:
            # Check for 503 Service Unavailable or other server errors (5xx)
            if http_err.response.status_code >= 500 and attempt < max_retries - 1:
                print(
                    f"Attempt {attempt + 1}/{max_retries}: Server error ({http_err.response.status_code}). Retrying in {retry_delay_seconds} seconds..."
                )
                time.sleep(retry_delay_seconds)
            else:
                # Re-raise the error if it's not a server error or if max retries reached
                return f"Error connecting to Gemini API after {attempt + 1} attempts: {http_err}"
        except requests.ConnectionError as conn_err:
            # Handle network-related errors (e.g., DNS failure, refused connection)
            if attempt < max_retries - 1:
                print(
                    f"Attempt {attempt + 1}/{max_retries}: Connection error. Retrying in {retry_delay_seconds} seconds..."
                )
                time.sleep(retry_delay_seconds)
            else:
                return f"Error connecting to Gemini API after {attempt + 1} attempts: {conn_err}"
        except requests.Timeout as timeout_err:
            # Handle request timeouts
            if attempt < max_retries - 1:
                print(
                    f"Attempt {attempt + 1}/{max_retries}: Timeout error. Retrying in {retry_delay_seconds} seconds..."
                )
                time.sleep(retry_delay_seconds)
            else:
                return f"Error connecting to Gemini API after {attempt + 1} attempts: {timeout_err}"
        except json.JSONDecodeError:
            return f"Error decoding JSON response: {response.text}"
        except Exception as e:
            # Catch any other unexpected errors
            return f"An unexpected error occurred during API call: {e}"
    return "Failed to get a summary after multiple retries."  # Should ideally not be reached if max_retries is handled correctly
