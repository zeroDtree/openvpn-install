# OpenVPN-PKI-Manager

- [OpenVPN-PKI-Manager](#openvpn-pki-manager)
  - [1. Brief introduction](#1-brief-introduction)
  - [2. Requirements](#2-requirements)
  - [3. Script Usage Examples](#3-script-usage-examples)
    - [3.1. Single Client Generation](#31-single-client-generation)
    - [3.2. Batch Client Generation](#32-batch-client-generation)
  - [4. Python Script Usage Examples](#4-python-script-usage-examples)
    - [4.1. CCD Management (`manage_vpn_ip.py`)](#41-ccd-management-manage_vpn_ippy)
    - [4.2. Batch CCD Creation (`batch_create_ccd.py`)](#42-batch-ccd-creation-batch_create_ccdpy)
  - [5. Documents](#5-documents)

## 1. Brief introduction

**OpenVPN-PKI-Manager** is an automated certificate management and client configuration generation tool for OpenVPN.

## 2. Requirements

Make sure you have installed the following software on your system:

- `easy-rsa`
- `openvpn`

## 3. Script Usage Examples

### 3.1. Single Client Generation

```bash
# Generate a client certificate and save to specific directory
./pki-gen.sh -c client1 -s 192.168.1.100 -p 1194 -o ./clients

# or use long form parameters
./pki-gen.sh --clientname user1 --server 192.168.1.100 --port 1194 --output-dir /path/to/clients
```

### 3.2. Batch Client Generation

```bash
# Generate clients and save to specific directory
./batch-pki-gen.sh -n 50 -s 192.168.1.100 -p 1194 -o ./clients

# or use long form parameters
./batch-pki-gen.sh --num-clients 25 --server 192.168.1.100 --port 1194 --output-dir /path/to/clients
```

## 4. Python Script Usage Examples

### 4.1. CCD Management (`manage_vpn_ip.py`)

The `manage_vpn_ip.py` script manages OpenVPN Client Config Directories (CCD) for assigning static IP addresses to clients.

**Prerequisites:**

- Python 3
- `omegaconf` package: `pip install omegaconf`
- Configuration file: `config/ccd_config.yaml`

**Available Commands:**

```bash
# Create CCD for a client (auto-assign IP from pool)
python3 py_script/manage_vpn_ip.py create client1

# Create CCD with a fixed IP address
python3 py_script/manage_vpn_ip.py create client1 10.10.0.100

# List all CCD files and their assigned IPs
python3 py_script/manage_vpn_ip.py list

# Delete CCD for a client
python3 py_script/manage_vpn_ip.py delete client1

# Check for IP conflicts in CCD files
python3 py_script/manage_vpn_ip.py check

# Use custom config file
python3 py_script/manage_vpn_ip.py -c /path/to/config.yaml create client1
```

### 4.2. Batch CCD Creation (`batch_create_ccd.py`)

The `batch_create_ccd.py` script creates CCD files for multiple clients in batch.

```bash
# Create CCD files for clients 31-250 (default range)
python3 py_script/batch_create_ccd.py

# Create CCD files for a custom range
python3 py_script/batch_create_ccd.py --start 50 --end 100

# Use custom config file
python3 py_script/batch_create_ccd.py -c /path/to/config.yaml --start 31 --end 250
```

## 5. Documents

[OpenVPN installation](doc/openvpn-install.md)
