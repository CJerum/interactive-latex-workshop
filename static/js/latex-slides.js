/**
 * Interactive LaTeX Slides JavaScript
 * Handles communication with the Flask backend for live LaTeX compilation
 */

const API_BASE = 'http://127.0.0.1:5000/api';

// Global state
let backendReady = false;
let codeMirrorInstances = {};

/**
 * Initialize CodeMirror instances for all LaTeX editors
 */
function initializeCodeMirror() {
        const USE_CODEMIRROR = false; // disable CM due to cursor misalignment
        // Initialize CodeMirror for all LaTeX editors; fallback to textarea if CM unavailable
        const editors = document.querySelectorAll('.latex-editor textarea');

        editors.forEach(textarea => {
                const editorId = textarea.id;

                if (USE_CODEMIRROR && window.CodeMirror) {
                        const cm = CodeMirror.fromTextArea(textarea, {
                                mode: 'stex',
                                theme: 'elegant',
                                lineNumbers: false,
                                lineWrapping: true,
                                matchBrackets: true,
                                autoCloseBrackets: true,
                                styleActiveLine: { nonEmpty: true },
                                cursorScrollMargin: 4
                        });

                        // Size to container
                        cm.setSize('100%', '100%');

                        // Persist content
                        const storageKey = `latex-slides-${editorId}`;
                        const saved = localStorage.getItem(storageKey);
                        if (saved) cm.setValue(saved);
                        cm.on('change', () => {
                                localStorage.setItem(storageKey, cm.getValue());
                        });

                        codeMirrorInstances[editorId] = cm;
                } else {
                        // Fallback: ensure proper wrapping for textarea
                        textarea.style.whiteSpace = 'pre-wrap';
                        textarea.style.overflowWrap = 'anywhere';
                        textarea.style.wordBreak = 'break-word';
                        textarea.style.overflowX = 'hidden';
                        textarea.setAttribute('wrap', 'soft');

                        const storageKey = `latex-slides-${editorId}`;
                        const saved = localStorage.getItem(storageKey);
                        if (saved) textarea.value = saved;
                        textarea.addEventListener('input', function () {
                                localStorage.setItem(storageKey, textarea.value);
                        });

                        codeMirrorInstances[editorId] = {
                                getValue: () => textarea.value,
                                setValue: (value) => { textarea.value = value; },
                                hasFocus: () => document.activeElement === textarea,
                                focus: () => textarea.focus()
                        };
                }
        });
}

/**
 * Check if the backend is ready and update status indicator
 */
async function checkBackendStatus() {
        const statusElement = document.getElementById('backend-status');
        const indicator = statusElement.querySelector('.status-indicator');

        try {
                // Check health endpoint
                const healthResponse = await fetch(`${API_BASE}/health`);
                if (!healthResponse.ok) throw new Error('Health check failed');

                // Check readiness
                const readinessResponse = await fetch(`${API_BASE}/readiness`);
                if (!readinessResponse.ok) throw new Error('Readiness check failed');

                const readiness = await readinessResponse.json();

                if (readiness.ready) {
                        indicator.className = 'status-indicator status-ready';
                        statusElement.innerHTML = `
                <span class="status-indicator status-ready"></span>
                Backend ready! LaTeX tools available.
            `;
                        backendReady = true;
                } else {
                        indicator.className = 'status-indicator status-error';
                        statusElement.innerHTML = `
                <span class="status-indicator status-error"></span>
                Backend connected but missing LaTeX tools.
            `;

                        // Show detailed tool status
                        const missingTools = Object.entries(readiness.tools)
                                .filter(([tool, available]) => !available)
                                .map(([tool, _]) => tool);

                        if (missingTools.length > 0) {
                                statusElement.innerHTML += `<br><small>Missing: ${missingTools.join(', ')}</small>`;
                        }
                }

        } catch (error) {
                indicator.className = 'status-indicator status-error';
                statusElement.innerHTML = `
            <span class="status-indicator status-error"></span>
            Backend unavailable. Start the Flask server first.
        `;
                backendReady = false;
                console.error('Backend status check failed:', error);
        }
}

/**
 * Compile LaTeX code and display the result
 * @param {string} editorId - ID of the editor containing LaTeX code
 * @param {string} outputId - ID of the div to display output
 */
async function compileLatex(editorId, outputId) {
        const output = document.getElementById(outputId);
        const button = event?.target || document.querySelector(`[onclick*="${editorId}"]`);

        if (!backendReady) {
                showError(output, 'Backend not ready. Please check the server status.');
                return;
        }

        // Get LaTeX code from CodeMirror instance or fallback to textarea
        let latexCode = '';
        if (codeMirrorInstances[editorId]) {
                latexCode = codeMirrorInstances[editorId].getValue().trim();
        } else {
                const editor = document.getElementById(editorId);
                latexCode = editor.value.trim();
        }

        if (!latexCode) {
                showError(output, 'Please enter some LaTeX code to compile.');
                return;
        }

        // Show loading state
        if (button) {
                button.disabled = true;
                button.textContent = 'Compiling...';
        }
        output.innerHTML = '<span class="loading">Compiling LaTeX...</span>';

        try {
                const response = await fetch(`${API_BASE}/compile`, {
                        method: 'POST',
                        headers: {
                                'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                                body: latexCode,
                                preamble_extra: '',
                                sanitize_graphics: true,
                                passes: 1,
                                hide_warnings: false
                        })
                });

                if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const result = await response.json();

                if (result.success) {
                        // Display the rendered image
                        output.innerHTML = `
                <img src="data:image/png;base64,${result.image_data}" 
                     alt="Rendered LaTeX" 
                     style="max-width: 100%; height: auto;" />
            `;
                } else {
                        showError(output, result.error, result.log);
                }

        } catch (error) {
                showError(output, `Network error: ${error.message}`);
                console.error('Compilation failed:', error);
        } finally {
                // Restore button state
                if (button) {
                        button.disabled = false;
                        button.textContent = 'Compile & Render';
                }
        }
}

