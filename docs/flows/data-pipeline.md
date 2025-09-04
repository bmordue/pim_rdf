# Data Processing Pipeline

## Purpose
This diagram shows the end-to-end data processing pipeline, from the raw RDF data files to the point where data is served and ready for querying. This illustrates the standard workflow for updating and consuming data in the `pim_rdf` system.

## Diagram
```mermaid
flowchart LR
    A[(Raw Data\n`data/*.ttl`)] --> B{Validate Data\n`validate_pim.sh`};
    B -- Valid --> C[Merge Data\n(e.g., using `riot` tool)];
    B -- Invalid --> D[(Validation Report\nSHACL & SPARQL errors)];
    C --> E[("Merged Graph\n`build/merged.ttl`")];
    E --> F[Serve Graph\n`Apache Fuseki`];
    F --> G{Consume via SPARQL};
    G --> H[(Query Results\nWeb UI, CLI, Exports)];
```

## Key Stages
1.  **Raw Data**: The pipeline starts with the collection of individual `.ttl` files located in the `data/` directory. These files represent different domains of personal information (contacts, notes, tasks, etc.).
2.  **Validate Data**: Before processing, all data files are validated using the `util/validate_pim.sh` script. This script checks for syntax errors, and more importantly, validates the data against SHACL shapes defined in `shapes/`. If validation fails, an error report is generated and the pipeline stops.
3.  **Merge Data**: If validation is successful, the individual `.ttl` files (as specified in `config/domains.yaml`) are merged into a single RDF graph, `build/merged.ttl`. This makes it easier to query the entire knowledge base at once.
4.  **Serve Graph**: The merged graph is loaded into an RDF server like Apache Fuseki, which exposes a standard SPARQL endpoint.
5.  **Consume via SPARQL**: Once the data is served, various clients can interact with it by sending SPARQL queries to the Fuseki endpoint. This includes the web interface, command-line query tools, and export scripts.

## Notes
- This pipeline is typically run manually by the user after making changes to the data files.
- The CI/CD workflow in GitHub Actions automates the validation stage for every commit.

## Related Diagrams
- [System Architecture Overview](../architecture/system-overview.md)
- [Data Ingestion Flow](./data-ingestion.md)
