# PIM RDF - Personal Knowledge Base Instructions

This repository contains a personal knowledge base modeled in RDF using Turtle (.ttl) files. It's designed for linking notes, tasks, contacts, projects, bookmarks, events, and tags using stable URIs and standardized vocabularies.

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Quick Start for New Developers

**Essential first steps after cloning:**
1. `pip3 install rdflib pyshacl` -- Install dependencies (~4 seconds)
2. `util/validate_pim.sh` -- Validate entire repository (~270ms)
3. Explore the data: `python3 -c "import rdflib; g=rdflib.Graph(); g.parse('build/merged.ttl', format='turtle'); results=g.query('SELECT ?type (COUNT(?e) as ?count) WHERE { ?e a ?type } GROUP BY ?type'); [print(f'{str(row[0]).split(\"/\")[-1]}: {row[1]} entities') for row in results]"`

**Repository contains 10 TTL files (~72 triples) modeling personal knowledge with RDF.**

## Working Effectively

### Essential Setup and Dependencies
- Install Python 3.12+ and pip: `sudo apt-get update && sudo apt-get install -y python3 python3-pip`
- Install required Python packages: `pip3 install rdflib pyshacl` -- takes 3-5 seconds. NEVER CANCEL.
- The repository uses Python-based RDF tools instead of Apache Jena due to network limitations in CI environments.

### Core Validation Workflow
- **ALWAYS validate TTL syntax before making changes:**
  ```bash
  python3 -c "
  import rdflib
  g = rdflib.Graph()
  g.parse('filename.ttl', format='turtle')
  print(f'Valid: {len(g)} triples')
  "
  ```
- **Validation time: ~1ms per file. Total repository validation: ~10ms for 10 files.**

### Building and Testing
- **Validate all TTL files:** `util/validate_pim.sh` -- takes 500-600ms. NEVER CANCEL.
- **Merge data files:** Creates `build/merged.ttl` with combined RDF graph (~40 triples) -- takes 6-10ms.
- **SPARQL query testing:** Automated tests run 3 sample queries -- takes 100-300ms total.
- **SHACL validation:** Tests data against shape constraints -- takes 0.6ms per validation.

### Manual Testing and Validation
- **ALWAYS run complete validation after making changes:** `util/validate_pim.sh`
- **Test specific TTL file syntax:** Use the Python validation snippet above for individual files.
- **Test SPARQL queries manually:**
  ```python
  import rdflib
  g = rdflib.Graph()
  g.parse('build/merged.ttl', format='turtle')
  results = g.query('SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5')
  for row in results: print(row)
  ```

### Functional Testing Scenarios
**ALWAYS test these scenarios after making changes:**
1. **Add a new entity** (note, task, contact) and validate it appears in queries
2. **Test SPARQL queries** on the merged dataset to ensure data relationships work
3. **Run end-to-end workflow:** Edit TTL → validate syntax → merge → query
4. **Verify entity types and counts:**
   ```python
   import rdflib
   g = rdflib.Graph()
   g.parse('build/merged.ttl', format='turtle')
   results = g.query('SELECT ?type (COUNT(?e) as ?count) WHERE { ?e a ?type } GROUP BY ?type')
   for row in results: print(f'{row[0]}: {row[1]} entities')
   ```

## Repository Structure

### Key Files and Directories
```
pim_rdf/
├── README.md              # Main documentation
├── data/                  # TTL data files
│   ├── base.ttl           # Core prefixes and personal metadata
│   ├── tasks.ttl          # Task management data
│   ├── notes.ttl          # Notes as schema:CreativeWork
│   ├── contacts.ttl       # Contacts using FOAF vocabulary
│   ├── projects.ttl       # Project definitions
│   ├── bookmarks.ttl      # Bookmarks as schema:BookmarkAction
│   ├── events.ttl         # Calendar events using iCal vocabulary
│   └── tags.ttl           # SKOS concept scheme for tags
├── shapes/                # SHACL validation shapes
│   └── notes-shapes.ttl   # Shape constraints for notes
├── queries/               # Sample SPARQL queries
├── build/                 # Generated files
│   └── merged.ttl         # Combined RDF graph
└── shell.nix              # Nix environment (alternative setup)
```

