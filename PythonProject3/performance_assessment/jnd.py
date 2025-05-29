import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# One-sided delta: only positive differences from ground truth
delta = np.array([0, 1, 2, 3, 4, 5, 6])

# Simulated user response: P(user detects difference) at each delta
# These are realistic ascending probabilities
responses_high = np.array([0.2, 0.4, 0.6, 0.75, 0.9, 0.97, 1.0])
responses_med =  np.array([0.1, 0.3, 0.5, 0.65, 0.8, 0.9, 0.95])
responses_low =  np.array([0.05, 0.2, 0.35, 0.5, 0.65, 0.8, 0.9])

# Sigmoid function for fitting
def sigmoid(x, L ,x0, k, b):
    return L / (1 + np.exp(-k*(x - x0))) + b

# Fit sigmoid for each response set
popt_high, _ = curve_fit(sigmoid, delta, responses_high, p0=[1, 2, 1, 0])
popt_med, _ = curve_fit(sigmoid, delta, responses_med, p0=[1, 2, 1, 0])
popt_low, _ = curve_fit(sigmoid, delta, responses_low, p0=[1, 2, 1, 0])

# Generate smooth x values and corresponding sigmoid curves
x_fit = np.linspace(0, 6.5, 300)
y_high = sigmoid(x_fit, *popt_high)
y_med = sigmoid(x_fit, *popt_med)
y_low = sigmoid(x_fit, *popt_low)

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(delta, responses_high, 'o', label='High Gain (Easy)', color='green')
plt.plot(x_fit, y_high, '-', color='green')

plt.plot(delta, responses_med, 'o', label='Medium Gain', color='orange')
plt.plot(x_fit, y_med, '-', color='orange')

plt.plot(delta, responses_low, 'o', label='Low Gain (Hard)', color='red')
plt.plot(x_fit, y_low, '-', color='red')

# JND threshold line
plt.axhline(0.5, color='gray', linestyle='--', label="JND Threshold (50%)")

# Vertical lines at JND (x0 from sigmoid fit)
plt.axvline(popt_high[1], color='green', linestyle='--', label=f'JND High ≈ {popt_high[1]:.2f} bpm')
plt.axvline(popt_med[1], color='orange', linestyle='--', label=f'JND Med ≈ {popt_med[1]:.2f} bpm')
plt.axvline(popt_low[1], color='red', linestyle='--', label=f'JND Low ≈ {popt_low[1]:.2f} bpm')

plt.title("JND Psychometric Curve Using One-Sided Δ (0 to 6 bpm)")
plt.xlabel("Δ from True Breath Rate (bpm)")
plt.ylabel("P(User Detects Difference)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
