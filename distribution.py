import csv
import json
from collections import defaultdict, OrderedDict

def generate_distribution(values, bin_size):
    if not values:
        raise ValueError("The list of values is empty. Please provide a valid list.")

    min_val = min(values)
    max_val = max(values)

    bins = defaultdict(int)

    # Calculer les bins
    for value in values:
        bin_start = (int((value - min_val) // bin_size) * bin_size) + min_val
        bin_end = bin_start + bin_size
        bin_key = f"[{bin_start}, {bin_end}]"  # Intervalle comme clé
        bins[bin_key] += 1

    # Calculer le pourcentage
    total_values = len(values)
    percentage_distribution = {k: (v / total_values) * 100 for k, v in sorted(bins.items())}

    sorted_distribution = OrderedDict(
        sorted(percentage_distribution.items(), key=lambda x: x[1], reverse=True)
    )    
    return sorted_distribution



def overall_traffic_distribution(input_file, output_file, time_bin, size_bin):
    timestamps = []
    packet_sizes = []

    # Lire le fichier CSV
    with open(input_file, mode="r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            timestamps.append(float(row["Time"]) * 1000)  # Conversion en ms
            packet_sizes.append(int(row["Size"]))

    # Calculer les temps inter-paquets
    inter_packet_times = [
        timestamps[i + 1] - timestamps[i]
        for i in range(len(timestamps) - 1)
    ]

    # Générer les distributions
    inter_packet_distribution = generate_distribution(inter_packet_times, time_bin)
    size_distribution = generate_distribution(packet_sizes, size_bin)

    # Sauvegarder dans un fichier JSON
    results = {
        "inter_packet_times_distribution": inter_packet_distribution,
        "packet_size_distribution": size_distribution
    }

    with open(output_file, "w") as json_file:
        json.dump(results, json_file, indent=4)
    print(f"Distributions saved to {output_file}")


def sub_flow_distribution(input_file, output_file, flow_num, time_bin, size_bin):
    sub_flows = defaultdict(list)

    # Lire le fichier CSV et regrouper par sous-flux
    with open(input_file, mode="r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            label = row["Label"]
            timestamp = float(row["Time"]) * 1000  # Conversion en ms
            size = int(row["Size"])
            sub_flows[label].append((timestamp, size))

    if flow_num not in sub_flows:
        raise ValueError(f"Invalid flow number: {flow_num}. Available flows: {list(sub_flows.keys())}")

    flow = sub_flows[flow_num]

    if not flow or len(flow) < 2:
        raise ValueError(f"Flow {flow_num} must contain at least two packets to analyze inter-packet times.")

    # Extraire les timestamps et tailles
    timestamps = [packet[0] for packet in flow]
    packet_sizes = [packet[1] for packet in flow]

    # Calculer les temps inter-paquets
    inter_packet_times = [
        timestamps[i + 1] - timestamps[i]
        for i in range(len(timestamps) - 1)
    ]

    # Générer les distributions
    inter_packet_distribution = generate_distribution(inter_packet_times, time_bin)
    size_distribution = generate_distribution(packet_sizes, size_bin)

    # Sauvegarder dans un fichier JSON
    results = {
        "inter_packet_times_distribution": inter_packet_distribution,
        "packet_size_distribution": size_distribution
    }

    with open(output_file, "w") as json_file:
        json.dump(results, json_file, indent=4)
    print(f"Distributions for flow {flow_num} saved to {output_file}")
