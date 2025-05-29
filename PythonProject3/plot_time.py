import matplotlib.pyplot as plt

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

def plot_time(filename):
    # Read and convert to integers
    adc1, adc2 = load_adc_data(filename)
    # print(f"ADC values: {adc_values}")
    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(adc1, marker='o', linestyle='-', markersize=2)
    plt.plot(adc2, marker='x', linestyle='-', markersize=2, color='red')
    # plt.plot(x_values, voltage_value, marker='x', linestyle='-', markersize=2, color='red')
    plt.title("ADC Data Plot")
    plt.xlabel("Sample Number")
    plt.ylabel("ADC Value")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    
if __name__ == "__main__":
    file_name = "adc_test.data"
    plot_time(file_name)