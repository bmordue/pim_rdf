#!/usr/bin/env python3
"""
Simple test script for Google Takeout ingestion functionality.
This script validates the basic ingestion and RDF generation functionality.
"""

import os
import tempfile
import zipfile
from pathlib import Path
import rdflib

def create_test_takeout_archive():
    """Create a minimal test Google Takeout archive."""
    temp_dir = Path(tempfile.mkdtemp(prefix="test_takeout_"))
    
    # Create test vCard content
    vcf_content = """BEGIN:VCARD
VERSION:3.0
FN:Test User
EMAIL:test@example.com
END:VCARD"""
    
    # Create test iCalendar content  
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0

BEGIN:VEVENT
SUMMARY:Test Event
DTSTART:20250915T100000Z
LOCATION:Test Location
END:VEVENT

END:VCALENDAR"""
    
    # Create test location data
    location_dir = temp_dir / "Location History"
    location_dir.mkdir(parents=True)
    
    json_content = """{
  "locations": [
    {
      "timestampMs": "1640995200000",
      "latitudeE7": 514874900,
      "longitudeE7": -114161,
      "name": "Test Place"
    }
  ]
}"""
    
    # Write test files
    (temp_dir / "contacts.vcf").write_text(vcf_content)
    (temp_dir / "calendar.ics").write_text(ics_content) 
    (location_dir / "history.json").write_text(json_content)
    
    # Create ZIP archive
    zip_path = temp_dir.parent / "test_takeout.zip"
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(temp_dir)
                zf.write(file_path, arc_path)
    
    return zip_path

def test_ingestion():
    """Test the complete ingestion process."""
    print("=== Testing Google Takeout Ingestion ===")
    
    # Create test archive
    test_archive = create_test_takeout_archive()
    print(f"Created test archive: {test_archive}")
    
    # Import the ingestion module
    import sys
    sys.path.append('util')
    
    try:
        from ingest_takeout import TakeoutIngestion
        
        # Create temporary output directory
        output_dir = Path(tempfile.mkdtemp(prefix="test_output_"))
        
        # Run ingestion
        ingestion = TakeoutIngestion(str(test_archive), str(output_dir))
        output_files = ingestion.ingest()
        
        print(f"Generated {len(output_files)} output files:")
        for data_type, file_path in output_files.items():
            print(f"  {data_type}: {file_path}")
        
        # Validate each generated file
        total_triples = 0
        for data_type, file_path in output_files.items():
            if os.path.exists(file_path):
                try:
                    graph = rdflib.Graph()
                    graph.parse(file_path, format='turtle')
                    triple_count = len(graph)
                    total_triples += triple_count
                    print(f"✓ {file_path}: {triple_count} triples")
                except Exception as e:
                    print(f"✗ {file_path}: Failed to parse - {e}")
                    return False
            else:
                print(f"✗ {file_path}: File not found")
                return False
        
        print(f"✓ Total triples generated: {total_triples}")
        print("✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    
    finally:
        # Cleanup
        if test_archive.exists():
            os.remove(test_archive)
        if test_archive.parent.exists():
            import shutil
            shutil.rmtree(test_archive.parent)

if __name__ == "__main__":
    # Change to repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    os.chdir(repo_root)
    
    success = test_ingestion()
    exit(0 if success else 1)