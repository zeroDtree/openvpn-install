#!/bin/bash

# OpenVPN Client Management Web Server Startup Script

# Default port
DEFAULT_PORT=5000
PORT=$DEFAULT_PORT

# Function to show usage
show_usage() {
    echo "Usage: $0 [-p|--port PORT]"
    echo "  -p, --port PORT    Specify the port number (default: $DEFAULT_PORT)"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Start server on default port $DEFAULT_PORT"
    echo "  $0 -p 8080         # Start server on port 8080"
    echo "  $0 --port 3000     # Start server on port 3000"
    echo ""
    echo "Note: The port is passed to the application via OPENVPN_WEB_PORT environment variable"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
                echo "Error: Port must be a number between 1 and 65535"
                exit 1
            fi
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Error: Unknown option $1"
            show_usage
            exit 1
            ;;
    esac
done

echo "Starting OpenVPN Client Management Web Server..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

# Check if port is occupied
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "Warning: Port $PORT is already in use"
    echo "Please stop the program using this port or specify a different port"
    echo "Use '$0 --help' for usage information"
    exit 1
fi

# Start server
echo "Starting Web server on port $PORT..."
echo "Access URL: http://localhost:$PORT"
echo "Default admin account: admin / admin123"
echo ""
echo "Press Ctrl+C to stop the server"

# Set the port environment variable for the Python app
export OPENVPN_WEB_PORT=$PORT
python3 app.py
