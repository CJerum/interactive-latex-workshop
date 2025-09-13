#!/usr/bin/env python3
"""
Simple Flask app to serve the interactive slides
"""

from flask import Flask, render_template, send_from_directory
from backend.app import app as api_app
import os
from pathlib import Path

# Create main Flask app for serving the slides
main_app = Flask(__name__, 
                 template_folder='templates',
                 static_folder='static')

@main_app.route('/')
def index():
    """Serve the main slides page"""
    return render_template('index.html')

@main_app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    print("Starting Interactive LaTeX Workshop...")
    print("=" * 50)
    print("Frontend server: http://127.0.0.1:3000")
    print("Backend API: http://127.0.0.1:5000")
    print("=" * 50)
    print("\nStarting frontend server...")
    
    main_app.run(debug=True, host='127.0.0.1', port=3000)
