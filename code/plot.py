import matplotlib.pyplot as plt
import sub_flows as sf
import csv

def plot_flow_throughput(input_file, flow_num):
    sub_flows = sf.create_sub_flows(input_file)

    if flow_num not in sub_flows:
        raise ValueError(f"Invalid flow number: {flow_num}. Available flows: {list(sub_flows.keys())}")

    flow = sub_flows[flow_num]

    if not flow or len(flow) < 2:
        raise ValueError(f"Flow {flow_num} must contain at least two packets to calculate throughput.")

    flow.sort(key=lambda x: x[0])

    timestamps = [packet[0] for packet in flow]
    sizes = [packet[1] for packet in flow]

    duration = timestamps[-1] - timestamps[0]
    if duration <= 0:
        raise ValueError(f"Invalid flow {flow_num}: duration must be greater than 0.")
    total_size = sum(sizes)

    average_throughput = (total_size * 8) / duration
    print(f"Average throughput for flow {flow_num}: {average_throughput:.2f} bits per second (bps)")

    throughputs = []
    times = []
    for i in range(len(flow) - 1):
        packet_size = sizes[i]
        time_interval = timestamps[i + 1] - timestamps[i]
        if time_interval > 0:
            throughputs.append((packet_size * 8) / time_interval)
            times.append(timestamps[i]) 

    plt.figure(figsize=(10, 6))
    plt.plot(times, throughputs, marker='o', linestyle='-', color='b')
    plt.title(f"Throughput for Flow {flow_num}")
    plt.xlabel("Time (s)")
    plt.ylabel("Throughput (Bits per Second)")
    plt.grid(True)
    plt.show()



def plot_overall_throughput(input_file):
    timestamps = []
    sizes = []
    with open(input_file, mode="r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            timestamps.append(float(row["Time"]))
            sizes.append(int(row["Size"]))

    if len(timestamps) < 2:
        raise ValueError("The file must contain at least two packets to calculate throughput.")

    duration = timestamps[-1] - timestamps[0]
    if duration <= 0:
        raise ValueError(f"Invalid flow {flow_num}: duration must be greater than 0.")
    total_size = sum(sizes)
    average_throughput = (total_size * 8) / duration
    print(f"Average throughput: {average_throughput:.2f} bits per second (bps)")

    throughputs = []
    times = []
    for i in range(len(timestamps) - 1):
        time_interval = timestamps[i + 1] - timestamps[i]
        if time_interval > 0:
            throughput = (sizes[i] * 8) / time_interval
            throughputs.append(throughput)
            times.append(timestamps[i])
    


    plt.figure(figsize=(12, 6))
    plt.plot(times, throughputs, marker='o', linestyle='-', color='b')
    plt.title("Overall Throughput Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Throughput (Bits per Second)")
    plt.grid(True)
    plt.show()





def plot_distribution(values, bin_size, title="Distribution", xlabel="Values", ylabel="Frequency (%)"):
    if not values:
        raise ValueError("The list of values is empty. Please provide a valid list.")
    
    min_val = min(values)
    max_val = max(values)
    num_bins = int((max_val - min_val) / bin_size) + 1

    plt.figure(figsize=(10, 6))
    plt.hist(values, bins=num_bins, edgecolor="black", color="blue", alpha=0.7, weights=[100 / len(values)] * len(values))
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()


def plot_overall_inter_packet_times(input_file, bin_size, title="Overall Inter-Packet Times Distribution", xlabel="Inter-Packet Time (ms)", ylabel="Frequency"):
    timestamps = []
    with open(input_file, mode="r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            timestamps.append(float(row["Time"]) * 1000)

    if len(timestamps) < 2:
        raise ValueError("The file must contain at least two packets to calculate inter-packet times.")

    inter_packet_times = [
        timestamps[i + 1] - timestamps[i]
        for i in range(len(timestamps) - 1)
    ]

    if not inter_packet_times:
        raise ValueError("No valid inter-packet times for the overall traffic.")

    plot_distribution(
        values=inter_packet_times,
        bin_size=bin_size,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel
    )


def plot_overall_packet_size(input_file, bin_size, title="Overall Packet Size Distribution", xlabel="Packet Size (Bytes)", ylabel="Frequency"):
    sizes = []
    with open(input_file, mode="r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            sizes.append(int(row["Size"]))

    if not sizes:
        raise ValueError("The file must contain at least one packet to analyze sizes.")

    plot_distribution(
        values=sizes,
        bin_size=bin_size,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel
    )


def plot_inter_packet_times(input_file, flow_num, bin_size, title="Inter-Packet Times Distribution", xlabel="Inter-Packet Time (ms)", ylabel="Frequency"):
    sub_flows = sf.create_sub_flows(input_file)

    if flow_num not in sub_flows:
        raise ValueError(f"Invalid flow number: {flow_num}. Available flows: {list(sub_flows.keys())}")

    flow = sub_flows[flow_num]

    if not flow or len(flow) < 2:
        raise ValueError(f"Flow {flow_num} must contain at least two packets to calculate inter-packet times.")

    flow.sort(key=lambda x: x[0])

    timestamps = [packet[0] *1000 for packet in flow]

    inter_packet_times = [
        timestamps[i + 1] - timestamps[i]
        for i in range(len(timestamps) - 1)
    ]

    if not inter_packet_times:
        raise ValueError(f"No valid inter-packet times for flow {flow_num}.")

    plot_distribution(
        values=inter_packet_times,
        bin_size=bin_size,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel
    )


def plot_packet_size(input_file, flow_num, bin_size, title="Packet Size Distribution", xlabel="Packet Size (Bytes)", ylabel="Frequency"):
    sub_flows = sf.create_sub_flows(input_file)

    if flow_num not in sub_flows:
        raise ValueError(f"Invalid flow number: {flow_num}. Available flows: {list(sub_flows.keys())}")

    flow = sub_flows[flow_num]

    if not flow:
        raise ValueError(f"Flow {flow_num} must contain at least one packet to analyze sizes.")

    packet_sizes = [packet[1] for packet in flow]

    plot_distribution(
        values=packet_sizes,
        bin_size=bin_size,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel
    )
