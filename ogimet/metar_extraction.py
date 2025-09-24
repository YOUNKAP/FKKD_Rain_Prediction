def extract_metar_speci(input_file, output_file):
    start_marker = "###################################\n#  METAR/SPECI de FKKD\n###################################"
    end_marker_1 = "# No hay TAF CORTOS de FKKD en el periodo solicitado."
    end_marker_2 = "###################################\n#  TAF LARGOS de FKKD\n###################################"

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    start_idx = content.find(start_marker)
    if start_idx == -1:
        raise ValueError("Start marker not found in file.")

    start_idx += len(start_marker)

    # Find the earliest of the two possible end markers
    end_idx_1 = content.find(end_marker_1, start_idx)
    end_idx_2 = content.find(end_marker_2, start_idx)
    possible_ends = [idx for idx in [end_idx_1, end_idx_2] if idx != -1]

    if not possible_ends:
        raise ValueError("No valid end marker found after start marker.")

    end_idx = min(possible_ends)

    # Extract and clean the data
    metar_data = content[start_idx:end_idx].strip()

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write(metar_data)

    print(f"METAR/SPECI data saved to '{output_file}'.")

# Example usage
extract_metar_speci("raw_2024_12.txt", "metar_only.txt")
