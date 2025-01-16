import threading
import json
import random
import numpy as np
import argparse

def generate_packet(timestamp, size, label, shared_list, lock):
    with lock:
        shared_list.append((timestamp, size, label))

def generate_uniform(min, max):
    return np.random.uniform(min, max)

def generate_exponential(mean):
    return np.random.exponential(mean)

def generate_normale(mean, stddev):
    if stddev == 0:
        return mean
    
    return np.random.normal(mean, stddev)

def generate_log_normal(mean, stddev):
    if stddev == 0:
        return mean 

    mu = np.log(mean**2 / np.sqrt(mean**2 + stddev**2))
    sigma = np.sqrt(np.log(1 + (stddev**2 / mean**2)))

    return np.random.lognormal(mu, sigma)


def generate_gamma(mean, var):
    if mean < 0 or var < 0:
        raise ValueError("Mean and var should be positive with gamma.")

    if mean == 0:
        return 0.0
    if var == 0:
        return mean
    theta = var / mean
    k = mean / theta

    sample = np.random.gamma(k, theta)
    return sample

def generate_distribution(distribution):
    intervals = [d for d in distribution]
    probabilities = [d["proba"] for d in distribution]
    selected_interval = random.choices(intervals, weights=probabilities, k=1)[0]

    min_val = selected_interval["min"]
    max_val = selected_interval["max"]
    sampled_value = random.uniform(min_val, max_val)

    return sampled_value


def generator(label, ps_generator, ipt_generator, inter_packet_times, packet_sizes, shared_list, lock, end_time):
    now = 0.0
    
    while now < end_time:
        if(ps_generator == "dist"):
            next_packet_size = int(generate_distribution(packet_sizes))
        if(ps_generator == "uni"):
            next_packet_size = int(generate_uniform(packet_sizes["min"], packet_sizes["max"]))
        if(ps_generator == "exp"):
            next_packet_size = int(generate_exponential(packet_sizes["mean"]))
        if(ps_generator == "norm"):
            next_packet_size = int(generate_log_normal(packet_sizes["mean"], packet_sizes["stddev"]))
        if(ps_generator == "gamma"):
            next_packet_size = int(generate_gamma(packet_sizes["mean"], packet_sizes["variance"]))

        if(ipt_generator == "dist"):
            next_inter_time = generate_distribution(inter_packet_times) / 1000
        if(ipt_generator == "uni"):
            next_inter_time = generate_uniform(inter_packet_times["min"], inter_packet_times["max"]) / 1000
        if(ipt_generator == "exp"):
            next_inter_time = generate_exponential(inter_packet_times["mean"]) / 1000 
        if(ipt_generator == "norm"):
            next_inter_time = generate_log_normal(inter_packet_times["mean"], inter_packet_times["stddev"]) / 1000
        if(ipt_generator == "gamma"):
            next_inter_time = generate_gamma(inter_packet_times["mean"], inter_packet_times["variance"]) / 1000

        now += next_inter_time
        if now > end_time:
            break
        if now < end_time:
            generate_packet(now, next_packet_size, label, shared_list, lock)

def adjust_negative_times(shared_list):
    label_min_times = {}
    for i, packet in enumerate(shared_list):
        label = packet[2]
        packet_time = packet[0]

        if label not in label_min_times:
            label_min_times[label] = packet_time
        
        if label_min_times[label] < 0:
            shared_list[i] = (packet_time - label_min_times[label], packet[1], label)
    
    return shared_list

def lauch(json_input, duration, ps_generator, ipt_generator, csv_output):
    with open(json_input, 'r') as file:
        data = json.load(file)

    shared_list = [] 
    lock = threading.Lock()  

    if "sub-flows" in data:
        threads = []
        for sub_flow in data["sub-flows"]:
            label = sub_flow.get("label")
            inter_packet_times = sub_flow.get("inter-packet-times")
            packet_sizes = sub_flow.get("packet-sizes")
            generator_thread = threading.Thread(
                target=generator,
                args=(label, ps_generator, ipt_generator, inter_packet_times, packet_sizes, shared_list, lock, duration)
            )
            threads.append(generator_thread)
            generator_thread.start()
        for thread in threads:
            thread.join()

        shared_list.sort(key=lambda packet: packet[0])
        #adjust_negative_times(shared_list)
        #shared_list.sort(key=lambda packet: packet[0])

        with open(csv_output, mode='w', newline='', encoding='utf-8') as csv_file:
            csv_file.write("Time,Size,Label\n")
            for packet in shared_list:
                csv_file.write(f"{packet[0]},{packet[1]},{packet[2]}\n")
            print(f'Packets generated in {csv_output}.')
    else:
        raise ValueError("Missing generators list in JSON configuration file.")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "This script provide functions to generate a trace. "
        )
    )
    parser.add_argument(
        "--input", 
        type=str, 
        required=True,
        help="Path to the input file (JSON)."
    )
    parser.add_argument(
        "--output", 
        type=str, 
        required=True,
        help="Path to the output file."
    )
    parser.add_argument(
        "--ipt-generator", 
        type=str,
        default="uni",
        choices=["dist","uni","norm","exp","gamma"],
        help="Inter packet times generator mode."
    )
    
    parser.add_argument(
        "--ps-generator", 
        type=str, 
        default="uni",
        choices=["dist","uni","norm","exp","gamma"],
        help="Packet sizes generator mode."
    )
    

    parser.add_argument(
        "--duration", 
        type=float, 
        default=100,
        help="Sampling interval for comparison."
    )

    args = parser.parse_args()
    lauch(args.input, args.duration, args.ps_generator, args.ipt_generator, args.output)
    print(f"Traffic generated in {args.output}")


if __name__ == "__main__":
    main()
