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

def process_metar_folder(input_folder, output_csv):
    """Process all .txt files in the given folder and save the parsed data to a CSV file."""
    results = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(input_folder, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        parsed = parse_metar_line(line)
                        results.append(parsed)

    # Write the results to a CSV file
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Time", "Wind", "Visibility", "Temperature", "Sea Level Pressure", "Rain"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ Extraction completed. Saved to {output_csv}")

# -------------------------
# 🔁 CONFIGURE THIS SECTION
# -------------------------

if __name__ == "__main__":
    input_folder = "input_metar_data"        # Folder with .txt files
    output_csv = "parsed_metar_output.csv"   # Output CSV file

    os.makedirs(input_folder, exist_ok=True)
    process_metar_folder(input_folder, output_csv)
