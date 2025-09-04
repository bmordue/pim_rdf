# PIM-RDF Documentation

Welcome to the documentation for the `pim_rdf` project. This documentation consists of a series of diagrams that illustrate the architecture, components, and data flows of the system.

## Index of Diagrams

### 1. Architecture Diagrams

High-level diagrams that describe the overall system structure and deployment.

- **[System Architecture Overview](./architecture/system-overview.md)**
  A look at the major components of the system and how they interact, from data sources to consumers.

- **[Deployment Architecture](./architecture/deployment.md)**
  Illustrates the local development workflow, showing how a developer authors, validates, and interacts with the data.

### 2. Component Diagrams

Diagrams that show the internal components of the system and their relationships.

- **[Class Relationships](./components/class-diagram.md)**
  A conceptual overview of the main RDF classes (Task, Project, Note, etc.) and the properties that connect them.

- **[Module Dependencies](./components/dependencies.md)**
  Shows the dependencies between different modules, scripts, and data files in the project.

### 3. Flow & State Diagrams

Diagrams that illustrate processes, workflows, and state transitions within the system.

- **[Data Ingestion Flow](./flows/data-ingestion.md)**
  A flowchart showing how to import data from external sources (like VCF files) into the knowledge base.

- **[Data Processing Pipeline](./flows/data-pipeline.md)**
  Shows the end-to-end pipeline from raw data files to a queryable data service.

- **[Task State Machine](./flows/task-states.md)**
  A state diagram illustrating the lifecycle of a task (todo -> doing -> done).

### 4. Sequence Diagrams

Diagrams that model interactions between different parts of the system over time.

- **[SPARQL Query Flow](./sequences/sparql-query-flow.md)**
  Shows the sequence of events when the web interface queries the backend for data.

- **[Validation Flow](./sequences/validation-flow.md)**
  Illustrates how the data validation process works and how errors are handled.
