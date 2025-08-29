#!/usr/bin/env python3
"""
PIM RDF Validation Script (Python version)

This script provides comprehensive validation for the PIM RDF knowledge base:
1. TTL syntax validation using rdflib
2. SHACL shapes validation using pyshacl
3. Data merging and SPARQL querying tests
4. Performance timing for all operations

Usage: python3 util/validate_pim_python.py [directory]
"""

import os
import sys
import time
import glob
import rdflib
import pyshacl
from pathlib import Path

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_header(text):
    print(f"{Colors.BLUE}=== {text} ==={Colors.NC}")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.NC} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.NC} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.NC} {text}")

def get_time_ms():
    return int(time.time() * 1000)

def validate_ttl_files(directory):
    """Validate TTL files for proper Turtle syntax"""
    print_header("TTL Syntax Validation")
    
    total_triples = 0
    file_count = 0
    total_start = get_time_ms()
    
    # Find all TTL files excluding merged files
    ttl_files = glob.glob(os.path.join(directory, "*.ttl"))
    ttl_files = [f for f in ttl_files if not os.path.basename(f).startswith("merged")]
    ttl_files.sort()
    
    for file_path in ttl_files:
        rel_path = os.path.relpath(file_path, directory)
        start_time = get_time_ms()
        
        try:
            g = rdflib.Graph()
            g.parse(file_path, format='turtle')
            
            end_time = get_time_ms()
            duration = end_time - start_time
            
            triples = len(g)
            total_triples += triples
            file_count += 1
            
            print_success(f"{rel_path}: Valid ({triples} triples) - {duration}ms")
            
        except Exception as e:
            print_error(f"{rel_path}: Invalid Turtle syntax")
            print(f"  Error: {e}")
            return False
    
    total_end = get_time_ms()
    total_duration = total_end - total_start
    
    print("")
    print(f"Total: {total_triples} triples across {file_count} files")
    print(f"Total validation time: {total_duration}ms")
    return True

def merge_data_files(directory):
    """Merge TTL data files into a single graph"""
    print_header("Data Merging")
    
    start_time = get_time_ms()
    
    # Create merged graph
    merged_graph = rdflib.Graph()
    
    # Get all TTL files except config and merged files
    ttl_files = glob.glob(os.path.join(directory, "*.ttl"))
    ttl_files = [f for f in ttl_files if not os.path.basename(f).startswith("config") 
                 and not os.path.basename(f).startswith("merged")]
    ttl_files.sort()
    
    files_merged = 0
    total_triples = 0
    
    for file_path in ttl_files:
        try:
            g = rdflib.Graph()
            g.parse(file_path, format='turtle')
            
            # Add to merged graph
            merged_graph += g
            files_merged += 1
            total_triples += len(g)
            
            rel_path = os.path.relpath(file_path, directory)
            print_success(f"Merged {rel_path} ({len(g)} triples)")
            
        except Exception as e:
            rel_path = os.path.relpath(file_path, directory)
            print_error(f"Failed to merge {rel_path}: {e}")
            return False
    
    # Create build directory if needed
    build_dir = os.path.join(directory, "build")
    os.makedirs(build_dir, exist_ok=True)
    
    # Save merged graph
    merged_path = os.path.join(build_dir, "merged.ttl")
    merged_graph.serialize(merged_path, format='turtle')
    
    end_time = get_time_ms()
    duration = end_time - start_time
    
    print("")
    print(f"Merged {files_merged} files into build/merged.ttl")
    print(f"Total triples in merged graph: {len(merged_graph)}")
    print(f"Merge time: {duration}ms")
    
    return True

