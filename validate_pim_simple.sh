#!/bin/bash
# Simple PIM RDF Validation Script
# Tests basic syntax and structure using available tools

DIRECTORY="${1:-.}"

echo "PIM RDF Simple Validation"
echo "Working directory: $DIRECTORY"
echo "========================="

# Count TTL files
ttl_count=$(find "$DIRECTORY" -name "*.ttl" -not -name "merged*.ttl" | wc -l)
echo "Found $ttl_count TTL files to validate"

# Basic file existence check
echo ""
echo "=== File Structure Check ==="
for file in base.ttl tasks.ttl notes.ttl contacts.ttl projects.ttl bookmarks.ttl events.ttl tags.ttl; do
    if [[ -f "$DIRECTORY/$file" ]]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
    fi
done

# Check for shapes directory
echo ""
echo "=== SHACL Shapes Check ==="
if [[ -d "$DIRECTORY/shapes" ]]; then
    echo "✓ shapes/ directory exists"
    shape_count=$(find "$DIRECTORY/shapes" -name "*.ttl" | wc -l)
    echo "  Found $shape_count shape files"
else
    echo "⚠ shapes/ directory not found"
fi

# Check for queries directory
echo ""
echo "=== Queries Check ==="
if [[ -d "$DIRECTORY/queries" ]]; then
    echo "✓ queries/ directory exists"
    query_count=$(find "$DIRECTORY/queries" -name "*.sparql" | wc -l)
    echo "  Found $query_count query files"
else
    echo "⚠ queries/ directory not found"
fi

# If we're in a Nix shell, try using riot
echo ""
echo "=== Tool Availability Check ==="
if command -v riot &>/dev/null; then
    echo "✓ riot command available"
    echo "Testing riot validation on base.ttl:"
    if riot --validate --syntax=turtle "$DIRECTORY/base.ttl" &>/dev/null; then
        echo "  ✓ base.ttl is valid Turtle"
    else
        echo "  ✗ base.ttl validation failed"
    fi
else
    echo "⚠ riot command not available (try running in nix-shell)"
fi

if command -v shacl &>/dev/null; then
    echo "✓ shacl command available"
else
    echo "⚠ shacl command not available (try running in nix-shell)"
fi

echo ""
echo "========================="
echo "✅ Basic validation completed"
echo ""
echo "For full validation, run this script within nix-shell:"
echo "  nix-shell --run './validate_pim_simple.sh'"
