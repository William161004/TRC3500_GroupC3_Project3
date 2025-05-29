import os
file_name = "adc_test.data"

def extract_and_clean(filename):
    output_lines = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("Ca=") and "Cb=" in line:
                try:
                    parts = line.replace("Ca=", "").replace("Cb=", "").split()
                    val1 = int(parts[0])
                    val2 = int(parts[1])
                    output_lines.append(f"{val1} {val2}")
                except (IndexError, ValueError):
                    continue  # Skip malformed lines

    # Overwrite the original file with the cleaned output
    with open(filename, 'w') as f:
        f.write("\n".join(output_lines))

    print(f"✅ Cleaned {len(output_lines)} lines and saved back to {filename}")

if __name__ == "__main__":
    extract_and_clean(file_name)