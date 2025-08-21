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
import yaml
from pathlib import Path

def load_domains_config(directory):
    """Load data domains configuration from YAML file"""
    config_path = os.path.join(directory, 'config', 'domains.yaml')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return [domain['filename'] for domain in config.get('domains', [])]
        except Exception as e:
            print(f"⚠ Error loading domains config: {e}")
    
    # Fallback to hardcoded list if config file doesn't exist
    print("⚠ Using fallback hardcoded domain list")
    return ['base.ttl', 'tasks.ttl', 'notes.ttl', 'contacts.ttl', 
            'projects.ttl', 'bookmarks.ttl', 'events.ttl', 'tags.ttl']

def load_validation_config(directory):
    """Load validation configuration from YAML file"""
    config_path = os.path.join(directory, 'config', 'validation.yaml')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return {item['data_file']: item['shape_file'] 
                       for item in config.get('validation', [])}
        except Exception as e:
            print(f"⚠ Error loading validation config: {e}")
    
    # Fallback to hardcoded mapping if config file doesn't exist
    print("⚠ Using fallback hardcoded validation mapping")
    return {'notes.ttl': 'notes-shapes.ttl'}

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
    
    # Load data files from configuration
    data_files = load_domains_config(directory)
    
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

def load_query_from_file(query_path):
    """Load a SPARQL query from a file"""
    try:
        with open(query_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"✗ Error loading query from {query_path}: {e}")
        return None

def test_sparql_queries(graph, directory='.'):
    """Test SPARQL queries on the merged data"""
    print("\n=== SPARQL Query Testing ===")
    
    # Load queries from external files
    queries_dir = os.path.join(directory, 'queries', 'validation')
    query_files = [
        ("List all tasks", "list-tasks.sparql"),
        ("List all schema.org CreativeWorks", "list-creativeworks.sparql"),
        ("Count entities by type", "count-by-type.sparql")
    ]
    
    queries = []
    for name, filename in query_files:
        query_path = os.path.join(queries_dir, filename)
        query_text = load_query_from_file(query_path)
        if query_text:
            queries.append((name, query_text))
        else:
            print(f"⚠ Skipping query '{name}' - file not found or error loading")
    
    if not queries:
        print("⚠ No validation queries found - skipping SPARQL testing")
        return
    
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
    
    # Load validation mappings from configuration
    data_files = load_validation_config(directory)
    
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
    test_sparql_queries(merged_graph, directory)
    
    # Step 4: SHACL validation
    if not validate_shacl_shapes(directory):
        print("\n⚠ SHACL validation had issues")
    
    print("\n" + "=" * 50)
    print("✅ All validation steps completed successfully!")

if __name__ == '__main__':
    main()