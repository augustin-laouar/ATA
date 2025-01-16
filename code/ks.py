from scipy.stats import ks_2samp
import csv
import argparse

def get_sizes(csv_filename):
    sizes = []
    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            size_str = row["Size"]     
            size_val = float(size_str) 
            sizes.append(size_val)

    return sizes

def get_inter_times(csv_filename):
    time_values = []
    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            time_str = row["Time"]     
            time_val = float(time_str) 
            time_values.append(time_val)
    
    inter_packet_times = [(time_values[i+1] - time_values[i]) * 1000 for i in range(len(time_values) - 1)] #in ms
    return inter_packet_times

def compare_with_ks(original_csv, generated_csv):
    original_sizes = get_sizes(original_csv)
    original_inter_times = get_inter_times(original_csv)
    generated_sizes = get_sizes(generated_csv)
    generated_inter_times = get_inter_times(generated_csv)
        

    ks_stat, p_value = ks_2samp(original_sizes, generated_sizes)
    print("Packet sizes :")
    print("KS statistic =", ks_stat)
    print("p-value =", p_value)
    ks_stat, p_value = ks_2samp(original_inter_times, generated_inter_times)
    print("Inter packet times :")
    print("KS statistic =", ks_stat)
    print("p-value =", p_value)

def main():
    parser = argparse.ArgumentParser(
        description=(
            "This script provide functions to perform Kolmogorov-Smirnov test."
        )
    )
    parser.add_argument(
        "--original-traffic", 
        type=str,
        required=True,
        help="Original traffic CSV file.")
    
    parser.add_argument(
        "--generated-traffic", 
        type=str,
        required=True,
        help="Generated traffic CSV file.")
    args = parser.parse_args()
    
    compare_with_ks(args.original_traffic, args.generated_traffic)

if __name__ == "__main__":
    main()