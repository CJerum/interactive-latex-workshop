#!/bin/bash

# Start the frontend slides server

echo "🎨 Starting LaTeX Workshop Frontend..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Start the frontend
python server.py
