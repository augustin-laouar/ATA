import threading
import json
import random
from scipy.stats import truncnorm
import numpy as np

def generate_packet(timestamp, size, label, shared_list, lock):
    with lock:
        shared_list.append((timestamp, size, label))

def generate_uniform(min, max):
    return np.random.uniform(min, max)

def generate_exponential(mean):
    return np.random.exponential(mean)

def generate_normale(min, max, mean, stddev):
    if stddev == 0:
        return mean
    
    a = (min - mean) / stddev
    b = (max - mean) / stddev
    
    value = truncnorm.rvs(a, b, loc=mean, scale=stddev)
    
    return value


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
            next_packet_size = int(generate_normale(packet_sizes["min"], packet_sizes["max"], packet_sizes["mean"], packet_sizes["stddev"]))

        if(ipt_generator == "dist"):
            next_inter_time = generate_distribution(inter_packet_times) / 1000
        if(ipt_generator == "uni"):
            next_inter_time = generate_uniform(inter_packet_times["min"], inter_packet_times["max"]) / 1000
        if(ipt_generator == "exp"):
            next_inter_time = generate_exponential(inter_packet_times["mean"]) / 1000 
        if(ipt_generator == "norm"):
            next_inter_time = generate_normale(inter_packet_times["min"], inter_packet_times["max"], inter_packet_times["mean"], inter_packet_times["stddev"]) / 1000

        now += next_inter_time
        if now > end_time:
            break
        if now < end_time:
            generate_packet(now, next_packet_size, label, shared_list, lock)

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

        with open(csv_output, mode='w', newline='', encoding='utf-8') as csv_file:
            csv_file.write("Time,Size,Label\n")
            for packet in shared_list:
                csv_file.write(f"{packet[0]},{packet[1]},{packet[2]}\n")
            print(f'Packets generated in {csv_output}.')
    else:
        raise ValueError("Missing generators list in JSON configuration file.")
