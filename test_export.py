#!/usr/bin/env python3
"""
Simple test to validate export functionality.
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from export import PIMExporter

def test_exports():
    """Test both HTML and JSON-LD exports."""
    print("Testing PIM RDF export functionality...")
    
    # Create a temporary directory for test output
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Initialize exporter with current directory (where the TTL files are)
        exporter = PIMExporter(".")
        
        print("Loading test data...")
        exporter.load_data()
        
        if len(exporter.graph) == 0:
            print("❌ No data loaded - TTL files may have syntax errors")
            return False
            
        print(f"✅ Loaded {len(exporter.graph)} triples")
        
        # Test HTML export
        print("Testing HTML export...")
        html_dir = temp_path / "test_html"
        exporter.export_html(html_dir)
        
        # Check HTML files exist
        required_files = ["index.html", "tasks.html", "notes.html", "projects.html", "style.css"]
        for file_name in required_files:
            file_path = html_dir / file_name
            if not file_path.exists():
                print(f"❌ Missing HTML file: {file_name}")
                return False
            if file_path.stat().st_size == 0:
                print(f"❌ Empty HTML file: {file_name}")
                return False
                
        print("✅ HTML export successful")
        
        # Test JSON-LD export  
        print("Testing JSON-LD export...")
        jsonld_file = temp_path / "test.jsonld"
        exporter.export_json_ld(jsonld_file)
        
        if not jsonld_file.exists():
            print("❌ JSON-LD file not created")
            return False
            
        # Validate JSON-LD structure
        with open(jsonld_file, 'r') as f:
            try:
                data = json.load(f)
                if "@context" not in data:
                    print("❌ JSON-LD missing @context")
                    return False
                if "@graph" not in data:
                    print("❌ JSON-LD missing @graph")
                    return False
                if "_export_metadata" not in data:
                    print("❌ JSON-LD missing export metadata")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON-LD: {e}")
                return False
                
        print("✅ JSON-LD export successful")
        
        # Check that exports contain actual data
        with open(html_dir / "index.html", 'r') as f:
            html_content = f.read()
            if "task_001" not in html_content:
                print("❌ HTML export missing expected task data")
                return False
                
        print("✅ HTML export contains expected data")
        
        print("✅ All tests passed!")
        return True

if __name__ == "__main__":
    success = test_exports()
    exit(0 if success else 1)