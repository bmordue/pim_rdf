# PIM RDF — A personal knowledge base powered by RDF/Turtle

This repository is a blueprint for a personal knowledge base modeled in RDF and stored in plain-text Turtle (.ttl) files. It’s modular, Git-friendly, and queryable with SPARQL. Use it to connect notes, tasks, contacts, projects, bookmarks, events, and tags with stable URIs and common vocabularies.

## Key ideas

- Files are the database
  - Keep each domain in its own .ttl file; use Git for history and sync.
- Human-first modeling
  - Favor familiar vocabularies; only create a minimal custom namespace for gaps.
- Everything is linkable
  - Use stable URIs so notes ↔ tasks ↔ contacts ↔ projects connect cleanly.
- Validate and query
  - Use SHACL for data quality; query locally with Jena/Fuseki (or RDF4J/Oxigraph).

## Namespaces

```turtle
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
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
```

## Custom PIM vocabulary

A minimal vocabulary to cover gaps. You can evolve or replace parts of this with schema.org or ActivityStreams 2.0 as needed.

```turtle
@prefix pim: <https://ben.example/ns/pim#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

pim:Task      a rdfs:Class .
pim:Project   a rdfs:Class .

pim:status    a rdf:Property ; rdfs:range xsd:string .   # "todo" | "doing" | "done"
pim:priority  a rdf:Property ; rdfs:range xsd:integer .
pim:blockedBy a rdf:Property ; rdfs:range rdfs:Resource .
pim:estimate  a rdf:Property ; rdfs:range xsd:duration .
pim:inbox     a rdf:Property ; rdfs:range xsd:boolean .
pim:project   a rdf:Property ; rdfs:range rdfs:Resource .
```

## Suggested project structure

This structure keeps domains modular and easy to validate and query. Create only what you need.

```text
pim/
  base.ttl              # prefixes, base metadata about “you”
  contacts.ttl
  notes.ttl
  tasks.ttl
  projects.ttl
  bookmarks.ttl
  events.ttl
  tags.ttl              # SKOS concept scheme for tags
  provenance.ttl        # optional: data import/derivation notes
  shapes/               # SHACL validation shapes
    notes-shapes.ttl
    tasks-shapes.ttl
build/
  merged.ttl            # generated: merged graph for serving/querying
```

## URI conventions

- Keep URIs stable and preferably opaque; avoid encoding titles into them.
- A practical slug pattern is date + short id:
  - Example: `https://ben.example/pim/task/2025-08-14-abc123`
- Give anything you may reference later a URI; avoid blank nodes for primary entities.

## Getting started

1) Authoring

- Edit `.ttl` files in your editor (VS Code + Turtle/TTL/SHACL plugins recommended).
- Keep small “snippets”/templates for notes, tasks, and contacts to ensure consistency.

2) Validation

- Validate syntax during edits:
  - Apache Jena: `riot --validate pim/tasks.ttl`
- Validate shapes (example with Jena SHACL):
  - `shacl validate --shapes pim/shapes/tasks-shapes.ttl --data pim/tasks.ttl`

3) Querying locally

- Merge your domain files into one graph (optional but convenient):
  - `riot --output=TURTLE pim/*.ttl > build/merged.ttl`
- Serve with Fuseki:
  - `fuseki-server --file=build/merged.ttl /pim`
  - Open SPARQL UI at http://localhost:3030/pim

4) Web interface

- A simple web interface is available in the `web/` directory for browsing your data:
  - Start Fuseki as above
  - Serve the web interface: `cd web && python3 -m http.server 8080`
  - Open http://localhost:8080 for a user-friendly data browser
  - See `web/README.md` for detailed setup instructions
  - Quick start with sample data: `./start_web_interface.sh --mock`

5) Versioning and provenance

- Use Git commits as your change history.
- Record imports/batch edits in `pim/provenance.ttl` using `prov:wasDerivedFrom`, `prov:generatedAtTime`, etc.

## Examples

### A task

```turtle
@prefix :        <https://ben.example/pim/> .
@prefix pim:     <https://ben.example/ns/pim#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .

:task-2025-08-14-abc123
  a pim:Task ;
  dcterms:title "Draft personal data model overview" ;
  dcterms:created "2025-08-14T10:05:00Z"^^xsd:dateTime ;
  pim:status "todo" ;
  pim:priority 2 ;
  pim:inbox true ;
  pim:project :project-2025-07-website .
```

### A project

```turtle
@prefix :        <https://ben.example/pim/> .
@prefix pim:     <https://ben.example/ns/pim#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

:project-2025-07-website
  a pim:Project ;
  dcterms:title "Personal website refresh" ;
  dcterms:description "Content audit, design tweaks, deploy automation." .
```

### A note (schema.org CreativeWork)

```turtle
@prefix :        <https://ben.example/pim/> .
@prefix schema:  <https://schema.org/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .

:note-2025-08-14-ttl-shapes
  a schema:CreativeWork ;
  dcterms:title "Why SHACL matters for personal data" ;
  dcterms:created "2025-08-14T09:00:00Z"^^xsd:dateTime ;
  schema:text """SHACL keeps the data tidy so queries stay simple and reliable…""" .
```

### SHACL shape for tasks

```turtle
@prefix sh:  <http://www.w3.org/ns/shacl#> .
@prefix pim: <https://ben.example/ns/pim#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

pim:TaskShape
  a sh:NodeShape ;
  sh:targetClass pim:Task ;
  sh:property [
    sh:path pim:status ;
    sh:in ("todo" "doing" "done") ;
    sh:message "pim:status must be one of: todo, doing, done." ;
  ] ;
  sh:property [
    sh:path pim:priority ;
    sh:datatype xsd:integer ;
    sh:minInclusive 0 ;
    sh:maxInclusive 5 ;
    sh:message "pim:priority should be an integer between 0 and 5." ;
  ] .
```

### SPARQL queries

List open tasks ordered by priority:

```sparql
PREFIX :        <https://ben.example/pim/>
PREFIX pim:     <https://ben.example/ns/pim#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?task ?title ?status ?priority
WHERE {
  ?task a pim:Task ;
        dcterms:title ?title ;
        pim:status ?status ;
        pim:priority ?priority .
  FILTER(?status != "done")
}
ORDER BY DESC(?priority) ?title
```

Tasks for a specific project:

```sparql
PREFIX :    <https://ben.example/pim/>
PREFIX pim: <https://ben.example/ns/pim#>

SELECT ?task
WHERE {
  ?task a pim:Task ;
        pim:project :project-2025-07-website .
}
```

## Conventions and best practices

- One resource, one home file
  - Keep the primary triples for a resource together; other files may add statements, but maintain a canonical “home”.
- Avoid blank nodes for re-usable entities; give them URIs.
- Use SKOS for tags (future-proof for hierarchies/synonyms).
- Use `dcterms:` for lifecycle metadata (created, modified, references, source, identifier).
- Prefer `schema:` for content-oriented entities (notes as `schema:CreativeWork`, bookmarks as `schema:BookmarkAction`, etc.).
- Keep dates as `xsd:dateTime` in UTC for consistent filtering.

## Roadmap (optional)

- TriG named graphs for per-file graph boundaries.
- Text search via Jena Text index for note bodies.
- Exports: generate static HTML (RDF → SPARQL → HTML) or JSON-LD snapshots.
- ICS bridge: generate `.ics` from `events.ttl` for calendar interoperability.
- Evaluate mapping/replacing custom task model with schema.org `Action` or ActivityStreams 2.0.

## License

No license specified yet. Consider adding a LICENSE file (e.g., MIT, Apache-2.0) to clarify usage.

