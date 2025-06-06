#!/bin/bash

echo "[INFO] Installing Python dependencies..."

REQ_FILE="$(dirname "$0")/../requirements.txt"

if [ -f "$REQ_FILE" ]; then
    pip install --break-system-packages -r "$REQ_FILE"
    echo "[INFO] ✅ requirements.txt installed successfully"
else
    echo "[ERROR] ❌ requirements.txt not found at $REQ_FILE"
    exit 1
fi
