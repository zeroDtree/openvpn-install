#!/bin/env bash

if [ $# -eq 0 ]; then
    echo "Usage: pki-gen.sh -c <client_name> [-s <server_ip>] [-p <port>] [-o <output_dir>]"
    echo "  -c, --clientname: Client name (required)"
    echo "  -s, --server: Server IP address (optional)"
    echo "  -p, --port: Server port (optional, default: 1194)"
    echo "  -o, --output-dir: Output directory for client file (optional, default: current directory)"
    echo ""
    echo "Examples:"
    echo "  ./pki-gen.sh -c client1 -s 192.168.1.100 -p 1194 -o ./clients"
    echo "  ./pki-gen.sh --clientname user1 --server 192.168.1.100 --output-dir /path/to/clients"
    exit 1
fi

echo "origin_paramters=<$@>"
ARGS=$(getopt --options="c:s:p:o:" --longoptions="clientname:,server:,port:,output-dir:" -- "$@")

if [ $? -ne 0 ]; then
    echo "Failed to parse arguments"
    exit 1
fi

echo "after_getopt_parameters=<$ARGS>"
eval set -- "${ARGS}"

CLIENT_NAME="client"
SERVER_IP=""
SERVER_PORT="1194"
OUTPUT_DIR=""

while true; do
    case "$1" in
        -c|--clientname)
            CLIENT_NAME="$2"
            echo "CLIENT_NAME=$CLIENT_NAME"
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

echo "$0 start======================================="

SERVER_NAME="server"
CONFIG_DIR=$(pwd)
EASYRSA="easyrsa"
EASYRSA_FLAG="--sbatch"
EASYRSA="$EASYRSA $EASYRSA_FLAG"

# initialize PKI environment
# initialize PKI (if not initialized)
if [ ! -d "./pki" ]; then
    echo "initializing PKI..."
    $EASYRSA init-pki
else
    echo "PKI already initialized, skipping"
fi

# generate CA (if not exists CA certificate)
if [ ! -f "./pki/ca.crt" ]; then
    # build CA, no password, no interaction
    echo "building CA..."
    $EASYRSA build-ca nopass
else
    echo "CA already exists, skipping"
fi

# =====================
# generate server request and signature
# =====================
if [ ! -f "./pki/private/$SERVER_NAME.key" ]; then
    echo "generating server private key request..."
    $EASYRSA gen-req $SERVER_NAME nopass
else
    echo "server private key already exists, skipping"
fi

if [ ! -f "./pki/issued/$SERVER_NAME.crt" ]; then
    echo "signing server certificate..."
    $EASYRSA sign-req server $SERVER_NAME
else
    echo "server certificate already signed, skipping"
fi

# ================
# generate DH parameters
# ================
if [ ! -f "./pki/dh.pem" ]; then
    echo "generating Diffie-Hellman parameters..."
    $EASYRSA gen-dh
else
    echo "DH parameters already exist, skipping"
fi

# =========================
# generate client request and signature
# =========================

if [ ! -f "./pki/private/$CLIENT_NAME.key" ]; then
    echo "generating client private key request..."
    $EASYRSA gen-req $CLIENT_NAME nopass
else
    echo "client private key already exists, skipping"
fi

if [ ! -f "./pki/issued/$CLIENT_NAME.crt" ]; then
    echo "signing client certificate..."
    $EASYRSA sign-req client $CLIENT_NAME
else
    echo "client certificate already signed, skipping"
fi

# ================
# generate TLS key
# ================
if [ ! -f "./pki/ta.key" ]; then
    echo "generating TLS pre-shared key ta.key..."
    openvpn --genkey secret ./pki/ta.key
else
    echo "TLS key already exists, skipping"
fi

# ===========================
# generate client configuration file
# ===========================
echo "creating client configuration file..."
OUTPUT_FILE="$CONFIG_DIR/$CLIENT_NAME.ovpn"

# Create client config from template with server IP and port replacement
if [ -n "$SERVER_IP" ]; then
    # Replace server IP and port in template
    sed "s/;remote my-server-2 1194/remote $SERVER_IP $SERVER_PORT/" ctemplate.ovpn > "$OUTPUT_FILE"
else
    # Use template as-is if no server IP specified
    cat ctemplate.ovpn > "$OUTPUT_FILE"
fi

echo "<ca>" >> "$OUTPUT_FILE"
cat "$CONFIG_DIR/pki/ca.crt" >> "$OUTPUT_FILE"
echo "</ca>" >> "$OUTPUT_FILE"

echo "<cert>" >> "$OUTPUT_FILE"
cat "$CONFIG_DIR/pki/issued/$CLIENT_NAME.crt" >> "$OUTPUT_FILE"
echo "</cert>" >> "$OUTPUT_FILE"

echo "<key>" >> "$OUTPUT_FILE"
cat "$CONFIG_DIR/pki/private/$CLIENT_NAME.key" >> "$OUTPUT_FILE"
echo "</key>" >> "$OUTPUT_FILE"

echo "<tls-auth>" >> "$OUTPUT_FILE"
cat "$CONFIG_DIR/pki/ta.key" >> "$OUTPUT_FILE"
echo "</tls-auth>" >> "$OUTPUT_FILE"

echo "✅ client configuration file generated: $OUTPUT_FILE"

# If output directory is specified, move generated files
if [ -n "$OUTPUT_DIR" ]; then
    echo "Creating output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create output directory '$OUTPUT_DIR'"
        exit 1
    fi
    
    # Move files to output directory
    if [ -f "$OUTPUT_FILE" ]; then
        mv "$OUTPUT_FILE" "$OUTPUT_DIR/"
        echo "📁 Moved $CLIENT_NAME.ovpn to $OUTPUT_DIR/"
    else
        echo "Warning: $OUTPUT_FILE not found"
    fi
fi

echo "$0 end========================================="
