# TRC3500_GroupC3_Project3
Project 3 : Estimating Breath Rate 

Breath Rate Estimation System
A dual-sensor system leveraging pressure and conductive rubber strain sensors for accurate breath rate estimation using STM32 microcontroller and Python data processing.

👥 Team (Group C3)
Chai Jun Lun (33454930)

Louis Aristio (33361126)

Nandhana Alif Kusumabrata (33404526)

Vincent Law Yun Kae (32840152)

William Melvern Yang (33291128)

🛠 Project Overview
This project implements a wearable breath monitoring solution using two complementary sensors:

MPS20N0040D-D Pressure Sensor

Adafruit 519 Conductive Rubber Cord Strain Sensor

Both sensors detect respiratory activity through pressure variation and torso expansion. The STM32 microcontroller captures and processes signals in real-time, and Python scripts handle feature extraction and breath cycle estimation.

Key Features:
Analog signal conditioning with op-amp circuits

Real-time sampling and UART data transfer

Digital signal processing: smoothing, thresholding, and compression

Dual-sensor data fusion for enhanced detection reliability

Accurate breath rate estimation under varied physical conditions

🔧 Circuit Design
Pressure Sensor Circuit: Differential amplifier with gain ≈ 1000 using R1 = R2 = 1kΩ and Rf = Rg = 1MΩ

Rubber Sensor Circuit: Voltage divider with signal shifting and amplification to map output to STM32’s ADC range (0.5–3V)

🔄 STM32 Signal Processing
Multiplexed ADC Channels (Channels 8 & 9)

Sampling rate: 650 Hz

Baud rate: 115200

Data compression: Binary thresholding (LOW/HIGH)

Noise filtering: Hysteresis thresholds with software Schmitt trigger

🧮 Python Post-Processing
Moving average filter (N = 300) applied to rubber sensor data

Peak detection using scipy.signal.find_peaks

Z-score normalization and signal phase alignment

Fusion logic compensates for missed peaks via redundancy

📊 Performance Metrics
MSE and Just-Noticeable Difference (JND) analyses under:

Normal breathing

Light exercise

Heavy exercise

Fusion-based breath detection showed up to 70× accuracy improvement compared to raw sensor data.

🔬 Tools & Equipment
STM32 microcontroller

MPS20N0040D-D pressure sensor

Adafruit 519 conductive rubber cord sensor

Python (NumPy, SciPy, Matplotlib)

UART serial interface

📎 References
Week 3: Signal Conditioning and Transformation

Project 3 – Breath Rate Estimation Report

