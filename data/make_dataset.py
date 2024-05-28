import os

import pandas as pd

INPUT_PATH = "data/raw/"
EXPORT_PATH = "data/processed/"

"""
1. Go to TradingView
2. Select "Export chart data"
3. Select "ISO Time"
"""


def extract_transform_dataset():
    # List all files in the folder with a .csv extension
    csv_files = [f for f in os.listdir(INPUT_PATH) if f.endswith(".csv")]

    for csv_file in csv_files:
        # Read a CSV files
        csv_file_path = os.path.join(INPUT_PATH, csv_file)
        df = pd.read_csv(csv_file_path)

        # Set the 'time' column as the index
        df.set_index("time", inplace=True)

        # Convert column names to lowercase and replace spaces with underscores
        df.columns = df.columns.str.lower().str.replace(" ", "_")

        # Export a CSV files
        output_csv_path = os.path.join(EXPORT_PATH + csv_file)
        df.to_csv(output_csv_path)


if __name__ == "__main__":
    extract_transform_dataset()
