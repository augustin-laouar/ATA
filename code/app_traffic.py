import pyshark
import csv
import argparse

def extract_application_traffic(input_pcap, output_csv):
    capture = pyshark.FileCapture(input_pcap, display_filter="tcp")

    application_traffic = []
    current_packet_start_time = None
    current_packet_size = 0

    start_time = None
    for packet in capture:
        try:
            tcp_layer = packet.tcp
            current_packet_has_psh = int(tcp_layer.flags, 16) & 0x08 != 0
            data_len = int(packet.tcp.len)
            timestamp = float(packet.sniff_timestamp)
            if start_time is None:
                start_time = timestamp

            relative_time = timestamp - start_time

            if current_packet_start_time is None:
                current_packet_start_time = relative_time

            current_packet_size += data_len

            if current_packet_has_psh:
                application_traffic.append((current_packet_start_time, current_packet_size))
                current_packet_start_time = None
                current_packet_size = 0

        except AttributeError:
            continue

    with open(output_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Time","Size"])
        for time, size in application_traffic:
            writer.writerow([time, size])

    print(f"Saved in {output_csv}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "This script provide functions to extract applicative messages from a PCAP trace. "
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

    args = parser.parse_args()
    extract_application_traffic(args.input, args.output)


if __name__ == "__main__":
    main()