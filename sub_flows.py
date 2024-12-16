import csv
from collections import defaultdict

def create_sub_flows(input_csv):
    label_dict = defaultdict(list)
    with open(input_csv, mode="r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            label = row["Label"]
            timestamp = float(row["Time"])
            size = int(row["Size"])
            label_dict[label].append((timestamp, size))
    return label_dict
