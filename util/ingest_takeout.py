#!/usr/bin/env python3
"""
Google Takeout Ingestion Script for PIM RDF

This script parses a Google Takeout archive and converts the data into RDF format
suitable for inclusion in the PIM RDF store. It handles the core data types:
- Contacts (vCard format) -> foaf:Person entities
- Calendar Events (iCalendar format) -> ical:Vevent entities  
- Location History (JSON format) -> pim:Place entities

Usage:
    python3 util/ingest_takeout.py /path/to/takeout-archive.zip
"""

import argparse
import json
import os
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

import rdflib
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import FOAF, DCTERMS, XSD, RDF, RDFS

# Define namespaces
PIM = Namespace("https://ben.example/pim/")
PIMNS = Namespace("https://ben.example/ns/pim#")
ICAL = Namespace("http://www.w3.org/2002/12/cal/ical#")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")


class TakeoutIngestionError(Exception):
    """Base exception for takeout ingestion errors."""
    pass


class TakeoutExtractor:
    """Handles extraction and file discovery from Google Takeout archives."""
    
    def __init__(self, archive_path: str):
        self.archive_path = Path(archive_path)
        if not self.archive_path.exists():
            raise TakeoutIngestionError(f"Archive file not found: {archive_path}")
    
    def extract_to_temp(self) -> Path:
        """Extract the takeout archive to a temporary directory."""
        temp_dir = Path(tempfile.mkdtemp(prefix="takeout_"))
        
        try:
            with zipfile.ZipFile(self.archive_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                print(f"Extracted archive to: {temp_dir}")
                return temp_dir
        except zipfile.BadZipFile:
            raise TakeoutIngestionError(f"Invalid ZIP file: {self.archive_path}")
    
    def find_data_files(self, extracted_dir: Path) -> Dict[str, List[Path]]:
        """Find relevant data files in the extracted archive."""
        data_files = {
            'contacts': [],
            'calendar': [],
            'location': []
        }
        
        # Walk through the extracted directory
        for root, dirs, files in os.walk(extracted_dir):
            root_path = Path(root)
            
            for file in files:
                file_path = root_path / file
                file_lower = file.lower()
                
                # Find contacts (vCard files)
                if file_lower.endswith('.vcf'):
                    data_files['contacts'].append(file_path)
                
                # Find calendar events (iCalendar files)
                elif file_lower.endswith('.ics'):
                    data_files['calendar'].append(file_path)
                
                # Find location history (JSON files)
                elif 'location' in str(root_path).lower() and file_lower.endswith('.json'):
                    data_files['location'].append(file_path)
        
        return data_files


class ContactsConverter:
    """Converts Google Contacts (vCard) to RDF."""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.contact_counter = 1
    
    def parse_vcard_simple(self, vcard_content: str) -> List[Dict]:
        """Simple vCard parser for basic contact information."""
        contacts = []
        current_contact = {}
        
        lines = vcard_content.strip().split('\n')
        for line in lines:
            line = line.strip()
            
            if line == 'BEGIN:VCARD':
                current_contact = {}
            elif line == 'END:VCARD':
                if current_contact:
                    contacts.append(current_contact.copy())
            elif ':' in line:
                key, value = line.split(':', 1)
                # Handle simple properties
                if key == 'FN':
                    current_contact['name'] = value
                elif key == 'EMAIL':
                    current_contact['email'] = value
                elif key.startswith('EMAIL;'):
                    current_contact['email'] = value
        
        return contacts
    
    def convert_to_rdf(self, vcf_files: List[Path]) -> None:
        """Convert vCard files to RDF triples."""
        for vcf_file in vcf_files:
            try:
                with open(vcf_file, 'r', encoding='utf-8') as f:
                    vcard_content = f.read()
                
                contacts = self.parse_vcard_simple(vcard_content)
                
                for contact in contacts:
                    if 'name' in contact:
                        self._add_contact_triples(contact)
                        
            except Exception as e:
                print(f"Warning: Failed to parse {vcf_file}: {e}")
    
    def _add_contact_triples(self, contact: Dict) -> None:
        """Add RDF triples for a single contact."""
        contact_id = f"contact-takeout-{self.contact_counter:03d}"
        contact_uri = PIM[contact_id]
        
        # Basic contact information
        self.graph.add((contact_uri, RDF.type, FOAF.Person))
        self.graph.add((contact_uri, RDFS.label, Literal(contact['name'])))
        
        if 'email' in contact:
            email_uri = URIRef(f"mailto:{contact['email']}")
            self.graph.add((contact_uri, FOAF.mbox, email_uri))
        
        # Add metadata
        self.graph.add((contact_uri, DCTERMS.created, 
                       Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        self.graph.add((contact_uri, DCTERMS.source, 
                       Literal("Google Takeout - Contacts")))
        
        self.contact_counter += 1


class CalendarConverter:
    """Converts Google Calendar (iCalendar) to RDF."""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.event_counter = 1
    
    def parse_icalendar_simple(self, ical_content: str) -> List[Dict]:
        """Simple iCalendar parser for basic event information."""
        events = []
        current_event = {}
        
        lines = ical_content.strip().split('\n')
        for line in lines:
            line = line.strip()
            
            if line == 'BEGIN:VEVENT':
                current_event = {}
            elif line == 'END:VEVENT':
                if current_event:
                    events.append(current_event.copy())
            elif ':' in line:
                key, value = line.split(':', 1)
                # Handle simple properties
                if key == 'SUMMARY':
                    current_event['title'] = value
                elif key == 'DTSTART':
                    current_event['start'] = value
                elif key == 'LOCATION':
                    current_event['location'] = value
        
        return events
    
    def convert_to_rdf(self, ics_files: List[Path]) -> None:
        """Convert iCalendar files to RDF triples."""
        for ics_file in ics_files:
            try:
                with open(ics_file, 'r', encoding='utf-8') as f:
                    ical_content = f.read()
                
                events = self.parse_icalendar_simple(ical_content)
                
                for event in events:
                    if 'title' in event:
                        self._add_event_triples(event)
                        
            except Exception as e:
                print(f"Warning: Failed to parse {ics_file}: {e}")
    
    def _add_event_triples(self, event: Dict) -> None:
        """Add RDF triples for a single event."""
        event_id = f"event-takeout-{self.event_counter:03d}"
        event_uri = PIM[event_id]
        
        # Basic event information
        self.graph.add((event_uri, RDF.type, ICAL.Vevent))
        self.graph.add((event_uri, DCTERMS.title, Literal(event['title'])))
        
        if 'start' in event:
            # Simple datetime parsing - handle YYYYMMDDTHHMMSSZ format
            start_str = event['start']
            try:
                if 'T' in start_str and start_str.endswith('Z'):
                    # Parse YYYYMMDDTHHMMSSZ format
                    dt_str = start_str[:-1]  # Remove Z
                    if len(dt_str) >= 8:
                        year = dt_str[:4]
                        month = dt_str[4:6]
                        day = dt_str[6:8]
                        
                        if len(dt_str) >= 15:
                            hour = dt_str[9:11]
                            minute = dt_str[11:13]
                            second = dt_str[13:15]
                            iso_dt = f"{year}-{month}-{day}T{hour}:{minute}:{second}Z"
                        else:
                            iso_dt = f"{year}-{month}-{day}T00:00:00Z"
                        
                        self.graph.add((event_uri, ICAL.dtstart, 
                                       Literal(iso_dt, datatype=XSD.dateTime)))
            except:
                pass  # Skip invalid dates
        
        if 'location' in event:
            self.graph.add((event_uri, ICAL.location, Literal(event['location'])))
        
        # Add metadata
        self.graph.add((event_uri, DCTERMS.created, 
                       Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        self.graph.add((event_uri, DCTERMS.source, 
                       Literal("Google Takeout - Calendar")))
        
        self.event_counter += 1


class LocationConverter:
    """Converts Google Location History (JSON) to RDF."""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.place_counter = 1
    
    def convert_to_rdf(self, json_files: List[Path]) -> None:
        """Convert location JSON files to RDF triples."""
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle different JSON structures
                locations = []
                if isinstance(data, dict):
                    if 'locations' in data:
                        locations = data['locations']
                    elif 'timelineObjects' in data:
                        # Extract locations from timeline objects
                        for obj in data['timelineObjects']:
                            if 'placeVisit' in obj:
                                place_visit = obj['placeVisit']
                                if 'location' in place_visit:
                                    locations.append(place_visit['location'])
                elif isinstance(data, list):
                    locations = data
                
                for location in locations[:10]:  # Limit to first 10 for demo
                    self._add_location_triples(location)
                    
            except Exception as e:
                print(f"Warning: Failed to parse {json_file}: {e}")
    
    def _add_location_triples(self, location: Dict) -> None:
        """Add RDF triples for a single location."""
        place_id = f"place-takeout-{self.place_counter:03d}"
        place_uri = PIM[place_id]
        
        # Basic place information
        self.graph.add((place_uri, RDF.type, PIMNS.Place))
        
        # Add coordinates if available
        if 'latitudeE7' in location and 'longitudeE7' in location:
            lat = float(location['latitudeE7']) / 10000000
            lng = float(location['longitudeE7']) / 10000000
            
            self.graph.add((place_uri, GEO.lat, Literal(lat, datatype=XSD.float)))
            self.graph.add((place_uri, GEO.long, Literal(lng, datatype=XSD.float)))
        
        # Add timestamp if available
        if 'timestampMs' in location:
            timestamp_ms = int(location['timestampMs'])
            dt = datetime.fromtimestamp(timestamp_ms / 1000).isoformat() + 'Z'
            self.graph.add((place_uri, PIMNS.visitedOn, 
                           Literal(dt, datatype=XSD.dateTime)))
        
        # Add name if available
        if 'name' in location:
            self.graph.add((place_uri, PIMNS.locationName, Literal(location['name'])))
        
        # Add metadata
        self.graph.add((place_uri, DCTERMS.created, 
                       Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        self.graph.add((place_uri, DCTERMS.source, 
                       Literal("Google Takeout - Location History")))
        
        self.place_counter += 1


class TakeoutIngestion:
    """Main ingestion class that orchestrates the conversion process."""
    
    def __init__(self, archive_path: str, output_dir: str = "data"):
        self.archive_path = archive_path
        self.output_dir = Path(output_dir)
        self.extractor = TakeoutExtractor(archive_path)
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
    
    def ingest(self) -> Dict[str, str]:
        """Main ingestion method."""
        print(f"Starting ingestion of {self.archive_path}")
        
        # Extract archive
        temp_dir = self.extractor.extract_to_temp()
        output_files = {}
        
        try:
            # Find data files
            data_files = self.extractor.find_data_files(temp_dir)
            print(f"Found data files: {[(k, len(v)) for k, v in data_files.items()]}")
            
            # Process each data type
            if data_files['contacts']:
                contacts_file = self._process_contacts(data_files['contacts'])
                output_files['contacts'] = contacts_file
            
            if data_files['calendar']:
                calendar_file = self._process_calendar(data_files['calendar'])
                output_files['calendar'] = calendar_file
            
            if data_files['location']:
                location_file = self._process_locations(data_files['location'])
                output_files['location'] = location_file
            
            print(f"Ingestion complete. Generated files: {list(output_files.values())}")
            return output_files
            
        finally:
            # Clean up temp directory
            import shutil
            shutil.rmtree(temp_dir)
    
    def _process_contacts(self, vcf_files: List[Path]) -> str:
        """Process contacts and generate contacts-takeout.ttl."""
        graph = self._create_base_graph()
        converter = ContactsConverter(graph)
        converter.convert_to_rdf(vcf_files)
        
        output_file = self.output_dir / "contacts-takeout.ttl"
        graph.serialize(destination=str(output_file), format='turtle')
        print(f"Generated: {output_file} ({len(graph)} triples)")
        
        return str(output_file)
    
    def _process_calendar(self, ics_files: List[Path]) -> str:
        """Process calendar events and generate events-takeout.ttl."""
        graph = self._create_base_graph()
        converter = CalendarConverter(graph)
        converter.convert_to_rdf(ics_files)
        
        output_file = self.output_dir / "events-takeout.ttl"
        graph.serialize(destination=str(output_file), format='turtle')
        print(f"Generated: {output_file} ({len(graph)} triples)")
        
        return str(output_file)
    
    def _process_locations(self, json_files: List[Path]) -> str:
        """Process location history and generate locations-takeout.ttl."""
        graph = self._create_base_graph()
        converter = LocationConverter(graph)
        converter.convert_to_rdf(json_files)
        
        output_file = self.output_dir / "locations-takeout.ttl"
        graph.serialize(destination=str(output_file), format='turtle')
        print(f"Generated: {output_file} ({len(graph)} triples)")
        
        return str(output_file)
    
    def _create_base_graph(self) -> Graph:
        """Create a graph with standard prefixes."""
        graph = Graph()
        
        # Bind namespaces
        graph.bind("", PIM)
        graph.bind("pim", PIMNS)
        graph.bind("foaf", FOAF)
        graph.bind("ical", ICAL)
        graph.bind("geo", GEO)
        graph.bind("dcterms", DCTERMS)
        graph.bind("xsd", XSD)
        graph.bind("rdfs", RDFS)
        graph.bind("vcard", VCARD)
        
        return graph


def main():
    """Command-line interface for the takeout ingestion script."""
    parser = argparse.ArgumentParser(
        description="Ingest Google Takeout archive into PIM RDF format"
    )
    parser.add_argument(
        "archive_path",
        help="Path to the Google Takeout ZIP archive"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="data",
        help="Output directory for generated TTL files (default: data)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be processed without generating files"
    )
    
    args = parser.parse_args()
    
    try:
        if args.dry_run:
            print(f"DRY RUN: Would process {args.archive_path}")
            extractor = TakeoutExtractor(args.archive_path)
            temp_dir = extractor.extract_to_temp()
            try:
                data_files = extractor.find_data_files(temp_dir)
                print(f"Would process: {[(k, len(v)) for k, v in data_files.items()]}")
            finally:
                import shutil
                shutil.rmtree(temp_dir)
        else:
            ingestion = TakeoutIngestion(args.archive_path, args.output_dir)
            output_files = ingestion.ingest()
            
            print("\n=== Ingestion Summary ===")
            for data_type, file_path in output_files.items():
                print(f"{data_type.title()}: {file_path}")
            print("\nNext steps:")
            print("1. Review generated TTL files")
            print("2. Update config/domains.yaml to include new files")
            print("3. Run util/validate_pim.sh to validate")
    
    except TakeoutIngestionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()