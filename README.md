# OpenVPN-PKI-Manager

- [OpenVPN-PKI-Manager](#openvpn-pki-manager)
  - [1. Brief introduction](#1-brief-introduction)
  - [2. Requirements](#2-requirements)
  - [3. Script Usage Examples](#3-script-usage-examples)
    - [3.1. Single Client Generation](#31-single-client-generation)
    - [3.2. Batch Client Generation](#32-batch-client-generation)
  - [4. Documents](#4-documents)

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

## 4. Documents

[OpenVPN installation](doc/openvpn-install.md)