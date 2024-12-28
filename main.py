import clustering
import app_traffic
import stats
import argparse
import plot
import distribution
import generator
def create_parser():
    parser = argparse.ArgumentParser(
        description=(
            "This script automates the analysis of application traffic. "
            "It supports traffic extraction, clustering, statistics generation, distribution analysis, and plotting."
        )
    )

    # Mode principal
    parser.add_argument(
        "-m","--mode", type=str, required=True,
        choices=["app-traffic", "clustering", "stats", "distributions", "generate", "plot"],
        help="Select the operation mode: app-traffic, clustering, stats, distributions, generate, or plot."
    )

    # Input and output
    parser.add_argument(
        "--input", type=str, required=True,
        help="Path to the main input file (e.g., pcap, CSV, or JSON)."
    )
    parser.add_argument(
        "--output", type=str,
        help="Directory where all output files will be saved (default: ./output)."
    )

    # Optional: Specific arguments for modes
    parser.add_argument("--clustering-algorithm", type=str, default="gmm",
                        help="Clustering algorithm to use. Options: 'gmm' (default) or 'dbscan'.")
    parser.add_argument("--sub-flow", type=str, help="Specify the sub-flow number to analyze.")
    parser.add_argument("--time-interval", type=float, default=100, help="Time interval for distributions.")
    parser.add_argument("--size-interval", type=int, default=100, help="Size interval for distributions.")
    parser.add_argument("--bin-size", type=float, help="Bin size for distribution plots.")
    parser.add_argument("--duration", type=int, default=10, help="Packet generation duration (in seconds).")

    # GMM-specific arguments
    parser.add_argument("--gmm-max-components", type=int, default=10, 
                        help="Maximum number of components for the GMM clustering algorithm (default: 10).")
    parser.add_argument("--gmm-min-cluster-size", type=int, default=2, 
                        help="Minimum cluster size for the GMM clustering algorithm (default: 2).")

    # DBSCAN-specific arguments
    parser.add_argument("--dbscan-eps", type=int, default=100, 
                        help="The epsilon parameter for the DBSCAN clustering algorithm (default: 100).")
    parser.add_argument("--dbscan-min-samples", type=int, default=5, 
                        help="The minimum samples parameter for the DBSCAN clustering algorithm (default: 5).")

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    app_traffic_file = "app_traffic.csv"
    labelled_data_file = "labelled_app_traffic.csv"
    stats_file = "stats.json"
    dist_file = "distributions.json"
    generated_csv_file = "generated_app_traffic.csv"

    if args.mode == "app-traffic":
        if args.output:
            app_traffic_file = args.output
        app_traffic.extract_application_traffic(args.input, app_traffic_file)

    elif args.mode == "clustering":
        if args.output:
            labelled_data_file = args.output
        if args.input:
            app_traffic_file = args.input
        if args.clustering_algorithm == "gmm":
            clustering.apply_gmm_clustering(
                app_traffic_file, labelled_data_file, args.gmm_max_components, args.gmm_min_cluster_size)
        elif args.clustering_algorithm == "dbscan":
            clustering.apply_dbscan_clustering(
                app_traffic_file, labelled_data_file, args.dbscan_eps, args.dbscan_min_samples)

    elif args.mode == "generate":
        if args.output:
            generated_csv_file = args.output
        generator.lauch(args.input, args.duration, generated_csv_file)

    elif args.mode == "stats":
        if args.output:
            stats_file = args.output
        if args.input:
            labelled_data_file = args.input
        if args.sub_flow:
            stats.process_sub_flow(labelled_data_file, stats_file, args.sub_flow)
        else:
            stats.process_sub_flows(labelled_data_file, stats_file)

    elif args.mode == "distributions":
        if args.output:
            dist_file = args.output
        if args.input:
            labelled_data_file = args.input
        if args.sub_flow:
            distribution.sub_flow_distribution(
                labelled_data_file, args.sub_flow, dist_file, args.time_interval, args.size_interval)
        else:
            distribution.sub_flows_distribution(
                labelled_data_file, dist_file, args.time_interval, args.size_interval)

    elif args.mode.startswith("plot"):
        if args.input:
            labelled_data_file = args.input
        if args.mode == "plot-throughput":
            plot.plot_overall_throughput(labelled_data_file)
        elif args.mode == "plot-inter-times":
            plot.plot_overall_inter_packet_times(labelled_data_file, args.bin_size)
        elif args.mode == "plot-packet-sizes":
            plot.plot_overall_packet_size(labelled_data_file, args.bin_size)

    else:
        raise ValueError(f"Unknown mode: {args.mode}")


if __name__ == "__main__":
    main()
