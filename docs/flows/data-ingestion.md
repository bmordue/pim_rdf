# Data Ingestion Flow

## Purpose
This diagram illustrates the process of ingesting data from an external source into the `pim_rdf` knowledge base. The example flow shows how contacts are imported from a VCF file using the provided utility script. A similar flow applies to importing data from Google Takeout.

## Diagram
```mermaid
flowchart TD
    subgraph "User Action"
        A([Start: User has a VCF file])
        B{Run `util/import_vcf.py` script}
        H{Update `config/domains.yaml`}
        J{Run `util/validate_pim.sh`}
    end

    subgraph "Script Execution"
        C[Script parses VCF data]
        D{For each contact?}
        E[Generate stable URI]
        F[Map VCF fields to RDF\n(FOAF, PIM vocabularies)]
        G[Write triples to output .ttl file]
    end

    subgraph "System State"
        I[New data is part of knowledge base]
        K([End: Data ingested and validated])
    end

    A --> B;
    B --> C;
    C --> D;
    D -- Yes --> E;
    E --> F;
    F --> D;
    D -- No --> G;
    G --> H;
    H --> I;
    I --> J;
    J --> K;
```

## Key Steps
1.  **Initiation**: The user starts with an external data file, such as `contacts.vcf`.
2.  **Execution**: The user runs the appropriate ingestion script (e.g., `python3 util/import_vcf.py contacts.vcf data/imported-contacts.ttl`).
3.  **Parsing**: The script reads and parses the source file.
4.  **Transformation**: The script iterates through the data, converting each entry into RDF triples using standard vocabularies (like FOAF for contacts). It generates stable URIs for new entities.
5.  **Output**: The script writes the generated RDF triples to a new `.ttl` file.
6.  **Integration**: The user manually edits `config/domains.yaml` to include the newly created `.ttl` file, making it part of the overall knowledge base.
7.  **Validation**: The user can run the validation script (`util/validate_pim.sh`) to ensure the newly imported data conforms to the project's data quality standards.

## Notes
- This is a manual, user-driven process. There is no automated data ingestion service.
- The same general pattern applies to other data sources like Google Takeout, which has its own ingestion script (`util/ingest_takeout.py`).

## Related Diagrams
- [System Architecture Overview](../architecture/system-overview.md)
- [Data Processing Pipeline](./data-pipeline.md)
