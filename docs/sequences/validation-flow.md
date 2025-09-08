# Validation Flow

## Purpose
This diagram shows the sequence of events for validating the RDF data against a set of rules (SHACL shapes). It illustrates how the `validate_pim.sh` script works and how errors are reported.

## Diagram
```mermaid
sequenceDiagram
    participant Developer
    participant CLI as Command Line
    participant Validator as Validation Script (`validate_pim.sh`)
    participant Engine as SHACL Engine (e.g., `pyshacl`)
    participant Files as RDF Data & SHACL Shapes

    Developer->>CLI: 1. Runs `util/validate_pim.sh` after changing data
    CLI->>Validator: 2. Executes the validation script

    Validator->>Engine: 3. Invokes the SHACL engine
    note right of Validator: Passes data and shape files to engine

    Engine->>Files: 4. Loads RDF data and SHACL shape files

    alt Data is Valid
        Files-->>Engine: 5a. Data conforms to shapes
        Engine-->>Validator: 6a. Returns success status
        Validator-->>CLI: 7a. Prints success message to stdout
        CLI-->>Developer: 8a. Sees "Validation successful" message
    else Data is Invalid
        Files-->>Engine: 5b. Data violates one or more shapes
        Engine-->>Validator: 6b. Returns validation report with violations
        Validator-->>CLI: 7b. Prints detailed report to stderr
        CLI-->>Developer: 8b. Sees specific error messages and exits with non-zero code
    end
```

## Key Participants
- **Developer**: The user who modified the data and wants to check its validity. This role is played by the CI pipeline in automated workflows.
- **Command Line (CLI)**: The interface through which the user runs the script.
- **Validation Script (`validate_pim.sh`)**: The main script that orchestrates the validation process.
- **SHACL Engine**: The underlying tool (e.g., `pyshacl`) that performs the actual validation of data against shapes.
- **Files**: The RDF data files (`.ttl`) and the SHACL shape files (`.ttl`) that serve as input to the engine.

## Notes
- This validation process is crucial for maintaining data quality and consistency in the knowledge base.
- The GitHub Actions CI pipeline runs this script automatically on every push and pull request, preventing invalid data from being merged.

## Related Diagrams
- [Data Processing Pipeline](../flows/data-pipeline.md)
