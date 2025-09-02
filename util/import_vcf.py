#!/usr/bin/env python3
"""
VCF to RDF Contact Import Script

Imports contacts from VCF (vCard) files and converts them to RDF using FOAF vocabulary,
compatible with the PIM RDF knowledge base.

Usage:
    python3 util/import_vcf.py input.vcf [output.ttl]
    python3 util/import_vcf.py contacts.vcf data/imported-contacts.ttl
"""

import sys
import re
from datetime import datetime
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, FOAF, XSD


def parse_vcard_file(filename):
    """
    Parse a VCF file and extract vCard records.
    
    Returns a list of dictionaries, each representing a vCard contact.
    """
    contacts = []
    current_contact = {}
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                
                if line == 'BEGIN:VCARD':
                    current_contact = {}
                elif line == 'END:VCARD':
                    if current_contact:
                        contacts.append(current_contact)
                        current_contact = {}
                elif ':' in line:
                    # Parse property:value lines
                    if ';' in line.split(':')[0]:
                        # Property has parameters (e.g., EMAIL;TYPE=WORK:email@example.com)
                        prop_part, value = line.split(':', 1)
                        prop_name = prop_part.split(';')[0]
                    else:
                        # Simple property:value
                        prop_name, value = line.split(':', 1)
                    
                    prop_name = prop_name.upper()
                    
                    # Handle multiple values for same property (e.g., multiple emails)
                    if prop_name in current_contact:
                        if not isinstance(current_contact[prop_name], list):
                            current_contact[prop_name] = [current_contact[prop_name]]
                        current_contact[prop_name].append(value)
                    else:
                        current_contact[prop_name] = value
                        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading VCF file: {e}")
        sys.exit(1)
    
    return contacts


def generate_contact_uri(base_namespace, contact_data, existing_uris, counter):
    """
    Generate a stable, unique URI for a contact.
    
    Uses name-based approach when possible, falls back to counter-based.
    """
    # Try to create a URI based on the contact's name
    if 'FN' in contact_data:
        name = contact_data['FN']
        # Clean name for URI (remove special characters, convert to lowercase)
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        clean_name = re.sub(r'\s+', '-', clean_name.strip()).lower()
        uri_candidate = f"contact-{clean_name}"
        
        # Ensure uniqueness
        if uri_candidate not in existing_uris:
            existing_uris.add(uri_candidate)
            return base_namespace[uri_candidate]
    
    # Fall back to counter-based URI
    uri_candidate = f"contact-{counter:03d}"
    while uri_candidate in existing_uris:
        counter += 1
        uri_candidate = f"contact-{counter:03d}"
    
    existing_uris.add(uri_candidate)
    return base_namespace[uri_candidate]


def convert_contacts_to_rdf(contacts):
    """
    Convert parsed vCard contacts to RDF using FOAF vocabulary.
    """
    # Create RDF graph
    g = Graph()
    
    # Define namespaces
    base_ns = Namespace("https://ben.example/pim/")
    pim_ns = Namespace("https://ben.example/ns/pim#")
    
    # Bind prefixes for cleaner output
    g.bind("", base_ns)
    g.bind("foaf", FOAF)
    g.bind("rdfs", RDFS)
    g.bind("pim", pim_ns)
    g.bind("xsd", XSD)
    
    existing_uris = set()
    counter = 1
    
    for contact_data in contacts:
        # Generate unique URI for this contact
        contact_uri = generate_contact_uri(base_ns, contact_data, existing_uris, counter)
        counter += 1
        
        # Add basic type
        g.add((contact_uri, RDF.type, FOAF.Person))
        
        # Add name information
        if 'FN' in contact_data:
            g.add((contact_uri, RDFS.label, Literal(contact_data['FN'])))
            g.add((contact_uri, FOAF.name, Literal(contact_data['FN'])))
        
        # Add structured name if available
        if 'N' in contact_data:
            # N format: Family;Given;Additional;Prefix;Suffix
            name_parts = contact_data['N'].split(';')
            if len(name_parts) >= 2:
                if name_parts[1]:  # Given name
                    g.add((contact_uri, FOAF.givenName, Literal(name_parts[1])))
                if name_parts[0]:  # Family name
                    g.add((contact_uri, FOAF.familyName, Literal(name_parts[0])))
        
        # Add email addresses
        if 'EMAIL' in contact_data:
            emails = contact_data['EMAIL'] if isinstance(contact_data['EMAIL'], list) else [contact_data['EMAIL']]
            for email in emails:
                g.add((contact_uri, FOAF.mbox, URIRef(f"mailto:{email}")))
        
        # Add phone numbers
        if 'TEL' in contact_data:
            phones = contact_data['TEL'] if isinstance(contact_data['TEL'], list) else [contact_data['TEL']]
            for phone in phones:
                g.add((contact_uri, FOAF.phone, URIRef(f"tel:{phone}")))
        
        # Add organization
        if 'ORG' in contact_data:
            g.add((contact_uri, pim_ns.organization, Literal(contact_data['ORG'])))
        
        # Add title/role
        if 'TITLE' in contact_data:
            g.add((contact_uri, pim_ns.title, Literal(contact_data['TITLE'])))
        
        # Add website
        if 'URL' in contact_data:
            g.add((contact_uri, FOAF.homepage, URIRef(contact_data['URL'])))
        
        # Add notes
        if 'NOTE' in contact_data:
            g.add((contact_uri, RDFS.comment, Literal(contact_data['NOTE'])))
    
    return g


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'imported-contacts.ttl'
    
    print(f"Importing contacts from: {input_file}")
    print(f"Output file: {output_file}")
    
    # Parse VCF file
    contacts = parse_vcard_file(input_file)
    print(f"Found {len(contacts)} contact(s)")
    
    if not contacts:
        print("No contacts found in VCF file.")
        sys.exit(0)
    
    # Convert to RDF
    rdf_graph = convert_contacts_to_rdf(contacts)
    
    # Save to TTL file
    try:
        rdf_graph.serialize(destination=output_file, format='turtle')
        print(f"Successfully saved {len(rdf_graph)} RDF triples to {output_file}")
        
        # Show a preview of the generated RDF
        print("\nGenerated RDF preview:")
        preview_text = rdf_graph.serialize(format='turtle')
        if isinstance(preview_text, bytes):
            preview_text = preview_text.decode('utf-8')
        preview_lines = preview_text.split('\n')[:15]
        for line in preview_lines:
            print(f"  {line}")
        if len(preview_text.split('\n')) > 15:
            print("  ...")
            
    except Exception as e:
        print(f"Error saving RDF file: {e}")
        sys.exit(1)
    
    print(f"\nImport completed! You can now merge this file with your existing contacts:")
    print(f"  1. Review the generated file: {output_file}")
    print(f"  2. Manually merge with data/contacts.ttl if needed")
    print(f"  3. Run validation: util/validate_pim.sh")


if __name__ == "__main__":
    main()