import serial
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# === Settings ===
SERIAL_PORT = "COM5"
BAUDRATE = 115200
READ_BYTES = 14
WINDOW_SIZE = 1200
COLLECTION_TIME = 30  # seconds

# === Cleaning Function ===
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
    
def load_adc_data(filename):
    adc1 = []
    adc2 = []
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    val1 = int(parts[0])
                    val2 = int(parts[1])
                    adc1.append(val1)
                    adc2.append(val2)
                except ValueError:
                    continue  # skip malformed lines
    return adc1, adc2

def plot_adc_before_processing(filename):
    # Read and convert to integers
    adc1, adc2 = load_adc_data(filename)
    # print(f"ADC values: {adc_values}")
    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(adc1, marker='o', linestyle='-', markersize=0.5, linewidth=0.1, color='blue')
    plt.plot(adc2, marker='x', linestyle='-', markersize=0.5, linewidth=0.1, color='red')
    # plt.plot(x_values, voltage_value, marker='x', linestyle='-', markersize=2, color='red')
    plt.title("ADC Data Plot")
    plt.xlabel("Sample Number")
    plt.ylabel("ADC Value")
    plt.legend(['ADC1', 'ADC2'])
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
# === Main collection function ===
def collect_data():
    global COLLECTION_TIME
    filename = "eval.data"
    print(f"Saving ADC data to {filename}")

    ser = serial.Serial(port=SERIAL_PORT, baudrate=BAUDRATE, bytesize=8, parity="N", stopbits=1, timeout=0.01)
    count = 0
    start_time = time.time()

    try:
        with open(filename, "wb") as file_1:
            while True:
                data = ser.read(READ_BYTES)
                if data:
                    file_1.write(data)
                    print(f"{count}: Received {data}")
                    count += 1

    except KeyboardInterrupt:
        end_time = time.time()
        elapsed_time = end_time - start_time
        COLLECTION_TIME = elapsed_time
        print("\nUser stopped the data collection.")
        print(f"Data collection time: {elapsed_time:.5f} seconds")
        print(f"Total data points collected: {count}")

    finally:
        # This always runs no matter how the try block ends
        if ser.is_open:
            ser.close()
            print("Serial connection closed.")

        # Cleaning and plotting
        try:
            extract_and_clean(filename)
            plot_adc_before_processing(filename)
        except Exception as e:
            print(f"Cleaning or plotting failed: {e}")

def MA_filter(data, window_size):
    """Apply a moving average filter to the data."""
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

def find_match_from_adc1(plateau_mids1, cur_adc2_peak, acceptable_dist):
    for i in range(len(plateau_mids1)):
        # print("plateau_mids1[i] - cur_adc2_peak: ", plateau_mids1[i] - cur_adc2_peak)
        if abs(plateau_mids1[i] - cur_adc2_peak) < acceptable_dist: 
            return plateau_mids1[i]
    return None

def insert_abnormal(data, gap):
    if not data:
        return []
    result = [data[0]]
    for prev, curr in zip(data, data[1:]):
        if abs(curr - prev) > gap:
            result.append("abnormal")
        result.append(curr)
    return result

def eval_data():
    global WINDOW_SIZE
    filename = "eval.data"
    if not os.path.exists(filename):
        print(f"File {filename} does not exist. Please collect data first.")
        return
    adc1, adc2 = load_adc_data(filename)
    adc1_filtered = MA_filter(adc1, WINDOW_SIZE)
    adc2_filtered = MA_filter(adc2, WINDOW_SIZE)
    adc1_normalized = (adc1_filtered - np.mean(adc1_filtered)) / np.std(adc1_filtered)
    adc2_normalized = (adc2_filtered - np.mean(adc2_filtered)) / np.std(adc2_filtered)
    # reflect adc2_normalized in the y-axis
    adc2_normalized = -adc2_normalized
    _, props1 = find_peaks(adc1_normalized, prominence=0.1, distance=1000, plateau_size=1)
    plateau_mids1 = [int((l + r) / 2) for l, r in zip(props1["left_edges"], props1["right_edges"])]
    _, props2 = find_peaks(adc2_normalized, prominence=0.1, distance=1000, plateau_size=1)
    plateau_mids2 = [int((l + r) / 2) for l, r in zip(props2["left_edges"], props2["right_edges"])]
    sorted_distances_peak_2 = sorted(np.diff(plateau_mids2))
    median_distance_peak_2 = np.median(sorted_distances_peak_2)
    percentile_25_peak_2 = np.percentile(sorted_distances_peak_2, 25)
    percentile_75_peak_2 = np.percentile(sorted_distances_peak_2, 75)
    iqr_peak_2 = percentile_75_peak_2 - percentile_25_peak_2
    # iqr_acceptable = iqr_peak_2*2.5
    iqr_acceptable = median_distance_peak_2/2
    acceptable_distance = median_distance_peak_2 + iqr_acceptable
    final_peak_index = insert_abnormal(plateau_mids2, acceptable_distance)
    for i in range(len(final_peak_index)):
        if final_peak_index[i] == "abnormal":
            try:
                front = final_peak_index[i-1]
                back = final_peak_index[i+1]
                middle = (front + back)/2
                adc1_match = find_match_from_adc1(plateau_mids1, middle, iqr_acceptable)
                if adc1_match is not None:
                    print("Found match:", adc1_match)
                    final_peak_index[i] = adc1_match 
                else:
                    print("No match found")
                    final_peak_index[i] = int(middle)
            except IndexError:
                final_peak_index[i] = final_peak_index[i-1] + median_distance_peak_2
    plt.figure(figsize=(12, 6))
    plt.plot(adc1_normalized, label='ADC1 Normalized', color='red')
    plt.plot(final_peak_index, adc2_normalized[final_peak_index], 'go', label='Detected Breaths')
    plt.plot(adc2_normalized, label='ADC2 Normalized', color='blue')
    plt.legend()
    plt.title("Final Peak Index")
    plt.show()
    breath_cycle = len(final_peak_index) + 1 if WINDOW_SIZE == 1200 else len(final_peak_index) + 2
    print("Total breaths detected:", breath_cycle, "cycles")
    print("Breath rate: ", breath_cycle / (COLLECTION_TIME / 60), "breaths/minute")
    

def change_eval_settings():
    print("Change evaluation settings here.")
    global WINDOW_SIZE
    while True:
        print("\n=== EVALUATION SETTINGS ===")
        print(f"Current window size: {WINDOW_SIZE}")
        print("1. Change to 5 cycle settings")
        print("2. Change to 30s settings")
        print("3. Back to main menu")

        choice = input("Enter your choice: ")

        if choice == '1':
            WINDOW_SIZE = 1200
        elif choice == '2':
            while True:
                new_window_size = input("Enter new window size (in samples): ")
                if new_window_size.isdigit():
                    WINDOW_SIZE = int(new_window_size)
                    print(f"Window size changed to {WINDOW_SIZE}")
                    break
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")
    
# === Program Entry ===
if __name__ == "__main__":
    while True:
        print("\n=== MAIN MENU ===")
        print("1. Start Collecting Data")
        print("2. Start Evaluation Data")
        print("3. Change Evaluation Settings")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            collect_data()
        elif choice == '2':
            eval_data()
        elif choice == '3':
            change_eval_settings()
        elif choice == '4':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")