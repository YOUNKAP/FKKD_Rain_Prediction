import os
import pandas as pd
import re

def extract_year_month_from_filename(filename):
    """Extract year and month from filename like metar_only_raw_2021_01.csv"""
    match = re.search(r"(\d{4})_(\d{2})", filename)
    if match:
        return match.group(1), match.group(2)
    else:
        return None, None

def add_year_month_to_csv(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(input_folder):
        if file.endswith(".csv"):
            input_path = os.path.join(input_folder, file)
            year, month = extract_year_month_from_filename(file)

            if year and month:
                df = pd.read_csv(input_path)
                df["Year"] = year
                df["Month"] = month

                output_path = os.path.join(output_folder, file)
                df.to_csv(output_path, index=False)
                print(f"✅ Updated file: {output_path}")
            else:
                print(f"❌ Skipped (invalid filename): {file}")

# -------------------------
# 🔁 CONFIGURE THIS SECTION
# -------------------------

if __name__ == "__main__":
    input_folder = "output_metar_csv"            # Where your original CSVs are
    output_folder = "output_with_year_month"     # Where you want to save updated CSVs

    add_year_month_to_csv(input_folder, output_folder)

