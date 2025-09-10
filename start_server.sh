#!/bin/bash

# OpenVPN Client Management Web Server Startup Script

echo "Starting OpenVPN Client Management Web Server..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi


# Check if port is occupied
PORT=5000
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "Warning: Port $PORT is already in use"
    echo "Please stop the program using this port or modify the port setting in app.py"
    exit 1
fi

# Start server
echo "Starting Web server on port $PORT..."
echo "Access URL: http://localhost:$PORT"
echo "Default admin account: admin / admin123"
echo ""
echo "Press Ctrl+C to stop the server"

python3 app.py
