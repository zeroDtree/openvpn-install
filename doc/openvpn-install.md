- [1. OpenVPN installation (for archlinux)](#1-openvpn-installation-for-archlinux)
	- [1.1. easy-rsa installation](#11-easy-rsa-installation)
	- [1.2. openvpn server installation](#12-openvpn-server-installation)
	- [1.3. certificate copy](#13-certificate-copy)
	- [1.4. openvpn server configuration file](#14-openvpn-server-configuration-file)
	- [1.5. openvpn client installation and configuration file](#15-openvpn-client-installation-and-configuration-file)

## 1. OpenVPN installation (for archlinux)

Assume that the certificates and keys are generated on machine `a`, the client is installed on machine `b` and the openvpn server is installed on machine `c`.

The following uses `easy-rsa` to generate the certificates and keys required for openvpn.

### 1.1. easy-rsa installation

(on machine `a`) download and install easy-rsa

```bash
yay -S easy-rsa
```

Generate and sign the certificates

```bash
easyrsa init-pki
easyrsa build-ca
easyrsa gen-req server nopass
easyrsa sign-req server server
easyrsa gen-req client nopass
easyrsa sign-req client client
easyrsa gen-dh
cd pki
openvpn --genkey secret ta.key
```

The directory structure of the certificates and keys that need to be paid attention to and generated is as follows:

```
pki:
ca.crt  dh.pem  issued  reqs  ta.key  private

pki/issued:
client.crt  server.crt

pki/private:
ca.key  client.key  server.key

pki/reqs:
client.req  server.req
```

### 1.2. openvpn server installation

(on server `c`) download and install openvpn

```bash
yay -S openvpn
```

### 1.3. certificate copy

Copy the generated certificates and keys to the server `c` from machine `a`

```bash
cd pki
scp ca.crt dh.pem issued/server.crt private/server.key ta.key {username}@{server_ip}:/etc/openvpn/server/
```

### 1.4. openvpn server configuration file

(on server `c`)

After installing openvpn, there will be a sample configuration file. The location of the sample configuration file may be different on different computers, but you should be able to find it.

```bash
cp /usr/share/doc/openvpn/examples/sample-config-files/server.conf /etc/openvpn/
```

Modify the configuration file as needed.

Start openvpn

```bash
systemctl enable openvpn@server
systemctl start openvpn@server
```

### 1.5. openvpn client installation and configuration file

(on machine `b`)

You can use `batch-pki-gen.sh` to batch generate client certificates and keys. The script now supports parameterized configuration, so you don't need to manually modify the template file.
