import serial
import os
import time
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

# === Settings ===
SERIAL_PORT = "COM5"
BAUDRATE = 115200
READ_BYTES = 14
SAVE_BASE_DIR = "./data"  # Base directory

object_types = ['normal', 'sport']
current_breath_type = 'normal'
current_breath_cycle = 5

# === Ensure base directory exists ===
os.makedirs(SAVE_BASE_DIR, exist_ok=True)

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

def plot_adc(filename):
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
def collect_data(breath_type, breath_cycle):
    dir_path = os.path.join(SAVE_BASE_DIR, breath_type, str(breath_cycle))
    os.makedirs(dir_path, exist_ok=True)

    existing_files = [f for f in os.listdir(dir_path) if f.startswith("adc_") and f.endswith(".data")]
    file_number = len(existing_files) + 1

    filename = os.path.join(dir_path, f"adc_{breath_type}{str(breath_cycle)}_{file_number}.data")
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
            plot_adc(filename)
        except Exception as e:
            print(f"Cleaning or plotting failed: {e}")


def change_breath_cycle():
    global current_breath_cycle
    print("Current breathe cycle:", current_breath_cycle)
    new_cycle = input("Enter new breathe cycle (1-10): ")
    if new_cycle.isdigit() and 1 <= int(new_cycle) <= 10:
        current_breath_cycle = int(new_cycle)
        print(f"Breathe cycle changed to {current_breath_cycle}.")
    else:
        print("Invalid input. Breathe cycle remains unchanged.")


def change_breath_type():
    global current_breath_type
    print("Current breathe type:", current_breath_type)
    new_type = input("Enter new breathe type (normal/sport): ").strip().lower()
    if new_type in object_types:
        current_breath_type = new_type
        print(f"Breathe type changed to {current_breath_type}.")
    else:
        print("Invalid input. Breathe type remains unchanged.")

# === Program Entry ===
if __name__ == "__main__":
    while True:
        print("\n=== MAIN MENU ===")
        print(f"Current Breathe Type: {current_breath_type}", end="\t")
        print(f"Current Breathe Cycle: {current_breath_cycle}")
        print("1. Start Collecting Data")
        print("2. Change Breathe Cycle")
        print("3. Change Breathe Type")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            collect_data(current_breath_type, current_breath_cycle)
        elif choice == '2':
            change_breath_cycle()
        elif choice == '3':
            change_breath_type()
        elif choice == '4':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")