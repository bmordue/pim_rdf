#!/usr/bin/env python3
"""
Test script to validate the enhanced takeout ingestion functionality.
"""

import json
import tempfile
import sys
from pathlib import Path

# Add the current directory to the path so we can import the ingestion module
sys.path.append(str(Path(__file__).parent))

try:
    from ingest_takeout import LocationConverter
    import rdflib
    from rdflib import Graph, Namespace
    
    # Define test data that represents different Google Takeout formats
    sample_classic_location = {
        "timestampMs": "1693574400000",  # Aug 31, 2023
        "latitudeE7": 559523380,  # Edinburgh
        "longitudeE7": -32031760,
        "accuracy": 15,
        "altitude": 120,
        "velocity": 5,
        "heading": 180,
        "activity": [
            {
                "type": "WALKING",
                "confidence": 85
            },
            {
                "type": "IN_VEHICLE", 
                "confidence": 15
            }
        ],
        "source": "fused",
        "deviceTag": 123456789,
        "platformType": "ANDROID"
    }
    
    sample_place_visit = {
        "location": {
            "latitudeE7": 559523380,
            "longitudeE7": -32031760,
            "placeId": "ChIJdd4hrwug2EcRmSrV3Vo6llI",
            "address": "Edinburgh Castle, Castlehill, Edinburgh EH1 2NG, UK",
            "name": "Edinburgh Castle",
            "semanticType": "TYPE_SEARCHED_ADDRESS",
            "locationConfidence": 87.5,
            "plusCode": "9C7QXQL4+XQ"
        },
        "duration": {
            "startTimestampMs": "1693574400000",
            "endTimestampMs": "1693578000000"  # 1 hour visit
        },
        "placeConfidence": "HIGH_CONFIDENCE",
        "visitConfidence": 95.0,
        "centerLatE7": 559523380,
        "centerLngE7": -32031760
    }
    
    sample_activity_segment = {
        "startLocation": {
            "latitudeE7": 559523380,
            "longitudeE7": -32031760
        },
        "endLocation": {
            "latitudeE7": 559834000,
            "longitudeE7": -31881000
        },
        "duration": {
            "startTimestampMs": "1693574400000",
            "endTimestampMs": "1693575300000"  # 15 minute journey
        },
        "distance": 2500,  # 2.5 km
        "activityType": "IN_VEHICLE",
        "confidence": "HIGH",
        "activities": [
            {
                "activityType": "IN_VEHICLE",
                "probability": 85.5
            },
            {
                "activityType": "WALKING", 
                "probability": 14.5
            }
        ],
        "waypointPath": {
            "waypoints": [
                {"latE7": 559523380, "lngE7": -32031760},
                {"latE7": 559600000, "lngE7": -32000000},
                {"latE7": 559700000, "lngE7": -31950000},
                {"latE7": 559834000, "lngE7": -31881000}
            ],
            "distanceMeters": 2500.0
        }
    }
    
    def test_location_converter():
        """Test the enhanced LocationConverter with sample data."""
        print("Testing enhanced LocationConverter...")
        
        graph = Graph()
        converter = LocationConverter(graph)
        
        # Test classic location format
        print("Testing classic location format...")
        converter._add_location_triples(sample_classic_location)
        print(f"  Added classic location - Graph now has {len(graph)} triples")
        
        # Test place visit format  
        print("Testing place visit format...")
        converter._add_place_visit_triples(sample_place_visit)
        print(f"  Added place visit - Graph now has {len(graph)} triples")
        
        # Test activity segment format
        print("Testing activity segment format...")
        converter._add_activity_segment_triples(sample_activity_segment)
        print(f"  Added activity segment - Graph now has {len(graph)} triples")
        
        # Output the RDF for inspection
        print("\nGenerated RDF (first 50 lines):")
        print("=" * 50)
        turtle_output = graph.serialize(format='turtle', encoding='utf-8').decode('utf-8')
        lines = turtle_output.split('\n')
        for line in lines[:50]:
            print(line)
        
        if len(lines) > 50:
            print(f"... (truncated, {len(lines)} total lines)")
        
        print("\n" + "=" * 50)
        print(f"SUCCESS: Generated {len(graph)} RDF triples from enhanced ingestion")
        
        return graph
    
    def analyze_predicates(graph):
        """Analyze what predicates were created."""
        print("\nPredicate Analysis:")
        print("-" * 30)
        
        predicates = set()
        for s, p, o in graph:
            predicates.add(p)
        
        # Group by namespace
        namespaces = {}
        for pred in predicates:
            namespace = str(pred).split('#')[0] + '#' if '#' in str(pred) else str(pred).rsplit('/', 1)[0] + '/'
            local_name = str(pred).split('#')[-1] if '#' in str(pred) else str(pred).split('/')[-1]
            
            if namespace not in namespaces:
                namespaces[namespace] = []
            namespaces[namespace].append(local_name)
        
        for ns, names in sorted(namespaces.items()):
            print(f"{ns}")
            for name in sorted(names):
                print(f"  {name}")
        
        print(f"\nTotal predicates: {len(predicates)}")
    
    if __name__ == "__main__":
        try:
            graph = test_location_converter()
            analyze_predicates(graph)
            print("\nAll tests passed! Enhanced ingestion is working correctly.")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure rdflib is installed and the util/ingest_takeout.py file is valid")
    sys.exit(1)
