#!/usr/bin/env python3
"""
Interactive LaTeX Slides Backend
Flask API server for live LaTeX compilation during presentations
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from flask_cors import CORS
import base64
import uuid
import shutil

# Set up Flask app with proper template and static directories
app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
CORS(app)  # Enable CORS for frontend communication

# Configuration
TEMP_DIR = Path(__file__).parent.parent / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# Base LaTeX preamble (from your notebook)
BASE_PREAMBLE = r"""
\documentclass[11pt]{article}
\usepackage[margin=0.5in]{geometry}
\usepackage{amsmath,amsfonts,amssymb}
\usepackage{siunitx}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{float}
\usepackage[hidelinks]{hyperref}
\usepackage{microtype}
"""

def render_snippet(body, preamble_extra="", sanitize_graphics=True, 
                  passes=1, bib_entries=None, use_biblatex=False, 
                  hide_warnings=False):
    """
    Render LaTeX snippet and return PNG image data
    Adapted from your notebook's render_snippet function
    """
    try:
        # Create unique temporary directory
        temp_id = str(uuid.uuid4())
        temp_path = TEMP_DIR / temp_id
        temp_path.mkdir(exist_ok=True)
        
        # Construct full LaTeX document
        full_preamble = BASE_PREAMBLE + "\n" + preamble_extra
        
        # Handle bibliography setup
        if bib_entries:
            if use_biblatex:
                full_preamble += "\n\\usepackage[style=numeric]{biblatex}"
                full_preamble += "\n\\addbibresource{references.bib}"
                bib_command = "\\printbibliography"
            else:
                full_preamble += "\n\\usepackage{natbib}"
                bib_command = "\\bibliography{references}"
        else:
            bib_command = ""
        
        latex_content = f"""
{full_preamble}

