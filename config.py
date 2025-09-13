# Interactive LaTeX Workshop Configuration

# Server Settings
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 5000
FRONTEND_HOST = "127.0.0.1" 
FRONTEND_PORT = 3000

# LaTeX Compilation Settings
DEFAULT_PASSES = 1
COMPILATION_TIMEOUT = 30  # seconds
CLEANUP_TEMP_FILES = True

# PDF to PNG Conversion
DEFAULT_DPI = 150
PREFER_PDFTOPPM = True  # Use pdftoppm over ImageMagick if available

# Workshop Settings
AUTO_SAVE_ENABLED = True
KEYBOARD_SHORTCUTS = True
SHOW_COMPILATION_LOGS = True

# Styling
THEME = "white"  # Reveal.js theme
SYNTAX_THEME = "prism"  # Prism.js theme
CUSTOM_CSS_ENABLED = True
