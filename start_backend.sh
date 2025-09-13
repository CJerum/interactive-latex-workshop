#!/bin/bash

# Start the backend API server

echo "🚀 Starting LaTeX Workshop Backend..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Start the backend
cd backend
python app.py
