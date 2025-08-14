# Overview

This is the blueprint for a personal knowledge base built on RDF with Turtle (.ttl) files as the storage layer. It’s modular, git-friendly, and queryable with SPARQL.

# Overall approach

    Files are the database. Keep each domain in its own .ttl file; commit to Git for history and sync.

    Human-first modeling. Favor familiar vocabularies; only create a tiny custom namespace for gaps.

    Everything is linkable. Use stable URIs so notes ↔ tasks ↔ contacts ↔ projects connect cleanly.

    Validate + query. Use SHACL for data quality; use Jena/Fuseki (or RDF4J/Oxigraph) to query locally.

# Namespaces used

```
@prefix :        <https://ben.example/pim/> .
@prefix pim:     <https://ben.example/ns/pim#> .
@prefix schema:  <https://schema.org/> .
@prefix foaf:    <http://xmlns.com/foaf/0.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix skos:    <http://www.w3.org/2004/02/skos/core#> .
@prefix prov:    <http://www.w3.org/ns/prov#> .
@prefix vcard:   <http://www.w3.org/2006/vcard/ns#> .
@prefix ical:    <http://www.w3.org/2002/12/cal/ical#> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .
```

# Custom PIM vocabulary

For simplicity, use a custom vocabulary:

```
@prefix pim: <https://ben.example/ns/pim#> .

pim:Task      a rdfs:Class .
pim:status    a rdf:Property ; rdfs:range xsd:string .        # "todo" | "doing" | "done"
pim:priority  a rdf:Property ; rdfs:range xsd:integer .
pim:blockedBy a rdf:Property ; rdfs:range rdfs:Resource .
pim:estimate  a rdf:Property ; rdfs:range xsd:duration .
pim:inbox     a rdf:Property .                                # boolean-ish flag via "true"/"false"
pim:Project   a rdfs:Class .
```

TODO: Replace this with schema.org’s Action or AS2

# Project structure

```
pim/
  base.ttl              # prefixes, base metadata about “you”
  contacts.ttl
  notes.ttl
  tasks.ttl
  projects.ttl
  bookmarks.ttl
  events.ttl
  tags.ttl              # SKOS concept scheme for tags
  provenance.ttl        # optional: data import notes
  shapes/               # SHACL validation
    notes-shapes.ttl
    tasks-shapes.ttl
```

Tip: keep URIs stable and opaque; use slugs with date + short id:

```
Tip: keep URIs stable and opaque; use slugs with date + short id:
```

# Local workflow

Authoring

Edit .ttl in your editor (VS Code + Turtle plugin).

Keep a “template” snippet for new notes/tasks to ensure consistent properties.

Validation

Run SHACL (e.g., with Jena SHACL or RDF4J) on save or before commit.

Querying

Start a local Fuseki server over your folder or a merged file:

Merge: riot --output=TURTLE *.ttl > build/merged.ttl

Serve: Fuseki dataset over build/merged.ttl

Versioning

Git commits are your change history; add provenance.ttl when you import or batch-edit to record sources with prov:wasDerivedFrom.

# Helpful conventions

One resource, one place. Put the primary triples for a resource in one file; other files may add statements, but keep the canonical “home” in one place.

Avoid blank nodes for anything you might want to reference later; give it a URI.

Tags via SKOS (future-proof for hierarchies and synonyms).

Use dcterms: for lifecycle metadata (created, modified, references, source, identifier).

Prefer schema: for content-ish things (notes as CreativeWork, bookmarks as BookmarkAction).

Keep dates as xsd:dateTime (UTC) for easier filtering.

# Maybe later

TriG named graphs (for per-file graphs), but stay with .ttl for now.

Text search: Jena’s text index module for searching note bodies.

Exports: generate a static HTML site (RDF → SPARQL → HTML) or JSON-LD snapshots for sharing.

ICS bridge: generate .ics from events.ttl for calendar interop.
