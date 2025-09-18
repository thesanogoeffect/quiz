import gspread
import pandas as pd
import os
from google.oauth2.service_account import Credentials

L1_SPREADSHEET_ID = '1BGOaJcSqKCa5QIiCgcXjqCUY9eizKWHP6Ltv4Em9LKU'
L1_SHEET_NAME = 'Sheet1'

CHAPTER_ERRORS_SPREADSHEET_ID = '100t8tCR_0TJHlGHdGPD5g1kh4u6UO8_UwQGlpzVuc2U'
CHAPTER_ERRORS_SHEET_NAME = 'Form Responses 1'

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

# Load credentials from JSON file with the required scopes
def load_credentials(json_path):
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = Credentials.from_service_account_file(json_path, scopes=scopes)
    return credentials

credentials = load_credentials('credentials.json')

# Download data from Google Sheet into a DataFrame
def download_l1_gsheet_to_df():
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(L1_SPREADSHEET_ID).worksheet(L1_SHEET_NAME)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# Upload DataFrame to Google Sheet (Append Mode)
def upload_l1_df_to_gsheet(df):
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(L1_SPREADSHEET_ID).worksheet(L1_SHEET_NAME)
    
    # Convert DataFrame to a list of lists for appending
    data_to_append = df.values.tolist()
    
    # Append each row of the DataFrame to the sheet
    for row in data_to_append:
        sheet.append_row(row)


def get_chapter_errors_table_as_df():
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(CHAPTER_ERRORS_SPREADSHEET_ID).worksheet(CHAPTER_ERRORS_SHEET_NAME)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# Usage example
