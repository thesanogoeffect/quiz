from scripts.gsheets import download_l1_gsheet_to_df
import pandas as pd
import sqlite3
from scripts.db_operations import create_table, process_new_questions


# Step 1: Download the data from the Google Sheet
df = download_l1_gsheet_to_df()

# Step 2: Load current snapshot, if it exists
try:
    snapshot_df = pd.read_csv("l1_latest_snapshot.csv", index_col=0)  # Load snapshot with index
except FileNotFoundError:
    snapshot_df = None

# Step 3: Compare DataFrames and get new rows
if snapshot_df is not None:
    # If there's a snapshot, compare and filter new rows
    new_rows_df = df[~df.index.isin(snapshot_df.index)]
else:
    # If no snapshot exists, assume all rows are new
    new_rows_df = df

# Step 4: Save the DataFrame as a new snapshot, including the index
df.to_csv("l1_latest_snapshot.csv", index=True)

# Step 6: Insert new data into the SQLite database
if not new_rows_df.empty:
    process_new_questions(new_rows_df)