### URI Conventions
- **Base namespace:** `https://ben.example/pim/`
- **Custom vocabulary:** `https://ben.example/ns/pim#`
- **Entity naming:** Use dash format like `:task-001`, `:note-001` (avoid slashes in local names)
- **Always use stable, opaque URIs:** Prefer `task-2025-08-18-abc123` over encoding titles

## TTL File Authoring Guidelines

### Required Prefixes
**Always include these prefixes in TTL files:**
```turtle
@prefix : <https://ben.example/pim/> .
@prefix pim: <https://ben.example/ns/pim#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix schema: <https://schema.org/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
```

### Vocabulary Usage
- **Tasks:** Use `pim:Task` with `pim:status` ("todo", "doing", "done"), `pim:priority` (0-5)
- **Notes:** Use `schema:CreativeWork` with `dcterms:title`, `schema:text`
- **Contacts:** Use `foaf:Person` with `foaf:mbox` for email
- **Events:** Use `ical:Vevent` with `ical:dtstart`, `ical:location`
- **Projects:** Use `pim:Project` with `dcterms:title`, `dcterms:description`
- **Tags:** Use `skos:Concept` within `skos:ConceptScheme`

### Data Quality Rules
- **Always use UTC timestamps:** `"2025-08-18T14:30:00Z"^^xsd:dateTime`
- **Validate syntax immediately after editing:** Run the Python validation snippet
- **Use consistent entity naming:** dash-separated local names, no slashes
- **Include lifecycle metadata:** `dcterms:created`, `dcterms:title` for all entities

## SPARQL Querying

### Common Query Patterns
```sparql
# List open tasks by priority
PREFIX pim: <https://ben.example/ns/pim#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?task ?title ?priority ?status
WHERE {
  ?task a pim:Task ;
        dcterms:title ?title ;
        pim:status ?status ;
        pim:priority ?priority .
  FILTER(?status != "done")
}
ORDER BY ASC(?priority)
```

### Query Testing
- **Load merged graph:** `g.parse('build/merged.ttl', format='turtle')`
- **Query execution time:** Typically 3-300ms (simple queries ~3ms, complex first queries ~300ms)
- **Always test queries on merged.ttl:** Contains complete dataset (~40 triples)
- **Sample queries available:** Test with files in `queries/` directory:
  - `open_tasks_by_priority.sparql` - Lists incomplete tasks by priority
  - `notes_tagged_rdf_last_30_days.sparql` - Recent notes with RDF tag
  - `dashboard.sparql` - Project dashboard with tasks and status
- **Test sample query:** 
  ```bash
  python3 -c "import rdflib; g=rdflib.Graph(); g.parse('build/merged.ttl', format='turtle'); results=g.query(open('queries/open_tasks_by_priority.sparql').read()); [print(row) for row in results]"
  ```

## SHACL Validation

### Shape Files
- **Location:** `shapes/` directory
- **Naming:** `{domain}-shapes.ttl` (e.g., `notes-shapes.ttl`)
- **Validation command:**
  ```python
  import pyshacl, rdflib
  data_g = rdflib.Graph(); data_g.parse('notes.ttl', format='turtle')
  shape_g = rdflib.Graph(); shape_g.parse('shapes/notes-shapes.ttl', format='turtle')
  conforms, report_graph, report_text = pyshacl.validate(data_g, shacl_graph=shape_g, inference='none')
  print(f'Valid: {conforms}')
  ```

### Validation Timing
- **Per-file SHACL validation:** ~0.6ms
- **Full repository validation:** ~11ms for TTL syntax validation
- **NEVER CANCEL:** All validations complete in under 1 second (total ~600ms)

