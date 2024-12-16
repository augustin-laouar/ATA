from collections import Counter
from sklearn.cluster import DBSCAN
from sklearn.mixture import GaussianMixture
import numpy as np
import csv


def count_packet_sizes_from_csv(output_csv):
    size_counts = Counter()

    with open(output_csv, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            size = int(row["Size"])
            size_counts[size] += 1
    repeated_sizes = {size: count for size, count in size_counts.items() if count > 1}

    print(f"Packet sizes count : {len(size_counts)}")
    print("Packet size present more than once :")
    for size, count in repeated_sizes.items():
        print(f"Size : {size} Bytes, Occure : {count}")

def apply_dbscan_clustering(input_csv, output_csv, eps, min_samples):
    data = []
    with open(input_csv, mode="r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            size = int(row["Size"])
            data.append(size)

    #2D array
    data_array = np.array(data).reshape(-1, 1)

    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(data_array)

    #Write labels
    with open(input_csv, mode="r") as infile, open(output_csv, mode="w", newline="") as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["Label"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        for row, label in zip(reader, labels):
            row["Label"] = label
            writer.writerow(row)

    unique_labels = set(labels)
    print("Clusters :")
    for label in unique_labels:
        if label == -1:
            print(f"Cluster {label} : Noise")
        else:
            print(f"Cluster {label}")


def apply_gmm_clustering(input_csv, output_csv, max_components, min_cluster_size):
    data = []
    with open(input_csv, mode="r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            size = int(row["Size"])
            data.append(size)

    data_array = np.array(data).reshape(-1, 1)

    best_gmm = None
    best_bic = float("inf")
    best_n_components = 1

    for n_components in range(1, max_components + 1):
        gmm = GaussianMixture(n_components=n_components, random_state=42)
        gmm.fit(data_array)
        bic = gmm.bic(data_array)
        if bic < best_bic:
            best_bic = bic
            best_gmm = gmm
            best_n_components = n_components

    print(f"Optimal number of clusters : {best_n_components}")

    labels = best_gmm.predict(data_array)

    cluster_counts = Counter(labels)

    # identify small clusters
    small_clusters = [cluster for cluster, count in cluster_counts.items() if count < min_cluster_size]

    # merge small clusters
    for i, label in enumerate(labels):
        if label in small_clusters:
            distances = np.linalg.norm(data_array[i] - best_gmm.means_, axis=1)
            nearest_cluster = np.argmin(distances)
            while nearest_cluster in small_clusters:
                distances[nearest_cluster] = float("inf")
                nearest_cluster = np.argmin(distances)
            labels[i] = nearest_cluster

    cluster_counts = Counter(labels)

    print("Clusters  :")
    for cluster, count in cluster_counts.items():
        print(f"Cluster {cluster}: {count} elements")

    with open(input_csv, mode="r") as infile, open(output_csv, mode="w", newline="") as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["Label"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        for row, label in zip(reader, labels):
            row["Label"] = label
            writer.writerow(row)