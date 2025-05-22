## The role of the files

- `batch-pki-gen.fish`: generate a batch of certificates and keys
- `ctemplate.ovpn`: client configuration template
- `pki-gen.fish`: generate certificates and keys

## openvpn installation (for archlinux)

Assume that the certificates and keys are generated on machine `a`, the client is installed on machine `b` and the openvpn server is installed on machine `c`.

The following uses easy-rsa to generate the certificates and keys required for openvpn.

### easy-rsa installation

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

### openvpn server installation

(on server `c`) download and install openvpn

```bash
yay -S openvpn
```

### certificate copy

Copy the generated certificates and keys to the server `c` from machine `a`

```bash
cd pki
scp ca.crt dh.pem issued/server.crt private/server.key ta.key {username}@{server_ip}:/etc/openvpn/server/
```

### openvpn server configuration file

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

### openvpn client installation and configuration file

(on machine `b`) similar to the server, download and install openvpn, copy the certificates and keys, and modify the configuration file as needed.

You can use `batch-pki-gen.fish` to batch generate client certificates and keys. Remember to modify the server ip and port in `ctemplate.ovpn`.
