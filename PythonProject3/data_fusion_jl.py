import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
# Load the newly uploaded file using user's custom loader
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

# Apply moving average filter
def MA_filter(data, window_size):
    return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

# Normalize data to range [0, 1]
def normalize(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))

# Load and process data
# filename = "Project3/data/data/normal/3/adc_normal3_1.data"
filename = "Project3/data/data/sport/10/adc_sport10_5.data"
adc1, adc2 = load_adc_data(filename)
adc1_filtered = MA_filter(adc1, 250)
adc2_filtered = MA_filter(adc2, 500)

# Normalize
adc1_normalized = normalize(adc1_filtered)
adc2_normalized = normalize(adc2_filtered)

# Create time vectors for valid regions after filtering
x1 = np.arange(len(adc1_normalized))
x2 = np.arange(len(adc2_normalized))


# Assume adc2 is more trustworthy
peaks_belly1, props1 = find_peaks(adc1_normalized, prominence=0.1, distance=1000, plateau_size=1)
plateau_mids1 = [int((l + r) / 2) for l, r in zip(props1["left_edges"], props1["right_edges"])]
peaks_belly2, props2 = find_peaks(adc2_normalized, prominence=0.1, distance=1000, plateau_size=1)
plateau_mids2 = [int((l + r) / 2) for l, r in zip(props2["left_edges"], props2["right_edges"])]

# Plot the normalized data
plt.figure(figsize=(12, 6))
plt.plot(adc1_normalized, label='ADC1 Normalized', color='red')
plt.plot(plateau_mids1, adc1_normalized[plateau_mids1], 'go', label='Detected Breaths')
plt.plot(adc2_normalized, label='ADC2 Normalized', color='blue')
plt.plot(plateau_mids2, adc2_normalized[plateau_mids2], 'go', label='Detected Breaths')
plt.title("Stable Breathing Detection via ADC2 Peaks")
plt.xlabel("Sample Index")
plt.ylabel("Normalized Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

print("Detected breaths:", len(plateau_mids1))
print("Detected breaths:", len(plateau_mids2))

