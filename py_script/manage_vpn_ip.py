#!/usr/bin/env python3
import os
import sys
import ipaddress
import argparse
from omegaconf import OmegaConf

# ======================
# Config loading
# ======================
def load_config(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    return OmegaConf.load(path)

# ======================
# Helper functions
# ======================
def ensure_ccd_dir(ccd_dir):
    os.makedirs(ccd_dir, exist_ok=True)

def parse_used_ips(ccd_dir, reserved_ips):
    used_ips = set()
    if not os.path.isdir(ccd_dir):
        return used_ips
    for filename in os.listdir(ccd_dir):
        filepath = os.path.join(ccd_dir, filename)
        if not os.path.isfile(filepath):
            continue
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ifconfig-push"):
                    parts = line.split()
                    if len(parts) >= 2:
                        used_ips.add(ipaddress.ip_address(parts[1]))
    used_ips.update(reserved_ips)
    return used_ips

def find_next_available_ip(start_ip, end_ip, used_ips):
    current = start_ip
    while current <= end_ip:
        if current not in used_ips:
            return current
        current += 1
    raise RuntimeError("No available IP addresses in client pool")

def validate_ip(ip_addr, vpn_network):
    if ip_addr not in vpn_network:
        raise ValueError(f"IP {ip_addr} is outside VPN network {vpn_network}")

def write_ccd(ccd_dir, client_name, ip_addr, netmask):
    filepath = os.path.join(ccd_dir, client_name)
    with open(filepath, "w") as f:
        f.write(f"ifconfig-push {ip_addr} {netmask}\n")

# ======================
# CCD Operations
# ======================
def create_client_ccd(cfg, client_name, fixed_ip=None):
    vpn_network = ipaddress.ip_network(cfg.vpn.network)
    netmask = cfg.vpn.netmask
    ccd_dir = cfg.paths.ccd_dir
    reserved_ips = {ipaddress.ip_address(ip) for ip in cfg.get("reserved_ips", {}).values()}
    client_ip_start = ipaddress.ip_address(cfg.client_pool.start)
    client_ip_end = ipaddress.ip_address(cfg.client_pool.end)

    ensure_ccd_dir(ccd_dir)
    used_ips = parse_used_ips(ccd_dir, reserved_ips)

    if fixed_ip:
        ip_addr = ipaddress.ip_address(fixed_ip)
        validate_ip(ip_addr, vpn_network)
        if ip_addr in used_ips:
            raise RuntimeError(f"IP {ip_addr} is already in use")
    else:
        ip_addr = find_next_available_ip(client_ip_start, client_ip_end, used_ips)

    write_ccd(ccd_dir, client_name, ip_addr, netmask)
    print(f"CCD created: {client_name} -> {ip_addr}")

def list_ccd(cfg):
    ccd_dir = cfg.paths.ccd_dir
    if not os.path.isdir(ccd_dir):
        print("CCD directory does not exist.")
        return
    print(f"{'Client Name':20} {'IP Address':15}")
    print("-" * 36)
    for filename in sorted(os.listdir(ccd_dir)):
        filepath = os.path.join(ccd_dir, filename)
        ip_addr = "-"
        if os.path.isfile(filepath):
            with open(filepath, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("ifconfig-push"):
                        parts = line.split()
                        if len(parts) >= 2:
                            ip_addr = parts[1]
        print(f"{filename:20} {ip_addr:15}")

def delete_ccd(cfg, client_name):
    ccd_dir = cfg.paths.ccd_dir
    filepath = os.path.join(ccd_dir, client_name)
    if os.path.isfile(filepath):
        os.remove(filepath)
        print(f"CCD deleted: {client_name}")
    else:
        print(f"No CCD found for client: {client_name}")

def check_ccd(cfg):
    ccd_dir = cfg.paths.ccd_dir
    if not os.path.isdir(ccd_dir):
        print("CCD directory does not exist.")
        return
    used_ips = {}
    for filename in sorted(os.listdir(ccd_dir)):
        filepath = os.path.join(ccd_dir, filename)
        if not os.path.isfile(filepath):
            continue
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ifconfig-push"):
                    parts = line.split()
                    if len(parts) >= 2:
                        ip = parts[1]
                        if ip in used_ips:
                            print(f"Conflict: IP {ip} used by {used_ips[ip]} and {filename}")
                        else:
                            used_ips[ip] = filename
    print("Check completed.")

# ======================
# CLI
# ======================
def main():
    parser = argparse.ArgumentParser(description="OpenVPN CCD manager with subcommands")
    parser.add_argument(
        "-c", "--config", default="config/ccd_config.yaml", help="Path to configuration file"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    parser_create = subparsers.add_parser("create", help="Create CCD for a client")
    parser_create.add_argument("client_name", help="OpenVPN client common name")
    parser_create.add_argument("fixed_ip", nargs="?", help="Optional fixed IP address")

    # list
    subparsers.add_parser("list", help="List all CCD and IPs")

    # delete
    parser_delete = subparsers.add_parser("delete", help="Delete CCD for a client")
    parser_delete.add_argument("client_name", help="Client name to delete CCD")

    # check
    subparsers.add_parser("check", help="Check CCD for IP conflicts")

    args = parser.parse_args()
    cfg = load_config(args.config)

    if args.command == "create":
        create_client_ccd(cfg, args.client_name, args.fixed_ip)
    elif args.command == "list":
        list_ccd(cfg)
    elif args.command == "delete":
        delete_ccd(cfg, args.client_name)
    elif args.command == "check":
        check_ccd(cfg)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
