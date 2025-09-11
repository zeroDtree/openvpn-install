# OpenVPN-PKI-Manager

- [OpenVPN-PKI-Manager](#openvpn-pki-manager)
  - [1. The role of the files](#1-the-role-of-the-files)
    - [1.1. Core Scripts:](#11-core-scripts)
    - [1.2. Web Management System:](#12-web-management-system)
    - [1.3. Templates:](#13-templates)
  - [2. OpenVPN installation (for archlinux)](#2-openvpn-installation-for-archlinux)
    - [2.1. easy-rsa installation](#21-easy-rsa-installation)
    - [2.2. openvpn server installation](#22-openvpn-server-installation)
    - [2.3. certificate copy](#23-certificate-copy)
    - [2.4. openvpn server configuration file](#24-openvpn-server-configuration-file)
    - [2.5. openvpn client installation and configuration file](#25-openvpn-client-installation-and-configuration-file)
  - [3. Script Usage](#3-script-usage)
    - [3.1. Single Client Generation](#31-single-client-generation)
    - [3.2. Batch Client Generation](#32-batch-client-generation)
    - [3.3. Parameters](#33-parameters)
  - [4. Web Management Interface](#4-web-management-interface)
    - [4.1. Overview](#41-overview)
    - [4.2. Installation and Setup](#42-installation-and-setup)
    - [4.3. Features](#43-features)
      - [4.3.1. For Users:](#431-for-users)
      - [4.3.2. For Administrators:](#432-for-administrators)
    - [4.4. Administrator Operations](#44-administrator-operations)
      - [4.4.1. Initialize database](#441-initialize-database)
      - [4.4.2. User Management:](#442-user-management)
      - [4.4.3. Generate Random Users:](#443-generate-random-users)
      - [4.4.4. File Assignment:](#444-file-assignment)
      - [4.4.5. For Users:](#445-for-users)
    - [4.5. Database](#45-database)
      - [4.5.1. Database Schema:](#451-database-schema)

## 1. The role of the files

### 1.1. Core Scripts:

- `batch-pki-gen.sh`: generate a batch of certificates and keys
- `ctemplate.ovpn`: client configuration template
- `pki-gen.sh`: generate certificates and keys

### 1.2. Web Management System:

- `app.py`: Flask web server for client file distribution
- `db_init.py`: database initialization and management
- `manage_users.py`: user management script
- `assign_files.py`: file assignment script
- `generate_random_users.py`: random user generator
- `config.py`: configuration settings
- `start_server.sh`: web server startup script

### 1.3. Templates:

- `templates/`: HTML templates for web interface
  - `base.html`: base template
  - `index.html`: homepage
  - `login.html`: login page
  - `dashboard.html`: user dashboard

## 2. OpenVPN installation (for archlinux)

Assume that the certificates and keys are generated on machine `a`, the client is installed on machine `b` and the openvpn server is installed on machine `c`.

The following uses easy-rsa to generate the certificates and keys required for openvpn.

### 2.1. easy-rsa installation

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

### 2.2. openvpn server installation

(on server `c`) download and install openvpn

```bash
yay -S openvpn
```

### 2.3. certificate copy

Copy the generated certificates and keys to the server `c` from machine `a`

```bash
cd pki
scp ca.crt dh.pem issued/server.crt private/server.key ta.key {username}@{server_ip}:/etc/openvpn/server/
```

### 2.4. openvpn server configuration file

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

### 2.5. openvpn client installation and configuration file

(on machine `b`)

You can use `batch-pki-gen.sh` to batch generate client certificates and keys. The script now supports parameterized configuration, so you don't need to manually modify the template file.

## 3. Script Usage

### 3.1. Single Client Generation

```bash
# Generate a single client certificate with default settings
./pki-gen.sh -c client1

# Generate a client certificate with specific server IP and port
./pki-gen.sh -c client1 -s 192.168.1.100 -p 1194

# Generate a client certificate and save to specific directory
./pki-gen.sh -c client1 -s 192.168.1.100 -p 1194 -o ./clients

# Generate with long form parameters
./pki-gen.sh --clientname user1 --server 192.168.1.100 --port 1194 --output-dir /path/to/clients
```

### 3.2. Batch Client Generation

```bash
# Generate 100 clients with default settings (using template as-is)
./batch-pki-gen.sh -n 100

# Generate 50 clients with specific server IP and port
./batch-pki-gen.sh -n 50 -s 192.168.1.100 -p 1194

# Generate 10 clients with server IP only (using default port 1194)
./batch-pki-gen.sh --num-clients 10 --server 192.168.1.100

# Generate 20 clients with long form parameters
./batch-pki-gen.sh --num-clients 20 --server 192.168.1.100 --port 1194

# Generate clients and save to specific directory
./batch-pki-gen.sh -n 50 -s 192.168.1.100 -p 1194 -o ./clients

# Generate with all parameters including output directory
./batch-pki-gen.sh --num-clients 25 --server 192.168.1.100 --port 1194 --output-dir /path/to/clients
```

### 3.3. Parameters

**pki-gen.sh parameters:**

- `-c, --clientname`: Client name (required)
- `-s, --server`: Server IP address (optional)
- `-p, --port`: Server port (optional, default: 1194)
- `-o, --output-dir`: Output directory for client file (optional, default: current directory)

**batch-pki-gen.sh parameters:**

- `-n, --num-clients`: Number of clients to generate (default: 100)
- `-s, --server`: Server IP address (optional)
- `-p, --port`: Server port (optional, default: 1194)
- `-o, --output-dir`: Output directory for client files (optional, default: current directory)

If no server IP is specified, the generated client configuration files will use the template as-is, and you can manually modify the server settings later.

## 4. Web Management Interface

### 4.1. Overview

The web management interface provides a user-friendly way to distribute OpenVPN client configuration files to users. It includes:

- User authentication system
- Download management

### 4.2. Installation and Setup

1. **Install Python dependencies:**

   ```bash
   conda create -n ovpn python=3.10 -y
   conda activate ovpn
   ```

   ```bash
   pip3 install -r requirements.txt
   ```

2. **Modify file path of client files:**(in `config.py`)

   ```python
    # File path configuration
    CLIENT_FILES_DIR = '.'  # Base directory where client files are located
    CLIENT_FILE_PATTERN = 'clients_ovpn/client*.ovpn'  # Client file matching pattern
   ```

3. **Initialize the database:**

   ```bash
   python3 db_init.py
   ```

   This will:

   - Create the SQLite database
   - Create necessary tables (users, client_files)
   - Add default admin user
   - Scan for existing client files and add them to database

4. **Start the web server:**

   ```bash
   ./start_server.sh
   ```

   Or manually:

   ```bash
   python3 app.py
   ```

5. **Access the web interface:**
   - Open your browser and go to `http://localhost:5000`
   - Default admin credentials: `admin` / `admin123`

### 4.3. Features

#### 4.3.1. For Users:

- **File Download**: Download assigned client configuration files
- **Personal Dashboard**: View only files assigned to you
- **Secure Access**: Only download files assigned to you
- **Simple Interface**: Clean and easy-to-use interface

#### 4.3.2. For Administrators:

- **Backend Management**: Use command-line tools to manage users and file assignments
- **CSV Import**: Bulk import users from CSV files
- **User Management**: Add, remove, and modify user accounts
- **File Assignment**: Assign client files to users via database operations

### 4.4. Administrator Operations

#### 4.4.1. Initialize database

```bash
python3 db_init.py
```

#### 4.4.2. User Management:

```bash
# Interactive user management
python3 manage_users.py

# Import users from CSV
python3 manage_users.py --import-csv users.csv

# Export users to CSV
python3 manage_users.py --export-csv users_backup.csv

# List all users
python3 manage_users.py --list-users
```

#### 4.4.3. Generate Random Users:

```bash
# Generate 100 random users
python3 generate_random_users.py -n 100 -o users.csv

# Preview generated users
python3 generate_random_users.py -n 10 --preview
```

#### 4.4.4. File Assignment:

```bash
# Interactive file assignment
python3 assign_files.py

# List all files and their status
python3 assign_files.py --list-files

# List all users
python3 assign_files.py --list-users

# Assign specific file to user
python3 assign_files.py --assign client1.ovpn username1 --notes "Production user"

# Unassign file
python3 assign_files.py --unassign client1.ovpn

# Batch assign files using regex patterns
python3 assign_files.py --batch-assign ".*" ".*client.*.ovpn" --notes "Batch assignment"
```

#### 4.4.5. For Users:

1. **Access the web interface:**

   - Go to `http://YOUR_SERVER:5000`（default port is 5000）
   - Login with your credentials

2. **Download your files:**
   - View assigned client files
   - Download `.ovpn` configuration files
   - Import to OpenVPN client

### 4.5. Database

The system uses SQLite database (`ovpn_clients.db`) to store:

- **users table**: user accounts and authentication
- **client_files table**: client configuration files and assignments

#### 4.5.1. Database Schema:

**users table:**

- `id`: Primary key
- `username`: Unique username
- `password_hash`: Hashed password
- `is_admin`: Boolean admin flag

**client_files table:**

- `id`: Primary key
- `filename`: Client file name (e.g., client1.ovpn)
- `assigned_to`: Username of assigned user
- `assigned_date`: Assignment timestamp
- `notes`: Assignment notes
- `is_available`: Boolean availability flag
