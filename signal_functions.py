import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate

def bits_per_second(file_path, sampling_interval):
    flux = pd.read_csv(file_path)
    
    if 'Time' not in flux.columns or 'Size' not in flux.columns:
        raise ValueError("CSV file should contain Time and Size columns.")
    
    flux["Time"] -= flux["Time"].iloc[0]
    duration = flux["Time"].iloc[-1]

    time_points = np.arange(0, duration + sampling_interval, sampling_interval)
    signal = np.zeros(len(time_points) - 1) 

    indices = np.searchsorted(time_points, flux["Time"], side='right') - 1
    for idx, size in zip(indices, flux["Size"]):
        if 0 <= idx < len(signal):
            signal[idx] += size

    return time_points[:-1], signal

def packets_per_second(file_path, sampling_interval):
    flux = pd.read_csv(file_path)
    
    if 'Time' not in flux.columns:
        raise ValueError("CSV file should contain a 'Time' column.")
    
    flux["Time"] -= flux["Time"].iloc[0]
    duration = flux["Time"].iloc[-1]

    time_points = np.arange(0, duration + sampling_interval, sampling_interval)
    signal = np.zeros(len(time_points) - 1) 

    indices = np.searchsorted(time_points, flux["Time"], side='right') - 1
    for idx in indices:
        if 0 <= idx < len(signal):
            signal[idx] += 1  

    return time_points[:-1], signal


def correlate_signals(signal1, signal2):
    min_length = min(len(signal1), len(signal2))
    signal1 = signal1[:min_length]
    signal2 = signal2[:min_length]
    correlation = correlate(signal1, signal2, mode='full')
    lags = np.arange(-len(signal1) + 1, len(signal2))

    return lags, correlation

def plot_signals(time_points_list, signals_list, labels=None, xlabel="Time (s)", ylabel="Throughput (packets/s)", title=""):
    if len(time_points_list) != len(signals_list):
        raise ValueError("The length of time_points_list and signals_list must be the same.")

    plt.figure(figsize=(10, 5))

    for time_points, signal, label in zip(time_points_list, signals_list, labels or [None] * len(signals_list)):
        plt.plot(time_points, signal, label=label)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    if labels:
        plt.legend()
    plt.show()

def compare_signals(signal1, signal2):
    signal1_norm = (signal1 - np.mean(signal1)) / np.std(signal1)
    signal2_norm = (signal2 - np.mean(signal2)) / np.std(signal2)

    correlation = correlate(signal1_norm, signal2_norm, mode='full')
    lags = np.arange(-len(signal1) + 1, len(signal2))

    max_corr_index = np.argmax(correlation)
    max_corr_value = correlation[max_corr_index]
    best_lag = lags[max_corr_index]

    throughput1 = np.sum(signal1) / len(signal1) 
    throughput2 = np.sum(signal2) / len(signal2)  

    throughput_diff_percent = abs(throughput1 - throughput2) / ((throughput1 + throughput2) / 2) * 100

    similarity_score = max_corr_value / len(signal1)
    return {
        "similarity_score": float(similarity_score),
        "best_lag": int(best_lag),
        "throughput_signal1": float(throughput1),
        "throughput_signal2": float(throughput2),
        "throughput_difference_percent": float(throughput_diff_percent)
    }



file_path = "./output/generated_180s.csv"
file_path2 = "./output/app_traffic_180s.csv"
sampling_interval = 1

time_points1, signal1 = packets_per_second(file_path, sampling_interval)
time_points2, signal2 = packets_per_second(file_path2, sampling_interval)

plot_signals([time_points1, time_points2], [signal1, signal2], ["Generated", "Original"])
res = compare_signals(signal1, signal2)
print(res)