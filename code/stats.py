import json
import numpy as np
import sub_flows as sf


def calculate_statistics(values):
    if len(values) == 0:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "mean_of_squares": None,
            "stddev": None,
            "variance": None,
            "coef_of_variation": None,
        }
    
    mean = float(np.mean(values))
    mean_of_squares = float(np.mean(np.square(values)))
    variance = float(np.var(values))
    stddev = float(np.std(values))
    coef_of_variation = float(stddev / mean) if mean != 0 else None

    return {
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "mean": mean,
        "mean_of_squares": mean_of_squares,
        "stddev": stddev,
        "variance": variance,
        "coef_of_variation": coef_of_variation,
    }

def compute_packet_statistics(packet_list):
    if len(packet_list) < 2:
        raise ValueError("Minimum 2 packets to compute statistics")

    timestamps = [packet[0] for packet in packet_list]
    sizes = [packet[1] for packet in packet_list]

    inter_packet_times = [(timestamps[i+1] - timestamps[i]) * 1000 for i in range(len(timestamps) - 1)] #in ms 

    inter_packet_stats = calculate_statistics(inter_packet_times)
    size_stats = calculate_statistics(sizes)

    return {
        "inter_packet_times": inter_packet_stats,
        "packet_sizes": size_stats,
    }


def process_sub_flow(input_file, output_file, flow_num):
    sub_flows = sf.create_sub_flows(input_file)
    
    if flow_num not in sub_flows:
        raise ValueError(f"Invalid flow number: {flow_num}. Available flows: {list(sub_flows.keys())}")
    
    sub_flow = sub_flows[flow_num]
    statistics = compute_packet_statistics(sub_flow)
    
    results = {
        "sub-flows": [
            {
                "label": flow_num,
                "type": "stats",
                "packet-sizes": statistics["packet_sizes"],
                "inter-packet-times": statistics["inter_packet_times"]
            }
        ]
    }
    
    with open(output_file, mode="w") as json_file:
        json.dump(results, json_file, indent=4)
    
    print(f"Statistics for flow {flow_num} saved in {output_file}")


def process_sub_flows(input_file, output_file):
    sub_flows = sf.create_sub_flows(input_file)
    
    results = {"sub-flows": []}
    for label, sub_flow in sub_flows.items():
        statistics = compute_packet_statistics(sub_flow)
        results["sub-flows"].append({
            "label": label,
            "type": "stats",
            "packet-sizes": statistics["packet_sizes"],
            "inter-packet-times": statistics["inter_packet_times"]
        })
    
    with open(output_file, mode="w") as json_file:
        json.dump(results, json_file, indent=4)
    
    print(f"Statistics saved in {output_file}")
