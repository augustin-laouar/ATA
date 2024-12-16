import clustering
import app_traffic
import stats
import argparse
import plot

def create_parser():

    parser = argparse.ArgumentParser(
        description=(
            "This script automates the analysis of application traffic. "
            "Its main functions include extracting application-level traffic from a Layer 4 (TCP) pcap capture, "
            "using clustering algorithms to generate sub-flows from the main application flow, "
            "and generating statistics and visualizations (graphs) for the flow or its sub-flows."
        )
    )

    # Modes
    parser.add_argument("-a", "--app-traffic", action="store_true", 
                        help="Extract application traffic from a pcap capture (Layer 4 - TCP).")
    parser.add_argument("-c", "--clustering", action="store_true", 
                        help="Apply a clustering algorithm to generate sub-flows from application traffic.")
    parser.add_argument("-s", "--stats", action="store_true", 
                        help="Generate statistics based on labelled data (output from the clustering step).")
    parser.add_argument("-pt", "--plot-throughput", action="store_true", 
                        help="Plot the overall throughput or the throughput for a specific sub-flow (use with --sub-flow).")
    parser.add_argument("-pit", "--plot-inter-times", action="store_true", 
                        help="Plot the distribution of inter-packet times. Use --sub-flow to specify a sub-flow.")
    parser.add_argument("-ps", "--plot-packet-sizes", action="store_true", 
                        help="Plot the distribution of packet sizes. Use --sub-flow to specify a sub-flow.")

    # Input
    parser.add_argument("-in", "--input", type=str, 
                        help="Input capture file in pcap or pcapng format.")

    # Optional arguments
    parser.add_argument("-so", "--stats-output", type=str, default="./stats/output.json", 
                        help="Path to the output JSON file for statistics (default: ./stats/output.json).")
    parser.add_argument("--input-app-traffic", type=str, 
                        help="Input CSV file containing extracted application packets.")
    parser.add_argument("--input-labelled-data", type=str, 
                        help="Input CSV file containing labelled application packets.")
    parser.add_argument("--output-app-traffic", type=str, default="./data/app_traffic.csv", 
                        help="Path to save the output CSV file with extracted application packets (default: ./data/app_traffic.csv).")
    parser.add_argument("--output-labelled-data", type=str, default="./labelled-data/labelled.csv", 
                        help="Path to save the output CSV file with labelled application packets (default: ./labelled-data/labelled.csv).")
    parser.add_argument("--clustering-algorithm", type=str, default="gmm", 
                        help="Clustering algorithm to use. Options: 'gmm' (default) or 'dbscan'.")

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

    # Plot arguments
    parser.add_argument("--sub-flow", type=str, 
                        help="Specify the sub-flow number to analyze for throughput, inter-packet times, or packet sizes.")
    parser.add_argument("--bin-size", type=float, 
                        help="Bin size for the distribution plots (e.g., inter-packet times or packet sizes).")


    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    app_traffic_file = args.output_app_traffic
    labelled_data_file = args.output_labelled_data
    stats_file = args.stats_output

    if args.app_traffic:
        if args.input: #we have pcapng input
            data_file = args.input
        else:
            parser.error("Please specify an input file.")
        app_traffic.extract_application_traffic(data_file, app_traffic_file)
    
    if args.clustering:
        if args.input_app_traffic:
            app_traffic_file = args.input_app_traffic
        if args.clustering_algorithm == "gmm":
            max_components = args.gmm_max_components
            min_cluster_size = args.gmm_min_cluster_size
            clustering.apply_gmm_clustering(app_traffic_file, labelled_data_file, max_components, min_cluster_size)
        if args.clustering_algorithm == "dbscan":
            eps = args.dbscan_eps
            min_samples = args.dbscan_min_samples
            clustering.apply_dbscan_clustering(app_traffic_file, labelled_data_file, eps, min_samples)
    
    if args.stats:
        if args.input_labelled_data:
            labelled_data_file = args.input_labelled_data
        if args.sub_flow:
            flow_num =args.sub_flow
            stats.process_sub_flow(labelled_data_file, stats_file, flow_num)
        else:
            stats.process_sub_flows(labelled_data_file, stats_file)


    if args.plot_throughput:
        if args.input_labelled_data:
            labelled_data_file = args.input_labelled_data
        if args.sub_flow:
            flow_num =args.sub_flow
            plot.plot_flow_throughput(labelled_data_file, flow_num)
        else:
            plot.plot_overall_throughput(labelled_data_file)

    if args.plot_inter_times:
        if args.input_labelled_data:
            labelled_data_file = args.input_labelled_data
        bin_size = 1
        if args.bin_size:
            bin_size = args.bin_size
        if args.sub_flow:
            flow_num =args.sub_flow
            plot.plot_inter_packet_times(labelled_data_file, flow_num, bin_size)
        else:
            plot.plot_overall_inter_packet_times(labelled_data_file, bin_size)

    if args.plot_packet_sizes:
        if args.input_labelled_data:
            labelled_data_file = args.input_labelled_data
        bin_size = 100
        if args.bin_size:
            bin_size = args.bin_size
        if args.sub_flow:
            flow_num =args.sub_flow
            plot.plot_packet_size(labelled_data_file, flow_num, bin_size)
        else:
            plot.plot_overall_packet_size(labelled_data_file, bin_size)
if __name__ == "__main__":
    main()