\\begin{{document}}
{body}
{bib_command}
\\end{{document}}
"""
        
        # Write LaTeX file
        tex_file = temp_path / "document.tex"
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        # Write bibliography file if needed
        if bib_entries:
            bib_file = temp_path / "references.bib"
            with open(bib_file, 'w', encoding='utf-8') as f:
                f.write(bib_entries)
        
        # Compile LaTeX
        compile_result = compile_latex(tex_file, passes, use_biblatex, hide_warnings)
        
        if not compile_result["success"]:
            return {
                "success": False,
                "error": compile_result["error"],
                "log": compile_result.get("log", "")
            }

        # Convert PDF to PNG (with cropping for better fit)
        pdf_file = temp_path / "document.pdf"
        png_file = temp_path / "document.png"

        convert_result = pdf_to_png(pdf_file, png_file, dpi=300, crop=True)

        if not convert_result["success"]:
            return {
                "success": False,
                "error": convert_result["error"]
            }

        # Read PNG as base64
        with open(png_file, 'rb') as f:
            png_data = base64.b64encode(f.read()).decode('utf-8')

        # Cleanup
        shutil.rmtree(temp_path)

        return {
            "success": True,
            "image_data": png_data,
            "temp_id": temp_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

def compile_latex(tex_file, passes=1, use_biblatex=False, hide_warnings=False):
    """Compile LaTeX document"""
    try:
        temp_path = tex_file.parent
        
        for i in range(passes):
            # Run pdflatex
            pdflatex_cmd = find_command("pdflatex")
            cmd = [pdflatex_cmd, "-interaction=nonstopmode", str(tex_file)]
            result = subprocess.run(
                cmd, 
                cwd=temp_path, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "LaTeX compilation failed",
                    "log": result.stdout + "\n" + result.stderr
                }
            
            # Run bibliography if needed and on first pass
            if i == 0 and (temp_path / "references.bib").exists():
                if use_biblatex:
                    biber_cmd = find_command("biber")
                    bib_cmd = [biber_cmd, "document"]
                else:
                    bibtex_cmd = find_command("bibtex")
                    bib_cmd = [bibtex_cmd, "document"]
                
                bib_result = subprocess.run(
                    bib_cmd,
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                # Note: bibtex/biber can fail on first run, that's normal
        
        return {"success": True}
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "LaTeX compilation timed out"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Compilation error: {str(e)}"
        }

def find_command(command):
    """Find the full path to a command"""
    try:
        result = subprocess.run(["which", command], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return command  # fallback to original command name

def pdf_to_png(pdf_file, png_file, dpi=150, crop=True):
    """Convert PDF to PNG, optionally cropping margins for better preview fit"""
    try:
        source_pdf = pdf_file

        # Prefer cropping the PDF first using pdfcrop (TeX Live), keeps vector fidelity before rasterizing
        if crop and check_command("pdfcrop"):
            cropped_pdf = pdf_file.parent / "document-cropped.pdf"
            pdfcrop_cmd = find_command("pdfcrop")
            # keep a tiny margin (3bp) to avoid clipping
            cmd = [pdfcrop_cmd, "--margins", "3", str(pdf_file), str(cropped_pdf)]
            subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if cropped_pdf.exists():
                source_pdf = cropped_pdf

        # Try pdftoppm first (from poppler-utils)
        pdftoppm_cmd = find_command("pdftoppm")
        cmd = [pdftoppm_cmd, "-png", "-singlefile", "-r", str(dpi), str(source_pdf), str(png_file.with_suffix(''))]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Optionally trim residual borders on the PNG if pdfcrop wasn't available
            if crop and not str(source_pdf).endswith("document-cropped.pdf"):
                _trim_png_inplace(png_file)
            return {"success": True}
        
        # Fallback to ImageMagick convert
        convert_cmd = find_command("convert") if check_command("convert") else find_command("magick")
        # If magick is used, command is: magick -density <dpi> input.pdf output.png
        if os.path.basename(convert_cmd) == "magick":
            cmd = [convert_cmd, "-density", str(dpi), str(source_pdf), str(png_file)]
        else:
            cmd = [convert_cmd, "-density", str(dpi), str(source_pdf), str(png_file)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            if crop:
                _trim_png_inplace(png_file)
            return {"success": True}
        
        return {
            "success": False,
            "error": f"Failed to convert PDF to PNG. pdftoppm result: {result.stderr}, convert not available."
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "PDF conversion timed out"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Conversion error: {str(e)}"
        }

def _trim_png_inplace(png_file):
    """Try to trim uniform borders from the PNG using ImageMagick if available"""
    try:
        # Prefer magick if present
        if check_command("magick"):
            cmd = [find_command("magick"), str(png_file), "-trim", "+repage", str(png_file)]
        elif check_command("convert"):
            cmd = [find_command("convert"), str(png_file), "-trim", "+repage", str(png_file)]
        else:
            return False
        subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return True
    except Exception:
        return False

def readiness_report():
    """Check if required tools are available"""
    tools = {
        "pdflatex": check_command("pdflatex"),
        "biber": check_command("biber"),
        "bibtex": check_command("bibtex"),
        "pdftoppm": check_command("pdftoppm"),
    "convert": check_command("convert") or check_command("magick"),
    "pdfcrop": check_command("pdfcrop")
    }
    
    return {
    "ready": tools["pdflatex"] and (tools["pdftoppm"] or tools["convert"]),
        "tools": tools
    }

def check_command(command):
    """Check if a command is available"""
    try:
        # First try using 'which' to find the command
        result = subprocess.run(["which", command], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            return True
            
        # Fallback: try running the command with --version
        result = subprocess.run([command, "--version"], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        return result.returncode == 0
    except:
        return False

# API Routes
@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('../static', filename)

@app.route('/api/compile', methods=['POST'])
def api_compile():
    """Compile LaTeX snippet and return PNG"""
    data = request.get_json()
    
    if not data or 'body' not in data:
        return jsonify({
            "success": False,
            "error": "Missing 'body' parameter"
        }), 400
    
    result = render_snippet(
        body=data['body'],
        preamble_extra=data.get('preamble_extra', ''),
        sanitize_graphics=data.get('sanitize_graphics', True),
        passes=data.get('passes', 1),
        bib_entries=data.get('bib_entries'),
        use_biblatex=data.get('use_biblatex', False),
        hide_warnings=data.get('hide_warnings', False)
    )
    
    return jsonify(result)

@app.route('/api/readiness', methods=['GET'])
def api_readiness():
    """Check if LaTeX tools are available"""
    return jsonify(readiness_report())

@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "interactive-latex-slides-backend"
    })

if __name__ == '__main__':
    print("Starting Interactive LaTeX Slides Backend...")
    print(f"Temp directory: {TEMP_DIR}")
    
    # Check readiness
    readiness = readiness_report()
    print(f"System readiness: {readiness}")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
