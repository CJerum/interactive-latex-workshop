# Interactive LaTeX Workshop Slides

A web-based interactive presentation system for teaching LaTeX with live compilation capabilities. This project transforms your traditional LaTeX workshop into an engaging, hands-on experience where students can edit and compile LaTeX code directly in the browser.

## Features

- 🎯 **Interactive Slides**: Web-based presentation using Reveal.js
- ⚡ **Live LaTeX Compilation**: Real-time rendering with your existing `render_snippet` function  
- 🎨 **Syntax Highlighting**: Beautiful code display with Prism.js
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- 💾 **Auto-save**: Student edits persist in browser localStorage
- ⌨️ **Keyboard Shortcuts**: Ctrl+Enter to compile code
- 🔧 **System Health Checks**: Visual indicators for LaTeX tool availability

## Architecture

```
Frontend (Port 3000)          Backend (Port 5000)
┌─────────────────────┐      ┌─────────────────────┐
│ HTML/CSS/JS         │ HTTP │ Flask API           │
│ - Reveal.js slides  │─────▶│ - render_snippet()  │
│ - Code editors      │      │ - LaTeX compilation │
│ - Live compilation  │      │ - PDF → PNG         │
└─────────────────────┘      └─────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.7+
- LaTeX distribution (MacTeX, TeX Live, or MiKTeX)
- PDF conversion tools (poppler-utils or ImageMagick)

### Installation

1. **Clone or set up the project structure** (already done!)

2. **Run the setup script**:
   ```bash
   ./setup.sh
   ```

3. **Start the workshop**:
   ```bash
   ./run_workshop.sh
   ```

4. **Open your browser** to http://127.0.0.1:3000

### Alternative: Manual Start

If you prefer to run the servers separately:

```bash
# Terminal 1: Backend
./start_backend.sh

# Terminal 2: Frontend  
./start_frontend.sh
```

## Workshop Structure

The interactive slides cover these modules:

1. **Document Setup** - Basic LaTeX structure
2. **Mathematical Equations** - Inline and display math with siunitx
3. **Professional Tables** - Data presentation with booktabs
4. **Figures and Graphics** - Figure templates and referencing
5. **Analysis Section** - Calculations and error analysis
6. **Final Assembly** - Overleaf integration instructions

Each module includes:
- ✏️ **Editable code examples**
- 🖼️ **Live rendering preview**
- 💡 **Interactive demonstrations**
- 📝 **Teaching notes and tips**

## API Endpoints

### Backend API (Port 5000)

- `POST /api/compile` - Compile LaTeX snippet
- `GET /api/readiness` - Check LaTeX tools availability  
- `GET /api/health` - Health check

### Frontend Routes (Port 3000)

- `GET /` - Main slides interface
- `GET /static/*` - Static assets (CSS, JS, images)

## Customization

### Adding New Slides

Edit `templates/index.html` and add new `<section>` elements:

```html
<section>
    <h3>Your New Module</h3>
    <div class="latex-editor">
        <textarea id="editor-new">Your LaTeX code here</textarea>
    </div>
    <div class="latex-controls">
        <button class="compile-btn" onclick="compileLatex('editor-new', 'output-new')">
            Compile & Render
        </button>
    </div>
    <div class="latex-output" id="output-new">
        <span class="loading">Click "Compile & Render" to see the output</span>
    </div>
</section>
```

### Modifying LaTeX Preamble

Edit the `BASE_PREAMBLE` in `backend/app.py`:

```python
BASE_PREAMBLE = r"""
\\documentclass[11pt]{article}
\\usepackage[margin=1in]{geometry}
\\usepackage{amsmath,amsfonts,amssymb}
\\usepackage{siunitx}
\\usepackage{booktabs}
\\usepackage{graphicx}
\\usepackage[hidelinks]{hyperref}
\\usepackage{microtype}
% Add your custom packages here
"""
```

### Styling Changes

Modify `static/css/custom.css` for visual customizations.

## Technical Details

### LaTeX Compilation Process

1. Student enters LaTeX code in browser
2. JavaScript sends code to Flask backend
3. Backend creates temporary directory
4. LaTeX document assembled with preamble
5. `pdflatex` compilation (with optional bibliography)
6. PDF converted to PNG via pdftoppm or ImageMagick
7. PNG returned as base64 to frontend
8. Image displayed in browser

### Error Handling

- **Compilation errors**: LaTeX log displayed to user
- **Missing tools**: System status indicators
- **Network issues**: Graceful fallback messages
- **Timeout protection**: 30-second limits on compilation

### Security Considerations

- LaTeX compilation runs in temporary directories
- File cleanup after each compilation
- Input sanitization for safety
- Local-only access by default

## Troubleshooting

### Common Issues

**"Backend unavailable"**
- Ensure backend server is running on port 5000
- Check firewall settings

**"LaTeX compilation failed"**  
- Verify pdflatex installation: `pdflatex --version`
- Check LaTeX syntax in error log

**"PDF conversion failed"**
- Install poppler-utils: `brew install poppler` (macOS)
- Or install ImageMagick: `brew install imagemagick`

**"Permission denied"**
- Make scripts executable: `chmod +x *.sh`
- Check write permissions in temp directory

### System Requirements Check

Run the readiness endpoint to verify your setup:
```bash
curl http://127.0.0.1:5000/api/readiness
```

## File Structure

```
LaTeX Workshop (Web-based)/
├── backend/
│   └── app.py              # Flask API server with render_snippet
├── static/
│   ├── css/
│   │   └── custom.css      # Custom styling
│   └── js/
│       └── latex-slides.js # Frontend JavaScript
├── templates/
│   └── index.html          # Main slides template
├── temp/                   # Temporary compilation files
├── requirements.txt        # Python dependencies
├── server.py              # Frontend Flask server
├── setup.sh               # Setup script
├── start_backend.sh       # Backend startup
├── start_frontend.sh      # Frontend startup
├── run_workshop.sh        # Combined startup
└── README.md              # This file
```

## Contributing

This workshop system is built around your existing `render_snippet` function and can be extended with:

- Additional LaTeX modules
- Enhanced error reporting
- Student progress tracking
- Template export features
- Integration with Overleaf API

## License

Created for educational use in physics lab report template building workshops.

---

**Happy teaching with interactive LaTeX!** 🎓✨
