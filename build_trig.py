#!/usr/bin/env python3
"""
Build script to merge individual TriG files into a single TriG file for querying.
Each domain remains in its own named graph for clear per-file boundaries.
"""

import rdflib
import os
import sys

def merge_trig_files():
    """Merge all .trig files into a single merged.trig file."""
    
    # Create a dataset to hold all named graphs
    dataset = rdflib.Dataset()
    
    # Find all .trig files in current directory
    trig_files = [f for f in os.listdir('.') if f.endswith('.trig')]
    trig_files.sort()  # For consistent ordering
    
    print(f"Merging {len(trig_files)} TriG files...")
    
    for filename in trig_files:
        print(f"  Adding {filename}...")
        try:
            # Parse each TriG file and add to dataset
            dataset.parse(filename, format='trig')
        except Exception as e:
            print(f"  Error parsing {filename}: {e}")
            return False
    
    # Create output directory if it doesn't exist
    os.makedirs('build', exist_ok=True)
    
    # Serialize to merged TriG file
    output_file = 'build/merged.trig'
    with open(output_file, 'w') as f:
        f.write(dataset.serialize(format='trig'))
    
    # Count total quads and graphs
    total_quads = sum(1 for _ in dataset.quads())
    graph_count = len(list(dataset.contexts()))
    
    print(f"✓ Created {output_file}")
    print(f"  Total quads: {total_quads}")
    print(f"  Named graphs: {graph_count}")
    
    # List all named graphs
    print("  Graph URIs:")
    for context in dataset.contexts():
        quad_count = sum(1 for _ in dataset.quads((None, None, None, context)))
        print(f"    {context.identifier} ({quad_count} quads)")
    
    return True

if __name__ == '__main__':
    if merge_trig_files():
        print("Build completed successfully!")
        sys.exit(0)
    else:
        print("Build failed!")
        sys.exit(1)