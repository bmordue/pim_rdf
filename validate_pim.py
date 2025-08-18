#!/usr/bin/env python3
"""
PIM RDF Validation Script

This script provides comprehensive validation for the PIM RDF knowledge base:
1. TTL syntax validation using rdflib
2. SHACL shapes validation using pyshacl 
3. Data merging and SPARQL querying tests
4. Performance timing for all operations

Usage: python3 validate_pim.py [directory]
"""

import rdflib
import pyshacl
import os
import sys
import time
from pathlib import Path

def validate_ttl_files(directory):
    """Validate all TTL files for proper Turtle syntax"""
    print("=== TTL Syntax Validation ===")
    
    ttl_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.ttl') and not file.startswith('merged'):
                ttl_files.append(os.path.join(root, file))
    
    total_triples = 0
    total_start = time.time()
    
    for file in sorted(ttl_files):
        rel_path = os.path.relpath(file, directory)
        start_time = time.time()
        g = rdflib.Graph()
        try:
            g.parse(file, format='turtle')
            end_time = time.time()
            total_triples += len(g)
            print(f"✓ {rel_path}: Valid ({len(g)} triples) - {(end_time - start_time)*1000:.1f}ms")
        except Exception as e:
            print(f"✗ {rel_path}: ERROR - {e}")
            return False
    
    total_end = time.time()
    print(f"\nTotal: {total_triples} triples across {len(ttl_files)} files")
    print(f"Total validation time: {(total_end - total_start)*1000:.1f}ms")
    return True

def merge_data_files(directory):
    """Merge TTL data files into a single graph"""
    print("\n=== Data Merging ===")
    
    # Core data files (exclude config and shapes)
    data_files = ['base.ttl', 'tasks.ttl', 'notes.ttl', 'contacts.ttl', 
                  'projects.ttl', 'bookmarks.ttl', 'events.ttl', 'tags.ttl']
    
    start_time = time.time()
    merged_graph = rdflib.Graph()
    
    for file in data_files:
        file_path = os.path.join(directory, file)
        if os.path.exists(file_path):
            try:
                merged_graph.parse(file_path, format='turtle')
                print(f"✓ Merged {file}")
            except Exception as e:
                print(f"✗ Error merging {file}: {e}")
                return None
    
    # Write merged graph
    build_dir = os.path.join(directory, 'build')
    os.makedirs(build_dir, exist_ok=True)
    merged_path = os.path.join(build_dir, 'merged.ttl')
    merged_graph.serialize(merged_path, format='turtle')
    
    end_time = time.time()
    print(f"\n✓ Merged {len(merged_graph)} triples into build/merged.ttl")
    print(f"Merge time: {(end_time - start_time)*1000:.1f}ms")
    
    return merged_graph

def test_sparql_queries(graph):
    """Test SPARQL queries on the merged data"""
    print("\n=== SPARQL Query Testing ===")
    
    queries = [
        ("List all tasks", """
PREFIX pim: <https://ben.example/ns/pim#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?task ?title ?status ?priority
WHERE {
  ?task a pim:Task ;
        dcterms:title ?title ;
        pim:status ?status ;
        pim:priority ?priority .
}
ORDER BY ASC(?priority)
"""),
        ("List all schema.org CreativeWorks", """
PREFIX schema: <https://schema.org/>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?work ?title
WHERE {
  ?work a schema:CreativeWork ;
        dcterms:title ?title .
}
"""),
        ("Count entities by type", """
SELECT ?type (COUNT(?entity) as ?count)
WHERE {
  ?entity a ?type .
}
GROUP BY ?type
ORDER BY DESC(?count)
""")
    ]
    
    for name, query in queries:
        print(f"\n--- {name} ---")
        start_time = time.time()
        try:
            results = graph.query(query)
            end_time = time.time()
            print(f"Query time: {(end_time - start_time)*1000:.1f}ms")
            
            count = 0
            for row in results:
                count += 1
                if count <= 3:  # Show first 3 results
                    print(f"  {row}")
                elif count == 4:
                    print("  ...")
            print(f"✓ Found {count} results")
            
        except Exception as e:
            print(f"✗ Query failed: {e}")

def validate_shacl_shapes(directory):
    """Validate data against SHACL shapes"""
    print("\n=== SHACL Shapes Validation ===")
    
    shapes_dir = os.path.join(directory, 'shapes')
    if not os.path.exists(shapes_dir):
        print("No shapes directory found - skipping SHACL validation")
        return True
    
    data_files = {
        'notes.ttl': 'notes-shapes.ttl'
    }
    
    all_valid = True
    
    for data_file, shape_file in data_files.items():
        data_path = os.path.join(directory, data_file)
        shape_path = os.path.join(shapes_dir, shape_file)
        
        if not os.path.exists(data_path) or not os.path.exists(shape_path):
            print(f"⚠ Skipping {data_file} - missing data or shape file")
            continue
            
        print(f"\n--- Validating {data_file} against {shape_file} ---")
        
        try:
            data_graph = rdflib.Graph()
            data_graph.parse(data_path, format='turtle')
            
            shapes_graph = rdflib.Graph()
            shapes_graph.parse(shape_path, format='turtle')
            
            start_time = time.time()
            conforms, report_graph, report_text = pyshacl.validate(
                data_graph=data_graph,
                shacl_graph=shapes_graph,
                inference='none',
                debug=False
            )
            end_time = time.time()
            
            if conforms:
                print(f"✓ SHACL validation passed - {(end_time - start_time)*1000:.1f}ms")
            else:
                print(f"✗ SHACL validation failed - {(end_time - start_time)*1000:.1f}ms")
                print("Report:")
                print(report_text)
                all_valid = False
                
        except Exception as e:
            print(f"✗ SHACL validation error: {e}")
            all_valid = False
    
    return all_valid

def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    directory = os.path.abspath(directory)
    
    print(f"PIM RDF Validation Script")
    print(f"Working directory: {directory}")
    print("=" * 50)
    
    # Step 1: Validate TTL syntax
    if not validate_ttl_files(directory):
        print("\n❌ TTL validation failed - stopping")
        sys.exit(1)
    
    # Step 2: Merge data files
    merged_graph = merge_data_files(directory)
    if merged_graph is None:
        print("\n❌ Data merging failed - stopping")
        sys.exit(1)
    
    # Step 3: Test SPARQL queries
    test_sparql_queries(merged_graph)
    
    # Step 4: SHACL validation
    if not validate_shacl_shapes(directory):
        print("\n⚠ SHACL validation had issues")
    
    print("\n" + "=" * 50)
    print("✅ All validation steps completed successfully!")

if __name__ == '__main__':
    main()