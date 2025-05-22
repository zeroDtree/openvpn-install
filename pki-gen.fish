#!/usr/bin/env fish

printf "origin_paramters:\n$argv\n"
set -l ARGS $(getopt -o c: -l clientname: -- $argv)

if test $status -ne 0
    echo "Failed to parse arguments"
    exit 1
end

printf "after_getopt_parameters:\n$ARGS\n"

eval set -- argv $ARGS

echo $argv

set -g CLIENT_NAME client

while test (count $argv) -gt 0
    switch $argv[1]
        case -c --clientname
            set -g CLIENT_NAME $argv[2]
            set argv $argv[3..-1]
            echo "CLIENT_NAME=$CLIENT_NAME"
        case --
            set argv $argv[2..-1]
            break
        case '*'
            echo "Unknown option: $argv[1]"
            exit 1
    end
end

echo $argv

set -l SERVER_NAME server
set -l CONFIG_DIR (pwd)
set -l EASYRSA easyrsa
set -l EASYRSA_FLAG --sbatch
set -l EASYRSA $EASYRSA $EASYRSA_FLAG

# initialize PKI environment
# initialize PKI (if not initialized)
if not test -d ./pki
    echo "initializing PKI..."
    $EASYRSA init-pki
else
    echo "PKI already initialized, skipping"
end

# generate CA (if not exists CA certificate)
if not test -f ./pki/ca.crt
    # build CA, no password, no interaction
    echo "building CA..."
    $EASYRSA build-ca nopass
else
    echo "CA already exists, skipping"
end

# =====================
# generate server request and signature
# =====================
if not test -f ./pki/private/$SERVER_NAME.key
    echo "generating server private key request..."
    $EASYRSA gen-req $SERVER_NAME nopass
else
    echo "server private key already exists, skipping"
end

if not test -f ./pki/issued/$SERVER_NAME.crt
    echo "signing server certificate..."
    $EASYRSA sign-req server $SERVER_NAME
else
    echo "server certificate already signed, skipping"
end

# ================
# generate DH parameters
# ================
if not test -f ./pki/dh.pem
    echo "generating Diffie-Hellman parameters..."
    $EASYRSA gen-dh
else
    echo "DH parameters already exist, skipping"
end

# =========================
# generate client request and signature
# =========================

if not test -f ./pki/private/$CLIENT_NAME.key
    echo "generating client private key request..."
    $EASYRSA gen-req $CLIENT_NAME nopass
else
    echo "client private key already exists, skipping"
end

if not test -f ./pki/issued/$CLIENT_NAME.crt
    echo "signing client certificate..."
    $EASYRSA sign-req client $CLIENT_NAME
else
    echo "client certificate already signed, skipping"
end

# ================
# generate TLS key
# ================
if not test -f ./pki/ta.key
    echo "generating TLS pre-shared key ta.key..."
    openvpn --genkey secret ./pki/ta.key
else
    echo "TLS key already exists, skipping"
end

# ===========================
# generate client configuration file
# ===========================
echo "creating client configuration file..."
set -l OUTPUT_FILE $CONFIG_DIR/$CLIENT_NAME.ovpn

cat ctemplate.ovpn >$OUTPUT_FILE

echo "<ca>" >>$OUTPUT_FILE
cat $CONFIG_DIR/pki/ca.crt >>$OUTPUT_FILE
echo "</ca>" >>$OUTPUT_FILE

echo "<cert>" >>$OUTPUT_FILE
cat $CONFIG_DIR/pki/issued/$CLIENT_NAME.crt >>$OUTPUT_FILE
echo "</cert>" >>$OUTPUT_FILE

echo "<key>" >>$OUTPUT_FILE
cat $CONFIG_DIR/pki/private/$CLIENT_NAME.key >>$OUTPUT_FILE
echo "</key>" >>$OUTPUT_FILE

echo "<tls-auth>" >>$OUTPUT_FILE
cat $CONFIG_DIR/pki/ta.key >>$OUTPUT_FILE
echo "</tls-auth>" >>$OUTPUT_FILE

echo "✅ client configuration file generated: $OUTPUT_FILE"