/**
 * Display an error message in the output area
 * @param {HTMLElement} outputElement - The output container
 * @param {string} message - Error message
 * @param {string} log - Optional compilation log
 */
function showError(outputElement, message, log = '') {
        let errorHtml = `<div class="error-message">Error: ${message}</div>`;

        if (log) {
                errorHtml += `<details style="margin-top: 10px;">
            <summary style="cursor: pointer; color: #666;">Show compilation log</summary>
            <pre style="margin-top: 10px; font-size: 10px; max-height: 200px; overflow-y: auto;">${log}</pre>
        </details>`;
        }

        outputElement.innerHTML = errorHtml;
}

/**
 * Add LaTeX code to an editor (for preset examples)
 * @param {string} editorId - ID of the editor
 * @param {string} code - LaTeX code to insert
 */
function insertLatexCode(editorId, code) {
        if (codeMirrorInstances[editorId]) {
                codeMirrorInstances[editorId].setValue(code);
                codeMirrorInstances[editorId].focus();
        } else {
                const editor = document.getElementById(editorId);
                editor.value = code;
                editor.focus();
        }
}

/**
 * Clear an output area
 * @param {string} outputId - ID of the output div
 */
function clearOutput(outputId) {
        const output = document.getElementById(outputId);
        output.innerHTML = '<span class="loading">Click "Compile & Render" to see the output</span>';
}

/**
 * Download the current LaTeX code as a .tex file
 * @param {string} editorId - ID of the editor
 * @param {string} filename - Desired filename
 */
function downloadLatex(editorId, filename = 'latex-code.tex') {
        let code = '';
        if (codeMirrorInstances[editorId]) {
                code = codeMirrorInstances[editorId].getValue();
        } else {
                const editor = document.getElementById(editorId);
                code = editor.value;
        }

        const blob = new Blob([code], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
}

/**
 * Copy LaTeX code to clipboard
 * @param {string} editorId - ID of the editor
 */
async function copyToClipboard(editorId) {
        let code = '';
        if (codeMirrorInstances[editorId]) {
                code = codeMirrorInstances[editorId].getValue();
        } else {
                const editor = document.getElementById(editorId);
                code = editor.value;
        }

        try {
                await navigator.clipboard.writeText(code);

                // Show temporary success message
                const button = event.target;
                const originalText = button.textContent;
                button.textContent = 'Copied!';
                button.style.backgroundColor = '#4caf50';

                setTimeout(() => {
                        button.textContent = originalText;
                        button.style.backgroundColor = '';
                }, 1500);

        } catch (error) {
                console.error('Failed to copy:', error);
                alert('Failed to copy to clipboard');
        }
}

// Keyboard shortcuts
document.addEventListener('keydown', function (event) {
        // Ctrl/Cmd + Enter to compile the focused editor
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
                // Check if a CodeMirror instance is focused
                for (const [editorId, cm] of Object.entries(codeMirrorInstances)) {
                        if (cm.hasFocus()) {
                                const outputId = getOutputIdFromEditor(editorId);
                                compileLatex(editorId, outputId);
                                event.preventDefault();
                                return;
                        }
                }

                // Fallback to textarea check
                const activeElement = document.activeElement;
                if (activeElement.tagName === 'TEXTAREA' && activeElement.closest('.latex-editor')) {
                        const editorId = activeElement.id;
                        const outputId = getOutputIdFromEditor(editorId);
                        compileLatex(editorId, outputId);
                        event.preventDefault();
                }
        }
});

// Helper function to get output ID from editor ID
function getOutputIdFromEditor(editorId) {
        // Handle different naming patterns
        const outputMappings = {
                'complete-template': 'complete-output',
                'preamble-editor': 'preamble-output',
                'abstract-editor': 'abstract-output',
                'methods-editor': 'methods-output',
                'data-editor': 'data-output',
                'analysis-editor': 'analysis-output',
                'conclusion-editor': 'conclusion-output'
        };

        return outputMappings[editorId] || editorId.replace('-editor', '-output');
}

// Auto-save setup is now handled in initializeCodeMirror
function setupAutoSave() {
        // Ensure autosave for any textareas not initialized yet
        const editors = document.querySelectorAll('.latex-editor textarea');

        editors.forEach(editor => {
                if (codeMirrorInstances[editor.id]) return;

                const storageKey = `latex-slides-${editor.id}`;

                const saved = localStorage.getItem(storageKey);
                if (saved) {
                        editor.value = saved;
                }

                editor.addEventListener('input', function () {
                        localStorage.setItem(storageKey, editor.value);
                });
        });
}

// Initialize both CodeMirror and auto-save when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
        setupAutoSave();
        initializeCodeMirror();
        addTooltips();
});

// Add helpful tooltips
function addTooltips() {
        const buttons = document.querySelectorAll('.compile-btn');
        buttons.forEach(button => {
                button.title = 'Click to compile LaTeX code (Ctrl+Enter)';
        });
}

// Removed overlay highlighting to ensure stable editing.
