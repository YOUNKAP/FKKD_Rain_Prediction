import os

def extract_metar_speci_from_text(text):
    start_marker = "###################################\n#  METAR/SPECI de FKKD\n###################################"
    end_marker_1 = "# No hay TAF CORTOS de FKKD en el periodo solicitado."
    end_marker_2 = "###################################\n#  TAF LARGOS de FKKD\n###################################"

    start_idx = text.find(start_marker)
    if start_idx == -1:
        return None  # Start not found

    start_idx += len(start_marker)
    end_idx_1 = text.find(end_marker_1, start_idx)
    end_idx_2 = text.find(end_marker_2, start_idx)
    valid_ends = [i for i in (end_idx_1, end_idx_2) if i != -1]

    if not valid_ends:
        return None  # No end marker found

    end_idx = min(valid_ends)
    return text[start_idx:end_idx].strip()

def process_metar_files(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_dir, filename)
            with open(input_path, 'r', encoding='utf-8') as file:
                content = file.read()

            metar_data = extract_metar_speci_from_text(content)

            if metar_data:
                output_path = os.path.join(output_dir, f"metar_only_{filename}")
                with open(output_path, 'w', encoding='utf-8') as out_file:
                    out_file.write(metar_data)
                print(f"[✓] Saved METAR/SPECI from {filename} to {output_path}")
            else:
                print(f"[!] METAR section not found in {filename}")

# Example usage
process_metar_files("input_metar_folder", "output_metar_folder")
