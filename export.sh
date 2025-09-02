#!/bin/bash
# PIM RDF Export Tool
# Simple wrapper script for the Python export tool

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
PYTHON_SCRIPT="$SCRIPT_DIR/export.py"

# Check if export.py exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: export.py not found in $SCRIPT_DIR"
    exit 1
fi

# Default behavior: export both HTML and JSON-LD
if [ $# -eq 0 ]; then
    echo "PIM RDF Export Tool"
    echo "=================="
    echo "Exporting knowledge base to HTML and JSON-LD..."
    python3 "$PYTHON_SCRIPT" --all
    echo ""
    echo "Files generated:"
    echo "  - html_export/index.html (and other HTML files)"
    echo "  - export.jsonld"
    echo ""
    echo "To view the HTML export, open html_export/index.html in your browser"
    echo "or run: python3 -m http.server 8000 --directory html_export"
else
    # Pass all arguments to the Python script
    python3 "$PYTHON_SCRIPT" "$@"
fi