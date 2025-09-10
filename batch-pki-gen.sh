#!/bin/env bash

# Usage: batch-pki-gen.sh [-n <num_clients>] [-s <server_ip>] [-p <port>] [-o <output_dir>]
#   -n, --num-clients: Number of clients to generate (default: 100)
#   -s, --server: Server IP address (optional)
#   -p, --port: Server port (optional, default: 1194)
#   -o, --output-dir: Output directory for client files (optional, default: current directory)

if [ $# -eq 0 ]; then
    echo "Usage: batch-pki-gen.sh [-n <num_clients>] [-s <server_ip>] [-p <port>] [-o <output_dir>]"
    echo "  -n, --num-clients: Number of clients to generate (default: 100)"
    echo "  -s, --server: Server IP address (optional)"
    echo "  -p, --port: Server port (optional, default: 1194)"
    echo "  -o, --output-dir: Output directory for client files (optional, default: current directory)"
    echo ""
    echo "Examples:"
    echo "  ./batch-pki-gen.sh -n 50 -s 192.168.1.100 -p 1194 -o ./clients"
    echo "  ./batch-pki-gen.sh --num-clients 10 --server 192.168.1.100 --output-dir /path/to/clients"
    echo "  ./batch-pki-gen.sh -n 100 -o ./output"
    exit 1
fi

echo "origin_paramters=<$@>"
ARGS=$(getopt --options="n:s:p:o:" --longoptions="num-clients:,server:,port:,output-dir:" -- "$@")

if [ $? -ne 0 ]; then
    echo "Failed to parse arguments"
    exit 1
fi

echo "after_getopt_parameters=<$ARGS>"
eval set -- "${ARGS}"

NUM_CLIENTS=100
SERVER_IP=""
SERVER_PORT="1194"
OUTPUT_DIR=""

while true; do
    case "$1" in
        -n|--num-clients)
            NUM_CLIENTS="$2"
            echo "NUM_CLIENTS=$NUM_CLIENTS"
            shift 2
            ;;
        -s|--server)
            SERVER_IP="$2"
            echo "SERVER_IP=$SERVER_IP"
            shift 2
            ;;
        -p|--port)
            SERVER_PORT="$2"
            echo "SERVER_PORT=$SERVER_PORT"
            shift 2
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            echo "OUTPUT_DIR=$OUTPUT_DIR"
            shift 2
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "positional parameters=<$@>"

echo "Generating $NUM_CLIENTS client certificates..."
if [ -n "$SERVER_IP" ]; then
    echo "Server: $SERVER_IP:$SERVER_PORT"
else
    echo "Using template configuration (no server IP specified)"
fi

# Create output directory (if specified)
if [ -n "$OUTPUT_DIR" ]; then
    echo "Output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create output directory '$OUTPUT_DIR'"
        exit 1
    fi
else
    echo "Output directory: current directory"
fi

for i in $(seq 1 $NUM_CLIENTS); do
    if [ -n "$SERVER_IP" ] && [ -n "$OUTPUT_DIR" ]; then
        echo "bash pki-gen.sh -c client$i -s $SERVER_IP -p $SERVER_PORT -o $OUTPUT_DIR"
        bash pki-gen.sh -c client$i -s $SERVER_IP -p $SERVER_PORT -o "$OUTPUT_DIR"
    elif [ -n "$SERVER_IP" ]; then
        echo "bash pki-gen.sh -c client$i -s $SERVER_IP -p $SERVER_PORT"
        bash pki-gen.sh -c client$i -s $SERVER_IP -p $SERVER_PORT
    elif [ -n "$OUTPUT_DIR" ]; then
        echo "bash pki-gen.sh -c client$i -o $OUTPUT_DIR"
        bash pki-gen.sh -c client$i -o "$OUTPUT_DIR"
    else
        echo "bash pki-gen.sh -c client$i"
        bash pki-gen.sh -c client$i
    fi
done

echo "✅ Batch generation completed! Generated $NUM_CLIENTS client certificates."
if [ -n "$OUTPUT_DIR" ]; then
    echo "📁 Files saved to: $OUTPUT_DIR"
else
    echo "📁 Files saved to: current directory"
fi

echo "$0 end========================================="
