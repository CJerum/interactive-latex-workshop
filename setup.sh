#!/bin/bash

# Interactive LaTeX Workshop Setup Script

echo "🔧 Setting up Interactive LaTeX Workshop..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check LaTeX installation
echo "🔍 Checking LaTeX installation..."

if command -v pdflatex &> /dev/null; then
    echo "✅ pdflatex found"
else
    echo "❌ pdflatex not found"
    echo "Please install a LaTeX distribution:"
    echo "  macOS: brew install --cask mactex"
    echo "  Linux: sudo apt-get install texlive-full"
    echo "  Windows: Install MiKTeX or TeX Live"
fi

# Check PDF conversion tools
if command -v pdftoppm &> /dev/null; then
    echo "✅ pdftoppm found (from poppler)"
elif command -v convert &> /dev/null; then
    echo "✅ ImageMagick convert found"
else
    echo "⚠️  No PDF conversion tool found"
    echo "Install one of the following:"
    echo "  macOS: brew install poppler"
    echo "  Linux: sudo apt-get install poppler-utils"
    echo "  Or install ImageMagick"
fi

# Check bibliography tools
if command -v biber &> /dev/null; then
    echo "✅ biber found"
else
    echo "ℹ️  biber not found (optional for bibliography)"
fi

if command -v bibtex &> /dev/null; then
    echo "✅ bibtex found"
else
    echo "ℹ️  bibtex not found (optional for bibliography)"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the workshop:"
echo "  1. Run: ./start_backend.sh (in one terminal)"
echo "  2. Run: ./start_frontend.sh (in another terminal)"
echo "  3. Open: http://127.0.0.1:3000"
echo ""
echo "Or use: ./run_workshop.sh to start both servers"
