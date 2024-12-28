import threading
import time
import datetime
import json
import random

def generate_packet(timestamp, size, label, shared_list, lock):
    with lock:
        shared_list.append((timestamp, size, label))

def generate_normale(min, max, mean, stddev):
    while True:
        value = random.gauss(mean, stddev)
        if min <= value <= max:
            return value

def generate_distribution(distribution):
    intervals = [d for d in distribution]
    probabilities = [d["proba"] for d in distribution]
    selected_interval = random.choices(intervals, weights=probabilities, k=1)[0]

    min_val = selected_interval["min"]
    max_val = selected_interval["max"]
    sampled_value = random.uniform(min_val, max_val)

    return sampled_value



def distribution_generator(label, inter_packet_times, packet_sizes, shared_list, lock, start_time, end_time):
    now = time.time()
    while now < start_time:
        time.sleep(0.01)
        now = time.time()
    
    while now < end_time:
        next_packet_size = int(generate_distribution(packet_sizes))
        next_inter_time = generate_distribution(inter_packet_times) / 1000  #from ms to s
        
        if now + next_inter_time > end_time:
            print(f'Stop sub flow {label} at {now - start_time}')
            break
        time.sleep(next_inter_time)
        now = time.time()
        relative_time = now - start_time
        if now < end_time:
            generate_packet(relative_time, next_packet_size, label, shared_list, lock)
            print(f'time : {relative_time}, size : {next_packet_size}')


def normale_generator(label, inter_packet_times, packet_sizes, shared_list, lock, start_time, end_time):
    now = time.time()
    while now < start_time:
        time.sleep(0.01)
        now = time.time()
    
    while now < end_time:
        next_packet_size = int(generate_normale(
            packet_sizes["min"], packet_sizes["max"], packet_sizes["mean"], packet_sizes["stddev"]))
        next_inter_time = generate_normale(
            inter_packet_times["min"], inter_packet_times["max"], inter_packet_times["mean"], inter_packet_times["stddev"]) / 1000  #from ms to s
        if now + next_inter_time > end_time:
            print(f'Stop sub flow {label} at {now - start_time}')
            break
        time.sleep(next_inter_time)
        now = time.time()
        relative_time = now - start_time
        if now < end_time:
            generate_packet(relative_time, next_packet_size, label, shared_list, lock)
            #print(f'time : {relative_time}, size : {next_packet_size}')

def lauch(json_input, duration, csv_output):
    with open(json_input, 'r') as file:
        data = json.load(file)

    shared_list = [] 
    lock = threading.Lock()  

    if "sub-flows" in data:
        start_time = time.time() + 1
        end_time = start_time + duration
        threads = []

        for sub_flow in data["sub-flows"]:
            type = sub_flow.get("type")
            label = sub_flow.get("label")
            if type == "stats":
                inter_packet_times = sub_flow.get("inter-packet-times")
                packet_sizes = sub_flow.get("packet-sizes")
                generator_thread = threading.Thread(
                    target=normale_generator,
                    args=(label, inter_packet_times, packet_sizes, shared_list, lock, start_time, end_time)
                )
                threads.append(generator_thread)
                generator_thread.start()
            if type == "distribution":
                inter_packet_times = sub_flow.get("inter-packet-times")
                packet_sizes = sub_flow.get("packet-sizes")
                generator_thread = threading.Thread(
                    target=distribution_generator,
                    args=(label, inter_packet_times, packet_sizes, shared_list, lock, start_time, end_time)
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
    else:
        raise ValueError("Missing generators list in JSON configuration file.")
