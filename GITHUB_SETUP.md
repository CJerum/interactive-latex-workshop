## GitHub Setup Instructions

### 1. Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `interactive-latex-workshop`
3. Description: `Interactive LaTeX Workshop with live compilation and professional lab report templates`
4. Set to Public or Private (your choice)
5. **Don't** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### 2. Push to GitHub
After creating the repository, run these commands:

```bash
cd "/Users/colejerum/Documents/URochester/Misc/LaTeX Workshop (Web-based)"
git remote add origin https://github.com/CJerum/interactive-latex-workshop.git
git branch -M main
git push -u origin main
```

### 3. Test Deployment
Clone and test the repository:

```bash
# In a new directory
git clone https://github.com/CJerum/interactive-latex-workshop.git
cd interactive-latex-workshop
./run_workshop.sh
```

Then open http://127.0.0.1:5000 in your browser.

### Quick Deploy Commands
```bash
# Setup and run (one-time)
./setup.sh
./run_workshop.sh

# Or run components separately
./start_backend.sh    # Terminal 1
./start_frontend.sh   # Terminal 2 (if needed)
```

### Repository URL
Once pushed: https://github.com/CJerum/interactive-latex-workshop
