import os
import re
import csv

def parse_metar_line(line):
    """Extract specific fields from a METAR/SPECI report line."""
    time_match = re.search(r"\b(\d{6}Z)\b", line)
    wind_match = re.search(r"\b(\w{5,7}KT)\b", line)
    visibility_match = re.search(r"\b\d{4}\b", line[line.find(wind_match.group()):]) if wind_match else None
    temp_match = re.search(r"\b\d{2}/\d{2}\b", line)
    pressure_match = re.search(r"\bQ\d{4}\b", line)
    rain_match = "YES" if "RA" in line else "NO"

    return {
        "Time": time_match.group() if time_match else "",
        "Wind": wind_match.group() if wind_match else "",
        "Visibility": visibility_match.group() if visibility_match else "",
        "Temperature": temp_match.group() if temp_match else "",
        "Sea Level Pressure": pressure_match.group() if pressure_match else "",
        "Rain": rain_match
    }

def process_metar_file(input_file, output_file):
    """Process a single METAR file and write parsed data to a CSV file."""
    results = []
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                parsed = parse_metar_line(line)
                results.append(parsed)

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Time", "Wind", "Visibility", "Temperature", "Sea Level Pressure", "Rain"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ Created: {output_file}")

def process_metar_folder(input_folder, output_folder):
    """Process all .txt files from input_folder, writing one .csv per file in output_folder."""
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_folder, filename)
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(output_folder, f"{base_name}.csv")
            process_metar_file(input_path, output_path)

# -------------------------
# 🔁 CONFIGURE THIS SECTION
# -------------------------

if __name__ == "__main__":
    input_folder = "input_metar_data"       # Folder containing .txt files
    output_folder = "output_metar_csv"      # Folder to store .csv files

    process_metar_folder(input_folder, output_folder)
