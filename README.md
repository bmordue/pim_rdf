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

> **📋 Task Model Update**: Based on vocabulary evaluation (see [TASK_MODEL_EVALUATION.md](TASK_MODEL_EVALUATION.md)), 
> **schema.org Action** is recommended over the custom `pim:Task` model for improved interoperability. 
> See `examples/` for migration examples and updated queries.

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

### Configuration-Driven Approach

The project now uses configuration files to separate data definitions from application logic:

- **`config/domains.yaml`**: Defines which TTL files should be included in data merging. Adding new domains just requires updating this file.
- **`config/validation.yaml`**: Maps data files to their SHACL shape files for validation.
- **`queries/validation/`**: External SPARQL query files used by the validation script.

This approach allows extending the system without modifying Python code.

**Updated project structure:**
```text
pim/
  # ... existing TTL files ...
  config/               # NEW: configuration-driven setup
    domains.yaml        # defines which TTL files to merge
    validation.yaml     # SHACL validation mappings
  queries/              # UPDATED: organized by purpose
    user/               # user-defined queries (moved from queries/)
      dashboard.sparql
      notes_tagged_rdf_last_30_days.sparql
      open_tasks_by_priority.sparql
    validation/         # NEW: queries used by validation script
      list-tasks.sparql
      list-creativeworks.sparql
      count-by-type.sparql
  # ... rest remains the same ...
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
  - Apache Jena: `riot --validate pim/data/tasks.ttl`
- Validate shapes (example with Jena SHACL):
  - `shacl validate --shapes pim/shapes/tasks-shapes.ttl --data pim/data/tasks.ttl`

3) Querying locally

- Merge your domain files into one graph (optional but convenient):
  - `riot --output=TURTLE pim/data/*.ttl > build/merged.ttl`
- Serve with Fuseki:
  - `fuseki-server --file=build/merged.ttl /pim`
  - Open SPARQL UI at http://localhost:3030/pim

4) Versioning and provenance

- Use Git commits as your change history.
- Record imports/batch edits in `pim/provenance.ttl` using `prov:wasDerivedFrom`, `prov:generatedAtTime`, etc.

## Running SPARQL queries locally

A small helper script is provided to run SPARQL queries from the `queries/` directory against the merged Turtle file `build/merged.ttl`.

Usage:

- Run the default query (open tasks by priority):

  ./util/run_query.py

- Run a specific query file:

  ./util/run_query.py queries/user/dashboard.sparql

- Specify a different data file:

  ./util/run_query.py queries/user/dashboard.sparql -d build/merged.ttl

Requirements:

- Python 3.12+
- rdflib: install with `pip3 install rdflib`

The script prints tab-separated results with a header row when available and exits with a non-zero code on error.

## Interactive Web Dashboard

An interactive web dashboard is available in the `web/` directory for viewing and filtering your personal data:

### Features
- **Unified Dashboard View**: Overview of tasks, notes, projects, and events with key statistics
- **Dynamic Filtering**: Filter tasks by status and priority, search notes by content
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Updates**: Connects to live SPARQL endpoint when available

### Quick Start
1. Start Fuseki server: `fuseki-server --config=data/config-pim.ttl`
2. Open `web/index.html` in browser or serve with: `cd web && python3 -m http.server 8080`
3. Dashboard will connect to SPARQL endpoint at http://localhost:3030/pim/query
4. Falls back to demo data if SPARQL endpoint is unavailable

### Screenshots
- **Dashboard Overview**: ![Dashboard](https://github.com/user-attachments/assets/fd4874e5-23ee-42f5-bd57-fb66f8279290)
- **Task Management**: ![Tasks View](https://github.com/user-attachments/assets/b0ced0cd-d366-45b8-946f-e4ee5025d4d7)  
- **Mobile Responsive**: ![Mobile View](https://github.com/user-attachments/assets/66a75343-48b1-495e-8ea9-c96396e3a480)

For detailed setup instructions, see `web/README.md`.

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

## Task Model Vocabulary Evaluation

**Status: ✅ COMPLETED** - See [TASK_MODEL_EVALUATION.md](TASK_MODEL_EVALUATION.md) for comprehensive analysis.

**Recommendation**: Migrate to **schema.org Action** vocabulary for improved interoperability and semantic richness.

### Key Findings
- **schema.org Action** provides optimal balance of compatibility, expressiveness, and ecosystem support
- **ActivityStreams 2.0** less suitable for personal task management use cases
- Migration path: Hybrid approach allowing gradual transition while preserving custom PIM properties

### Migration Examples
See `examples/` directory for:
- Current vs. migrated task examples
- Updated SPARQL queries
- Enhanced SHACL validation shapes
- Hybrid approach for gradual migration

## Features

- **Google Takeout Ingestion**: Import contacts, calendar events, and location history from Google Takeout archives. See [`docs/takeout-ingestion/USAGE.md`](docs/takeout-ingestion/USAGE.md) for details.
- **Configuration-Driven Data Management**: Easily add new data domains via YAML configuration files.
- **SHACL Validation**: Data quality assurance with shape constraints.
- **SPARQL Querying**: Query your personal data using standard SPARQL.

## Roadmap

- TriG named graphs for per-file graph boundaries.
- Text search via Jena Text index for note bodies.
- Exports: generate static HTML (RDF → SPARQL → HTML) or JSON-LD snapshots.
- ICS bridge: generate `.ics` from `events.ttl` for calendar interoperability.
- **Google Takeout Expansion**: Gmail, Drive, Photos, Chrome bookmarks, Keep notes.

## Quick Start

1. Install dependencies: `pip3 install rdflib pyshacl`
2. Validate repository: `util/validate_pim.sh`
3. **NEW**: Import Google Takeout data: `python3 util/ingest_takeout.py /path/to/takeout.zip`
4. For detailed developer instructions: See `.github/copilot-instructions.md`

## Continuous Integration

The repository includes a GitHub Actions workflow that automatically validates all changes:

- **Triggers**: Pull requests and pushes to main branch
- **Validation includes**: TTL syntax checking, SHACL shapes validation, SPARQL query testing
- **Files monitored**: `*.ttl`, `shapes/**`, `util/validate_pim.sh`, workflow config
- **Dependencies**: Automatically installs `rdflib` and `pyshacl`

The CI pipeline runs the same `util/validate_pim.sh` script used for local development, ensuring consistency between local and remote validation.
