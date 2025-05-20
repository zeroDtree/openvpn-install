#!/usr/bin/env fish
#!/usr/bin/fish
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

# 初始化 PKI 环境
# 初始化 PKI（如果未初始化）
if not test -d ./pki
    echo "初始化 PKI..."
    $EASYRSA init-pki
else
    echo "PKI 已初始化，跳过"
end

# 生成 CA（如果不存在 CA 证书）
if not test -f ./pki/ca.crt
    # 构建 CA，无密码，无交互
    echo "构建 CA..."
    $EASYRSA build-ca nopass
else
    echo "CA 已存在，跳过"
end

# =====================
# 生成服务器请求和签名
# =====================
if not test -f ./pki/private/$SERVER_NAME.key
    echo "生成服务器私钥请求..."
    $EASYRSA gen-req $SERVER_NAME nopass
else
    echo "服务器私钥已存在，跳过"
end

if not test -f ./pki/issued/$SERVER_NAME.crt
    echo "签发服务器证书..."
    $EASYRSA sign-req server $SERVER_NAME
else
    echo "服务器证书已签发，跳过"
end

# ================
# 生成 DH 参数
# ================
if not test -f ./pki/dh.pem
    echo "生成 Diffie-Hellman 参数..."
    $EASYRSA gen-dh
else
    echo "DH 参数已存在，跳过"
end

# =========================
# 生成客户端请求和签名
# =========================

if not test -f ./pki/private/$CLIENT_NAME.key
    echo "生成客户端私钥请求..."
    $EASYRSA gen-req $CLIENT_NAME nopass
else
    echo "客户端私钥已存在，跳过"
end

if not test -f ./pki/issued/$CLIENT_NAME.crt
    echo "签发客户端证书..."
    $EASYRSA sign-req client $CLIENT_NAME
else
    echo "客户端证书已签发，跳过"
end

# ================
# 生成 TLS 密钥
# ================
if not test -f ./pki/ta.key
    echo "生成 TLS 预共享密钥 ta.key..."
    openvpn --genkey secret ./pki/ta.key
else
    echo "TLS 密钥已存在，跳过"
end

# ===========================
# 生成客户端配置文件
# ===========================
echo "创建客户端配置文件..."
set -l OUTPUT_FILE $CONFIG_DIR/$CLIENT_NAME.ovpn

cat ctemplate.ovpn > $OUTPUT_FILE

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

echo "✅ 客户端配置文件生成完成: $OUTPUT_FILE"
