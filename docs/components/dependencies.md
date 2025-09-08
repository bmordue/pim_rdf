# Module Dependencies

## Purpose
This diagram shows the dependencies between the various modules, scripts, and data components of the `pim_rdf` project. It helps in understanding how changes in one part of the system might affect others.

## Diagram
```mermaid
graph LR
    subgraph "Data & Config"
        direction TB
        DataTTL["data/*.ttl"]
        style DataTTL fill:#f9f
        Config["config/*.yaml"]
        Shapes["shapes/*.ttl"]
        Queries["queries/**/*.sparql"]
    end

    subgraph "Core Scripts & Tools"
        direction TB
        Validate["util/validate_pim.sh"]
        Ingest["Ingestion Scripts\n(ingest_takeout.py, import_vcf.py)"]
        Export["export.py"]
        ICSBridge["ics_bridge.py"]
        RunQuery["util/run_query.py"]
    end

    subgraph "Web Interface"
        direction TB
        Fuseki["Apache Fuseki"]
        WebApp["Web App (JS/HTML)"]
        style WebApp fill:#bbf
    end

    %% Dependencies
    Config --> Validate
    Shapes --> Validate
    DataTTL --> Validate

    Ingest --> DataTTL

    DataTTL --> Fuseki
    Fuseki --> WebApp

    DataTTL --> RunQuery
    Queries --> RunQuery

    DataTTL --> Export
    DataTTL --> ICSBridge
```

## Key Components
- **Data & Config**: The declarative part of the system. This includes the core RDF data (`.ttl` files), YAML configuration files, SHACL shapes for validation, and SPARQL queries.
- **Core Scripts & Tools**: The imperative part of the system. These are scripts that perform actions like validating data, importing new data from external sources, or exporting data to different formats.
- **Web Interface**: The user-facing component, which consists of a backend SPARQL server (Apache Fuseki) and a frontend web application.

## Notes
- The arrows indicate a dependency. For example, the `Validation` script depends on `Config`, `Shapes`, and `Data TTL` files to perform its function.
- The `Data TTL` files are central to the system, as almost every component either reads from or writes to them.

## Related Diagrams
- [System Architecture Overview](../architecture/system-overview.md)
- [Class Relationships](./class-diagram.md)