## Common Tasks

### Adding New Data
1. **Edit appropriate TTL file** (tasks.ttl, notes.ttl, etc.)
2. **Follow URI and vocabulary conventions** outlined above
3. **Validate syntax:** Run Python validation snippet
4. **Test complete workflow:** `util/validate_pim.sh`
5. **Check merged output:** Verify `build/merged.ttl` updates correctly

### Debugging Validation Errors
- **Syntax errors:** Usually missing prefixes or invalid URI formats
- **SHACL violations:** Check shape constraints in `shapes/` directory
- **Query failures:** Verify entity types and property names match vocabulary

### Performance Expectations
- **TTL file parsing:** 0.5-3ms per file
- **Data merging:** 5-6ms for full repository (~40 triples)
- **SPARQL queries:** 3-300ms depending on complexity (simple queries ~3ms, first query ~300ms)
- **SHACL validation:** 0.6ms per shape/data pair
- **Complete validation workflow:** 250-600ms total (typically ~270ms)

## Validation Commands Reference

```bash
# Validate single TTL file
python3 -c "import rdflib; g=rdflib.Graph(); g.parse('filename.ttl', format='turtle'); print(f'Valid: {len(g)} triples')"

# Run complete validation suite
util/validate_pim.sh

# Test SPARQL query
python3 -c "import rdflib; g=rdflib.Graph(); g.parse('build/merged.ttl', format='turtle'); print(list(g.query('SELECT ?s WHERE { ?s a ?type } LIMIT 5')))"

# SHACL validation
python3 -c "import pyshacl, rdflib; d=rdflib.Graph(); d.parse('notes.ttl', format='turtle'); s=rdflib.Graph(); s.parse('shapes/notes-shapes.ttl', format='turtle'); print(pyshacl.validate(d, shacl_graph=s, inference='none')[0])"
```

## Error Prevention
- **Never use slashes in local names:** Use `task-001` not `task/001`
- **Always include required prefixes:** Especially `xsd:` for datatypes
- **Test syntax after every edit:** Use the validation snippet immediately
- **Use consistent vocabulary:** Follow the patterns in existing files
- **Validate before committing:** Run `util/validate_pim.sh` always

## Troubleshooting Common Issues

### Syntax Errors
- **Missing prefix error:** Add missing prefix declaration at top of TTL file
- **Invalid URI:** Check for special characters in local names (use dashes, not slashes)
- **Missing datatype:** Add `^^xsd:dateTime` for timestamps, `^^xsd:integer` for numbers

### SHACL Validation Failures
- **Check shapes directory:** Ensure `shapes/notes-shapes.ttl` exists and is valid
- **Verify data structure:** Ensure notes have required properties (`dcterms:title`, `schema:text`)

### Query Failures
- **Empty results:** Verify entity types match expected vocabularies (`pim:Task`, `schema:CreativeWork`)
- **Performance issues:** First query may take ~300ms, subsequent queries ~3ms (caching)

### Environment Issues
- **Import errors:** Re-run `pip3 install rdflib pyshacl` if modules not found
- **File not found:** Ensure you're in repository root directory `/home/runner/work/pim_rdf/pim_rdf`

## Alternative Setup (Advanced)
- **Nix environment:** `nix-shell` loads Apache Jena and Fuseki (if network allows)
- **Apache Jena tools:** `riot --validate file.ttl`, `shacl validate --shapes shapes.ttl --data data.ttl`
- **Fuseki server options:**
  - Simple: `fuseki-server --file=build/merged.ttl /pim` (for local SPARQL endpoint)
  - Advanced: `fuseki-server --config=config-pim.ttl` (uses repository configuration)
- **Fuseki UI:** Available at http://localhost:3030/pim when server is running

**Note:** Python-based tools are recommended for CI/network-constrained environments due to reliable installation. Apache Jena tools require network access and may not be available in all environments.