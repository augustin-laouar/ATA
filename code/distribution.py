import csv
import json
from collections import defaultdict
from typing import List
import argparse

def generate_distribution(values: List[float], interval: float) -> List[Dict[str, float]]:
    min_value = min(values)
    max_value = max(values)

    slots = []
    current_min = min_value // interval * interval
    while current_min <= max_value:
        slots.append(current_min)
        current_min += interval

    slot_ranges = {}
    for slot_min in slots:
        slot_max = slot_min + interval
        slot_ranges[(slot_min, slot_max)] = []

    for value in values:
        for slot_min, slot_max in slot_ranges.keys():
            if slot_min <= value < slot_max:
                slot_ranges[(slot_min, slot_max)].append(value)
                break

    total_values = len(values)
    distribution = []
    for (slot_min, slot_max), slot_values in slot_ranges.items():
        if slot_values:
            actual_min = min(slot_values)
            actual_max = max(slot_values)
            prob = len(slot_values) / total_values
            distribution.append({
                "min": actual_min,
                "max": actual_max,
                "proba": prob
            })
    distribution.sort(key=lambda x: x["proba"], reverse=True)

    return distribution

def sub_flow_distribution(input_file, output_file, flow_num, time_bin, size_bin):
    sub_flows = defaultdict(list)

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
    timestamps = [packet[0] for packet in flow]
    packet_sizes = [packet[1] for packet in flow]

    inter_packet_times = [
        timestamps[i + 1] - timestamps[i]
        for i in range(len(timestamps) - 1)
    ]

    inter_packet_distribution = generate_distribution(inter_packet_times, time_bin)
    size_distribution = generate_distribution(packet_sizes, size_bin)

    results = {
        "label": flow_num,
        "type": "distribution",
        "inter-packet-times": inter_packet_distribution,
        "packet-sizes": size_distribution
    }

    with open(output_file, "w") as json_file:
        json.dump({"sub-flow": results}, json_file, indent=4)

def sub_flows_distribution(input_file, output_file, time_bin, size_bin):
    sub_flows = defaultdict(list)

    with open(input_file, mode="r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            label = row["Label"]
            timestamp = float(row["Time"]) * 1000  # Conversion en ms
            size = int(row["Size"])
            sub_flows[label].append((timestamp, size))

    results = []

    for label, flow in sub_flows.items():
        if not flow or len(flow) < 2:
            raise ValueError(f"Flow {label} must contain at least two packets to analyze inter-packet times.")

        timestamps = [packet[0] for packet in flow]
        packet_sizes = [packet[1] for packet in flow]

        inter_packet_times = [
            timestamps[i + 1] - timestamps[i]
            for i in range(len(timestamps) - 1)
        ]

        inter_packet_distribution = generate_distribution(inter_packet_times, time_bin)
        size_distribution = generate_distribution(packet_sizes, size_bin)

        results.append({
            "label": label,
            "type": "distribution",
            "inter-packet-times": inter_packet_distribution,
            "packet-sizes": size_distribution
        })

    with open(output_file, "w") as json_file:
        json.dump({"sub-flows": results}, json_file, indent=4)
    print(f"Distributions for all sub-flows saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "This script extracts distributions (message size and inter message times) from applicative messages."
        )
    )
    parser.add_argument(
        "--input", 
        type=str, 
        required=True,
        help="Path to the input file (PCAP)."
    )
    parser.add_argument(
        "--output", 
        type=str, 
        required=True,
        help="Path to the output file."
    )
    parser.add_argument(
        "--sub-flow", 
        type=str, 
        help="Specify the sub-flow number to analyze.")
    parser.add_argument(
        "--time-interval", 
        type=float, 
        default=100, 
        help="Time interval for distributions.")
    parser.add_argument(
        "--size-interval", 
        type=int, 
        default=100, 
        help="Size interval for distributions.")
    
    args = parser.parse_args()

    if args.sub_flow:
        sub_flow_distribution(args.input, args.output, args.sub_flow, args.time_interval, args.size_interval)
    else:
        sub_flows_distribution(args.input, args.output, args.time_interval, args.size_interval)


if __name__ == "__main__":
    main()