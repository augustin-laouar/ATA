import csv
from collections import defaultdict
import matplotlib.pyplot as plt
from scipy.signal import correlate
import numpy as np
import argparse

def get_traffic(csv_file_path):
    traffic = []
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            time = float(row['Time'])
            size = int(row['Size'])

            traffic.append((time, size))
    traffic = sorted(traffic, key=lambda x: x[0])
    return traffic

def get_sub_flows_traffic(csv_file_path):
    sub_flows_dict = defaultdict(list)

    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            time = float(row['Time'])
            size = int(row['Size'])
            label = row['Label']

            sub_flows_dict[label].append((time, size))

    sub_flows = []
    for label in sorted(sub_flows_dict.keys(), key=lambda x: int(x)):
        sub_flows.append(sub_flows_dict[label])

    return sub_flows

def bits_per_second(data, sampling_interval):
    if not data:
        return np.array([]), np.array([])

    data = sorted(data, key=lambda x: x[0])
    
    start_time = data[0][0]
    data = [(t - start_time, size) for t, size in data]
    
    duration = data[-1][0]
    time_points = np.arange(0, duration + sampling_interval, sampling_interval)
    
    signal = np.zeros(len(time_points) - 1, dtype=float)

    times = [row[0] for row in data]
    sizes = [row[1] for row in data]
    
    indices = np.searchsorted(time_points, times, side='right') - 1
    for idx, size in zip(indices, sizes):
        if 0 <= idx < len(signal):
            signal[idx] += size * 8 

    return time_points[:-1], signal



def compare(original_file, generated_file, sampling_interval, output_path):
    original_traffic = get_traffic(original_file)
    generated_traffic = get_traffic(generated_file)
    time_original, bits_original = bits_per_second(original_traffic, sampling_interval)
    time_generated, bits_generated = bits_per_second(generated_traffic, sampling_interval)

    # to bits / s
    bps_original = bits_original / sampling_interval
    bps_generated = bits_generated / sampling_interval

    # Max duration
    min_time = min(time_original[-1], time_generated[-1])

    plt.figure(figsize=(8, 5))
    plt.plot(time_original, bps_original, label='Original', color='orange')
    plt.plot(time_generated, bps_generated, label='Generated', color='blue')

    plt.xlim(0, min_time)

    plt.title("Original (orange) vs Generated (blue)")
    plt.xlabel("Time (s)")
    plt.ylabel("Throughput (bits/s)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)
    plt.close()


def compare_signals_autocorr(original_file, generated_file, sampling_interval, output_path, max_lag=None):
    original_traffic = get_traffic(original_file)
    generated_traffic = get_traffic(generated_file)

    _, bits_original = bits_per_second(original_traffic, sampling_interval)
    _, bits_generated = bits_per_second(generated_traffic, sampling_interval)

    original_signal = (bits_original - np.mean(bits_original)) / np.std(bits_original)
    generated_signal = (bits_generated - np.mean(bits_generated)) / np.std(bits_generated)

    if max_lag is None:
        max_lag = min(len(original_signal), len(generated_signal)) // 2

    autocorr_original = correlate(original_signal, original_signal, mode='full')
    autocorr_generated = correlate(generated_signal, generated_signal, mode='full')

    center_o = len(original_signal) - 1
    center_g = len(generated_signal) - 1
    
    autocorr_original = autocorr_original[center_o - max_lag : center_o + max_lag + 1]
    autocorr_generated = autocorr_generated[center_g - max_lag : center_g + max_lag + 1]

    autocorr_original /= np.max(np.abs(autocorr_original))
    autocorr_generated /= np.max(np.abs(autocorr_generated))

    mse = np.mean((autocorr_original - autocorr_generated)**2)

    lags = np.arange(-max_lag, max_lag + 1)

    plt.figure(figsize=(10, 5))
    plt.plot(lags, autocorr_generated, label="Generated", color='blue')
    plt.plot(lags, autocorr_original, label="Original", color='orange', alpha=0.7)

    plt.title(f"Autocorrelation Comparison\n(MSE = {mse:.4f})")
    plt.xlabel("Lag")
    plt.ylabel("Autocorrelation")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)
    plt.close()



def get_stats(file_path, sampling_interval):
    traffic = get_traffic(file_path)
    _, signal = bits_per_second(traffic, sampling_interval)
    stats = {}
    stats["min"] = float(np.min(signal))
    stats["max"] = float(np.max(signal))
    stats["mean"] = float(np.mean(signal))
    stats["stddev"] = float(np.std(signal, ddof=1))   
    stats["variance"] = float(np.var(signal, ddof=1))

    if stats["mean"] != 0:
        stats["coef_of_variation"] = stats["stddev"] / stats["mean"]
    else:
        stats["coef_of_variation"] = 0.0
    
    return stats

def print_stats(stats):
    print(f'Min: {stats["min"]}')
    print(f'Max: {stats["max"]}')
    print(f'Mean: {stats["mean"]}')
    print(f'StdDev: {stats["stddev"]}')
    print(f'Variance: {stats["variance"]}')
    print(f'CoefVar: {stats["coef_of_variation"]}')

def main():
    parser = argparse.ArgumentParser(
        description=(
            "This script provide functions to evaluate throughput. "
        )
    )
    parser.add_argument(
        "--original", 
        type=str, 
        required=True,
        help="Original trafic file (csv)."
    )
    parser.add_argument(
        "--generated", 
        type=str, 
        required=True,
        help="Generated trafic file (csv)."
    )
    parser.add_argument(
        "--interval", type=float, default=1,
        help="Sampling interval for comparison."
    )
    parser.add_argument(
        "--output-dir", 
        type=str,
        required=True,
        help="Output directory."
    )
    args = parser.parse_args()

    compare(args.original, args.generated, args.interval, f'{args.output_dir}/throughput.png')

    compare_signals_autocorr(args.original, args.generated, args.interval, f'{args.output_dir}/throughput_autocorr.png')

    original_stats = get_stats(args.original, args.interval)
    generated_stats = get_stats(args.generated, args.interval)
    print('Original stats :')
    print_stats(original_stats)
    print('Generated stats :')
    print_stats(generated_stats)



if __name__ == "__main__":
    main()
