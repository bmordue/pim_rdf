#!/usr/bin/env python3
"""
ICS Bridge - Generate .ics files from events.ttl for calendar interoperability

This script reads RDF event data from Turtle files and converts it to the
standard iCalendar (.ics) format for use with calendar applications.
"""

import argparse
import sys
from datetime import datetime, timezone
import rdflib
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, DCTERMS, XSD


def create_ics_content(events_data):
    """Generate ICS content from events data."""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//PIM RDF//ICS Bridge//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    
    for event in events_data:
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{event['uid']}",
        ])
        
        # Handle date/datetime formatting
        if event.get('is_datetime', False):
            lines.append(f"DTSTART:{event['date']}")
        else:
            lines.append(f"DTSTART;VALUE=DATE:{event['date']}")
        
        lines.append(f"SUMMARY:{event['title']}")
        
        if event.get('location'):
            lines.append(f"LOCATION:{event['location']}")
        
        if event.get('description'):
            lines.append(f"DESCRIPTION:{event['description']}")
            
        # Add creation timestamp
        now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        lines.append(f"DTSTAMP:{now}")
        lines.append(f"CREATED:{now}")
        
        lines.append("END:VEVENT")
    
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def extract_events_from_rdf(graph, base_namespace):
    """Extract event data from RDF graph."""
    events = []
    
    # Define namespaces
    BASE = Namespace(base_namespace)
    
    # Query for events
    event_query = """
    PREFIX : <%s>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT ?event ?title ?date ?location ?tag
    WHERE {
        ?event a :Event .
        OPTIONAL { ?event dcterms:title ?title }
        OPTIONAL { ?event :date ?date }
        OPTIONAL { ?event :location ?location }
        OPTIONAL { ?event :hasTag ?tag }
    }
    """ % base_namespace
    
    results = graph.query(event_query)
    
    # Group results by event
    event_dict = {}
    for row in results:
        event_uri = str(row.event)
        if event_uri not in event_dict:
            event_dict[event_uri] = {
                'uri': event_uri,
                'title': '',
                'date': '',
                'location': '',
                'tags': []
            }
        
        if row.title:
            event_dict[event_uri]['title'] = str(row.title)
        if row.date:
            # Convert date to ICS format
            date_str = str(row.date)
            if 'T' in date_str:
                # DateTime format: convert to YYYYMMDDTHHMMSSZ
                # Parse and reformat properly
                if '+' in date_str:
                    # Handle timezone offsets
                    dt_part = date_str.split('+')[0]
                    if 'Z' not in date_str:
                        dt_part += 'Z'
                else:
                    dt_part = date_str
                    if not dt_part.endswith('Z'):
                        dt_part += 'Z'
                
                # Remove separators for ICS format
                formatted_dt = dt_part.replace('-', '').replace(':', '')
                event_dict[event_uri]['date'] = formatted_dt
                event_dict[event_uri]['is_datetime'] = True
            else:
                # Date only format: convert to YYYYMMDD
                event_dict[event_uri]['date'] = date_str.replace('-', '')
                event_dict[event_uri]['is_datetime'] = False
        if row.location:
            event_dict[event_uri]['location'] = str(row.location)
        if row.tag:
            tag_name = str(row.tag).split('/')[-1].replace('-', ' ').title()
            if tag_name not in event_dict[event_uri]['tags']:
                event_dict[event_uri]['tags'].append(tag_name)
    
    # Convert to list and add UIDs
    for event_uri, event_data in event_dict.items():
        # Generate UID from event URI
        uid = event_uri.replace('https://', '').replace('http://', '').replace('/', '-')
        event_data['uid'] = uid
        
        # Add tags as description if available
        if event_data['tags']:
            event_data['description'] = f"Tags: {', '.join(event_data['tags'])}"
        
        events.append(event_data)
    
    return events


def main():
    parser = argparse.ArgumentParser(
        description="Generate ICS calendar files from RDF event data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ics_bridge.py events.ttl -o calendar.ics
  python3 ics_bridge.py events.ttl --output calendar.ics
  python3 ics_bridge.py events.ttl > calendar.ics
        """
    )
    
    parser.add_argument('input_file', help='Input Turtle (.ttl) file containing events')
    parser.add_argument('-o', '--output', help='Output ICS file (default: stdout)')
    parser.add_argument('--base-namespace', 
                      default='https://ben.example/pim/',
                      help='Base namespace for RDF data (default: https://ben.example/pim/)')
    
    args = parser.parse_args()
    
    try:
        # Load RDF graph
        graph = Graph()
        graph.parse(args.input_file, format='turtle')
        print(f"Loaded {len(graph)} triples from {args.input_file}", file=sys.stderr)
        
        # Extract events
        events = extract_events_from_rdf(graph, args.base_namespace)
        print(f"Found {len(events)} events", file=sys.stderr)
        
        if not events:
            print("Warning: No events found in the RDF data", file=sys.stderr)
            return 1
        
        # Generate ICS content
        ics_content = create_ics_content(events)
        
        # Output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(ics_content)
            print(f"ICS calendar written to {args.output}", file=sys.stderr)
        else:
            print(ics_content, end='')
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())