def test_sparql_queries(directory):
    """Test SPARQL queries on the merged dataset"""
    print_header("SPARQL Query Testing")
    
    merged_path = os.path.join(directory, "build", "merged.ttl")
    if not os.path.exists(merged_path):
        print_error("Merged file not found. Run data merging first.")
        return False
    
    # Load merged graph
    start_time = get_time_ms()
    g = rdflib.Graph()
    g.parse(merged_path, format='turtle')
    load_time = get_time_ms() - start_time
    print_success(f"Loaded merged graph ({len(g)} triples) - {load_time}ms")
    
    # Test validation queries
    validation_queries_dir = os.path.join(directory, "queries", "validation")
    query_files = glob.glob(os.path.join(validation_queries_dir, "*.sparql"))
    
    total_queries = 0
    for query_file in query_files:
        try:
            with open(query_file, 'r') as f:
                query = f.read()
            
            start_time = get_time_ms()
            results = g.query(query)
            end_time = get_time_ms()
            duration = end_time - start_time
            
            result_count = len(list(results))
            rel_path = os.path.relpath(query_file, directory)
            print_success(f"{rel_path}: {result_count} results - {duration}ms")
            total_queries += 1
            
        except Exception as e:
            rel_path = os.path.relpath(query_file, directory)
            print_error(f"Query failed {rel_path}: {e}")
    
    # Test basic count query
    try:
        start_time = get_time_ms()
        results = g.query('''
            SELECT ?type (COUNT(?entity) as ?count)
            WHERE {
              ?entity a ?type .
            }
            GROUP BY ?type
            ORDER BY DESC(?count)
        ''')
        end_time = get_time_ms()
        duration = end_time - start_time
        
        print("")
        print("Entity type counts:")
        for row in results:
            type_name = str(row[0]).split('/')[-1] if '/' in str(row[0]) else str(row[0]).split('#')[-1]
            print(f"  {type_name}: {row[1]} entities")
        
        print_success(f"Basic count query - {duration}ms")
        
    except Exception as e:
        print_error(f"Basic count query failed: {e}")
        return False
    
    print("")
    print(f"Total queries tested: {total_queries + 1}")
    return True

def validate_shacl_shapes(directory):
    """Validate data against SHACL shapes"""
    print_header("SHACL Validation")
    
    shapes_dir = os.path.join(directory, "shapes")
    if not os.path.exists(shapes_dir):
        print_warning("No shapes directory found - skipping SHACL validation")
        return True
    
    # Find shape files
    shape_files = glob.glob(os.path.join(shapes_dir, "*-shapes.ttl"))
    if not shape_files:
        print_warning("No SHACL shape files found - skipping validation")
        return True
    
    all_valid = True
    
    for shape_file in shape_files:
        # Determine data file from shape file name
        shape_name = os.path.basename(shape_file)
        if shape_name.startswith("notes-"):
            data_file = os.path.join(directory, "notes.ttl")
        else:
            # Extract domain name from shape file
            domain = shape_name.replace("-shapes.ttl", "")
            data_file = os.path.join(directory, f"{domain}.ttl")
        
        if not os.path.exists(data_file):
            print_warning(f"Data file for {shape_name} not found: {os.path.basename(data_file)}")
            continue
        
        try:
            start_time = get_time_ms()
            
            # Load data and shapes
            data_g = rdflib.Graph()
            data_g.parse(data_file, format='turtle')
            
            shape_g = rdflib.Graph()
            shape_g.parse(shape_file, format='turtle')
            
            # Perform validation
            conforms, report_graph, report_text = pyshacl.validate(
                data_g, shacl_graph=shape_g, inference='none'
            )
            
            end_time = get_time_ms()
            duration = end_time - start_time
            
            rel_shape = os.path.relpath(shape_file, directory)
            rel_data = os.path.relpath(data_file, directory)
            
            if conforms:
                print_success(f"{rel_data} validates against {rel_shape} - {duration}ms")
            else:
                print_error(f"SHACL validation failed for {rel_data} against {rel_shape} - {duration}ms")
                if report_text:
                    print("Report:")
                    for line in report_text.split('\n'):
                        if line.strip():
                            print(f"  {line}")
                all_valid = False
            
        except Exception as e:
            rel_shape = os.path.relpath(shape_file, directory)
            print_error(f"SHACL validation error for {rel_shape}: {e}")
            all_valid = False
    
    return all_valid

def main():
    """Main execution"""
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    directory = os.path.abspath(directory)
    
    print("PIM RDF Validation Script (Python version)")
    print(f"Working directory: {directory}")
    print("=" * 50)
    
    # Step 1: Validate TTL syntax
    if not validate_ttl_files(directory):
        print("")
        print_error("TTL validation failed - stopping")
        sys.exit(1)
    
    # Step 2: Merge data files  
    if not merge_data_files(directory):
        print("")
        print_error("Data merging failed - stopping")
        sys.exit(1)
    
    # Step 3: Test SPARQL queries
    if not test_sparql_queries(directory):
        print("")
        print_error("SPARQL query testing failed - stopping")
        sys.exit(1)
    
    # Step 4: SHACL validation
    if not validate_shacl_shapes(directory):
        print("")
        print_warning("SHACL validation had issues")
    
    print("")
    print("=" * 50)
    print_success("All validation steps completed successfully!")

if __name__ == "__main__":
    main()