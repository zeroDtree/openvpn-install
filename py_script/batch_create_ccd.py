#!/usr/bin/env python3
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manage_vpn_ip import create_client_ccd, load_config


def main():
    parser = argparse.ArgumentParser(description="Batch generate OpenVPN CCD files")
    parser.add_argument("-c", "--config", default="config/ccd_config.yaml", help="Path to configuration file")
    parser.add_argument("--start", type=int, default=31, help="Starting client number (default: 31)")
    parser.add_argument("--end", type=int, default=254, help="Ending client number (default: 254)")

    args = parser.parse_args()

    if not os.path.isfile(args.config):
        print(f"Config file {args.config} not found")
        sys.exit(1)

    cfg = load_config(args.config)

    for i in range(args.start, args.end + 1):
        client_name = f"client{i}"
        try:
            create_client_ccd(cfg, client_name)
        except Exception as e:
            print(f"Failed to create {client_name}: {e}")


if __name__ == "__main__":
    main()
