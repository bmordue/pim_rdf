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
SCHEMA = Namespace("https://schema.org/")


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
                timeline_objects = []
                
                if isinstance(data, dict):
                    if 'locations' in data:
                        # Classic Location History format
                        locations = data['locations']
                    elif 'timelineObjects' in data:
                        # Semantic Location History format
                        timeline_objects = data['timelineObjects']
                elif isinstance(data, list):
                    locations = data
                
                # Process classic location entries (limit for demo)
                for location in locations[:20]:
                    self._add_location_triples(location)
                
                # Process timeline objects (place visits and activity segments)
                for obj in timeline_objects[:20]:
                    if 'placeVisit' in obj:
                        self._add_place_visit_triples(obj['placeVisit'])
                    elif 'activitySegment' in obj:
                        self._add_activity_segment_triples(obj['activitySegment'])
                        
            except Exception as e:
                print(f"Warning: Failed to parse {json_file}: {e}")
    
    def _add_location_triples(self, location: Dict) -> None:
        """Add RDF triples for a single location from classic Location History."""
        place_id = f"place-takeout-{self.place_counter:03d}"
        place_uri = PIM[place_id]
        
        # Basic place information - use schema:Place as primary type
        self.graph.add((place_uri, RDF.type, SCHEMA.Place))
        self.graph.add((place_uri, RDF.type, PIMNS.Place))  # Keep custom type as well
        
        # Geographic coordinates
        if 'latitudeE7' in location and 'longitudeE7' in location:
            lat = float(location['latitudeE7']) / 10000000
            lng = float(location['longitudeE7']) / 10000000
            
            self.graph.add((place_uri, GEO.lat, Literal(lat, datatype=XSD.float)))
            self.graph.add((place_uri, GEO.long, Literal(lng, datatype=XSD.float)))
            self.graph.add((place_uri, SCHEMA.latitude, Literal(lat, datatype=XSD.float)))
            self.graph.add((place_uri, SCHEMA.longitude, Literal(lng, datatype=XSD.float)))
        
        # Altitude if available
        if 'altitude' in location:
            self.graph.add((place_uri, SCHEMA.elevation, 
                           Literal(location['altitude'], datatype=XSD.integer)))
        
        # Location accuracy
        if 'accuracy' in location:
            self.graph.add((place_uri, PIMNS.accuracy, 
                           Literal(location['accuracy'], datatype=XSD.integer)))
        
        # Velocity and heading (for movement data)
        if 'velocity' in location:
            self.graph.add((place_uri, PIMNS.velocity, 
                           Literal(location['velocity'], datatype=XSD.integer)))
        
        if 'heading' in location:
            self.graph.add((place_uri, PIMNS.heading, 
                           Literal(location['heading'], datatype=XSD.integer)))
        
        # Timestamp - when this location was recorded
        if 'timestampMs' in location:
            timestamp_ms = int(location['timestampMs'])
            dt = datetime.fromtimestamp(timestamp_ms / 1000).isoformat() + 'Z'
            self.graph.add((place_uri, PIMNS.visitedOn, 
                           Literal(dt, datatype=XSD.dateTime)))
            self.graph.add((place_uri, SCHEMA.dateCreated, 
                           Literal(dt, datatype=XSD.dateTime)))
        
        # Activity information (if this location has activity data)
        if 'activity' in location:
            for activity in location['activity']:
                if 'type' in activity:
                    activity_type = activity['type'].replace('_', ' ').title()
                    self.graph.add((place_uri, PIMNS.activityType, 
                                   Literal(activity_type)))
                
                if 'confidence' in activity:
                    self.graph.add((place_uri, PIMNS.activityConfidence, 
                                   Literal(activity['confidence'], datatype=XSD.integer)))
        
        # Source information
        if 'source' in location:
            self.graph.add((place_uri, PIMNS.dataSource, Literal(location['source'])))
        
        # Device information
        if 'deviceTag' in location:
            self.graph.add((place_uri, PIMNS.deviceTag, 
                           Literal(location['deviceTag'], datatype=XSD.integer)))
        
        # Platform type
        if 'platformType' in location:
            platform = location['platformType'].replace('_', ' ').title()
            self.graph.add((place_uri, PIMNS.platformType, Literal(platform)))
        
        # Add basic metadata
        self.graph.add((place_uri, DCTERMS.created, 
                       Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        self.graph.add((place_uri, DCTERMS.source, 
                       Literal("Google Takeout - Location History")))
        
        self.place_counter += 1
    
    def _add_place_visit_triples(self, place_visit: Dict) -> None:
        """Add RDF triples for a place visit from timeline data."""
        place_id = f"place-visit-takeout-{self.place_counter:03d}"
        place_uri = PIM[place_id]
        
        # Basic place visit information
        self.graph.add((place_uri, RDF.type, SCHEMA.Place))
        self.graph.add((place_uri, RDF.type, SCHEMA.TouristAttraction))  # Could be visit to any place
        self.graph.add((place_uri, RDF.type, PIMNS.PlaceVisit))
        
        # Duration of visit
        if 'duration' in place_visit:
            duration = place_visit['duration']
            if 'startTimestampMs' in duration and 'endTimestampMs' in duration:
                start_ms = int(duration['startTimestampMs'])
                end_ms = int(duration['endTimestampMs'])
                
                start_dt = datetime.fromtimestamp(start_ms / 1000).isoformat() + 'Z'
                end_dt = datetime.fromtimestamp(end_ms / 1000).isoformat() + 'Z'
                
                self.graph.add((place_uri, SCHEMA.startDate, 
                               Literal(start_dt, datatype=XSD.dateTime)))
                self.graph.add((place_uri, SCHEMA.endDate, 
                               Literal(end_dt, datatype=XSD.dateTime)))
                
                # Calculate duration in minutes
                duration_minutes = (end_ms - start_ms) / (1000 * 60)
                self.graph.add((place_uri, SCHEMA.duration, 
                               Literal(f"PT{int(duration_minutes)}M", datatype=XSD.duration)))
        
        # Place location details
        if 'location' in place_visit:
            location = place_visit['location']
            
            # Coordinates
            if 'latitudeE7' in location and 'longitudeE7' in location:
                lat = float(location['latitudeE7']) / 10000000
                lng = float(location['longitudeE7']) / 10000000
                
                self.graph.add((place_uri, GEO.lat, Literal(lat, datatype=XSD.float)))
                self.graph.add((place_uri, GEO.long, Literal(lng, datatype=XSD.float)))
                self.graph.add((place_uri, SCHEMA.latitude, Literal(lat, datatype=XSD.float)))
                self.graph.add((place_uri, SCHEMA.longitude, Literal(lng, datatype=XSD.float)))
            
            # Place ID (Google's internal ID)
            if 'placeId' in location:
                self.graph.add((place_uri, DCTERMS.identifier, 
                               Literal(location['placeId'])))
                self.graph.add((place_uri, PIMNS.googlePlaceId, 
                               Literal(location['placeId'])))
            
            # Place name
            if 'name' in location:
                self.graph.add((place_uri, SCHEMA.name, Literal(location['name'])))
                self.graph.add((place_uri, RDFS.label, Literal(location['name'])))
            
            # Address information
            if 'address' in location:
                self.graph.add((place_uri, SCHEMA.address, Literal(location['address'])))
            
            if 'formattedAddress' in location:
                self.graph.add((place_uri, SCHEMA.address, 
                               Literal(location['formattedAddress'])))
            
            # Semantic place type (restaurant, home, etc.)
            if 'semanticType' in location:
                semantic_type = location['semanticType'].replace('_', ' ').title()
                self.graph.add((place_uri, PIMNS.semanticType, Literal(semantic_type)))
                
                # Map common semantic types to schema.org types
                schema_type_mapping = {
                    'TYPE_HOME': SCHEMA.Residence,
                    'TYPE_WORK': SCHEMA.Place,  # Could be more specific
                    'TYPE_SEARCHED_ADDRESS': SCHEMA.Place,
                    'TYPE_ALIASED_LOCATION': SCHEMA.Place
                }
                
                if location['semanticType'] in schema_type_mapping:
                    schema_type = schema_type_mapping[location['semanticType']]
                    self.graph.add((place_uri, RDF.type, schema_type))
            
            # Location confidence
            if 'locationConfidence' in location:
                confidence = float(location['locationConfidence'])
                self.graph.add((place_uri, PIMNS.locationConfidence, 
                               Literal(confidence, datatype=XSD.float)))
            
            # Plus code (Open Location Code)
            if 'plusCode' in location:
                self.graph.add((place_uri, PIMNS.plusCode, 
                               Literal(location['plusCode'])))
            
            # Source information
            if 'sourceInfo' in location:
                source_info = location['sourceInfo']
                if 'deviceTag' in source_info:
                    self.graph.add((place_uri, PIMNS.deviceTag, 
                                   Literal(source_info['deviceTag'], datatype=XSD.integer)))
        
        # Visit confidence
        if 'visitConfidence' in place_visit:
            confidence = float(place_visit['visitConfidence'])
            self.graph.add((place_uri, PIMNS.visitConfidence, 
                           Literal(confidence, datatype=XSD.float)))
        
        # Place confidence (overall confidence in place identification)
        if 'placeConfidence' in place_visit:
            place_confidence_str = place_visit['placeConfidence']
            # Convert confidence strings to numeric values
            confidence_map = {
                'LOW_CONFIDENCE': 0.3,
                'MEDIUM_CONFIDENCE': 0.7,
                'HIGH_CONFIDENCE': 0.9,
                'USER_CONFIRMED': 1.0
            }
            confidence = confidence_map.get(place_confidence_str, 0.5)
            self.graph.add((place_uri, PIMNS.placeConfidence, 
                           Literal(confidence, datatype=XSD.float)))
        
        # Center lat/lng if different from location
        if 'centerLatE7' in place_visit and 'centerLngE7' in place_visit:
            center_lat = float(place_visit['centerLatE7']) / 10000000
            center_lng = float(place_visit['centerLngE7']) / 10000000
            self.graph.add((place_uri, PIMNS.centerLatitude, 
                           Literal(center_lat, datatype=XSD.float)))
            self.graph.add((place_uri, PIMNS.centerLongitude, 
                           Literal(center_lng, datatype=XSD.float)))
        
        # Child visits (nested visits within this location)
        if 'childVisits' in place_visit:
            for child_idx, child_visit in enumerate(place_visit['childVisits']):
                child_id = f"{place_id}-child-{child_idx + 1}"
                child_uri = PIM[child_id]
                
                self.graph.add((child_uri, RDF.type, PIMNS.PlaceVisit))
                self.graph.add((place_uri, PIMNS.hasChildVisit, child_uri))
                
                # Add child visit details (simplified)
                if 'location' in child_visit and 'name' in child_visit['location']:
                    self.graph.add((child_uri, SCHEMA.name, 
                                   Literal(child_visit['location']['name'])))
        
        # Other places (nearby or related places)
        if 'otherCandidateLocations' in place_visit:
            for candidate in place_visit['otherCandidateLocations']:
                if 'placeId' in candidate:
                    # Create a simple reference to alternative place
                    candidate_uri = URIRef(f"https://ben.example/pim/place-candidate-{candidate['placeId']}")
                    self.graph.add((place_uri, PIMNS.hasAlternativePlace, candidate_uri))
                    
                    if 'semanticType' in candidate:
                        semantic_type = candidate['semanticType'].replace('_', ' ').title()
                        self.graph.add((candidate_uri, PIMNS.semanticType, 
                                       Literal(semantic_type)))
        
        # Add metadata
        self.graph.add((place_uri, DCTERMS.created, 
                       Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        self.graph.add((place_uri, DCTERMS.source, 
                       Literal("Google Takeout - Timeline (Place Visit)")))
        
        self.place_counter += 1
    
    def _add_activity_segment_triples(self, activity_segment: Dict) -> None:
        """Add RDF triples for an activity segment (travel between places)."""
        activity_id = f"activity-takeout-{self.place_counter:03d}"
        activity_uri = PIM[activity_id]
        
        # Basic activity information
        self.graph.add((activity_uri, RDF.type, SCHEMA.TravelAction))
        self.graph.add((activity_uri, RDF.type, PIMNS.ActivitySegment))
        
        # Duration
        if 'duration' in activity_segment:
            duration = activity_segment['duration']
            if 'startTimestampMs' in duration and 'endTimestampMs' in duration:
                start_ms = int(duration['startTimestampMs'])
                end_ms = int(duration['endTimestampMs'])
                
                start_dt = datetime.fromtimestamp(start_ms / 1000).isoformat() + 'Z'
                end_dt = datetime.fromtimestamp(end_ms / 1000).isoformat() + 'Z'
                
                self.graph.add((activity_uri, SCHEMA.startTime, 
                               Literal(start_dt, datatype=XSD.dateTime)))
                self.graph.add((activity_uri, SCHEMA.endTime, 
                               Literal(end_dt, datatype=XSD.dateTime)))
        
        # Activity type (walking, driving, etc.)
        if 'activityType' in activity_segment:
            activity_type = activity_segment['activityType'].replace('_', ' ').title()
            self.graph.add((activity_uri, PIMNS.activityType, Literal(activity_type)))
            
            # Map to schema.org types where possible
            if activity_segment['activityType'] == 'IN_VEHICLE':
                self.graph.add((activity_uri, RDF.type, SCHEMA.DriveAction))
            elif activity_segment['activityType'] == 'WALKING':
                self.graph.add((activity_uri, RDF.type, SCHEMA.WalkAction))
            elif activity_segment['activityType'] == 'ON_BICYCLE':
                self.graph.add((activity_uri, RDF.type, SCHEMA.BicycleTrip))
        
        # Distance
        if 'distance' in activity_segment:
            distance_m = float(activity_segment['distance'])
            self.graph.add((activity_uri, SCHEMA.distance, 
                           Literal(f"{distance_m} m")))  # Include units
            self.graph.add((activity_uri, PIMNS.distanceMeters, 
                           Literal(distance_m, datatype=XSD.float)))
        
        # Start and end locations
        if 'startLocation' in activity_segment:
            start_loc = activity_segment['startLocation']
            if 'latitudeE7' in start_loc and 'longitudeE7' in start_loc:
                start_lat = float(start_loc['latitudeE7']) / 10000000
                start_lng = float(start_loc['longitudeE7']) / 10000000
                
                # Create a simple location point
                start_point_id = f"{activity_id}-start"
                start_point_uri = PIM[start_point_id]
                
                self.graph.add((start_point_uri, RDF.type, SCHEMA.GeoCoordinates))
                self.graph.add((start_point_uri, SCHEMA.latitude, 
                               Literal(start_lat, datatype=XSD.float)))
                self.graph.add((start_point_uri, SCHEMA.longitude, 
                               Literal(start_lng, datatype=XSD.float)))
                
                self.graph.add((activity_uri, SCHEMA.fromLocation, start_point_uri))
        
        if 'endLocation' in activity_segment:
            end_loc = activity_segment['endLocation']
            if 'latitudeE7' in end_loc and 'longitudeE7' in end_loc:
                end_lat = float(end_loc['latitudeE7']) / 10000000
                end_lng = float(end_loc['longitudeE7']) / 10000000
                
                # Create a simple location point
                end_point_id = f"{activity_id}-end"
                end_point_uri = PIM[end_point_id]
                
                self.graph.add((end_point_uri, RDF.type, SCHEMA.GeoCoordinates))
                self.graph.add((end_point_uri, SCHEMA.latitude, 
                               Literal(end_lat, datatype=XSD.float)))
                self.graph.add((end_point_uri, SCHEMA.longitude, 
                               Literal(end_lng, datatype=XSD.float)))
                
                self.graph.add((activity_uri, SCHEMA.toLocation, end_point_uri))
        
        # Confidence
        if 'confidence' in activity_segment:
            confidence_str = activity_segment['confidence']
            # Convert confidence strings to numeric values
            confidence_map = {
                'LOW': 0.3,
                'MEDIUM': 0.7,
                'HIGH': 0.9
            }
            confidence = confidence_map.get(confidence_str, 0.5)
            self.graph.add((activity_uri, PIMNS.confidence, 
                           Literal(confidence, datatype=XSD.float)))
        
        # Activities with confidence scores
        if 'activities' in activity_segment:
            for activity in activity_segment['activities']:
                if 'activityType' in activity:
                    activity_type = activity['activityType'].replace('_', ' ').title()
                    self.graph.add((activity_uri, PIMNS.possibleActivityType, 
                                   Literal(activity_type)))
                
                if 'probability' in activity:
                    # Note: storing multiple probabilities would need a more complex model
                    pass
        
        # Waypoint path (detailed GPS trace)
        if 'waypointPath' in activity_segment:
            waypoint_path = activity_segment['waypointPath']
            if 'waypoints' in waypoint_path:
                waypoint_count = len(waypoint_path['waypoints'])
                self.graph.add((activity_uri, PIMNS.waypointCount, 
                               Literal(waypoint_count, datatype=XSD.integer)))
                
                # Store a simplified representation of the path
                # In a full implementation, you might store each waypoint
                if 'distanceMeters' in waypoint_path:
                    path_distance = float(waypoint_path['distanceMeters'])
                    self.graph.add((activity_uri, PIMNS.pathDistanceMeters, 
                                   Literal(path_distance, datatype=XSD.float)))
        
        # Add metadata
        self.graph.add((activity_uri, DCTERMS.created, 
                       Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        self.graph.add((activity_uri, DCTERMS.source, 
                       Literal("Google Takeout - Timeline (Activity Segment)")))
        
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
        graph.bind("schema", SCHEMA)
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