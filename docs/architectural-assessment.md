# Architectural Assessment and Improvement Suggestions

This document provides an assessment of the `pim_rdf` repository's architecture as of September 2025. It highlights areas of strength and proposes specific, prioritized improvements to enhance the project's maintainability, robustness, and consistency.

## Overall Assessment

The project has a strong and clear architectural vision centered on local-first, plain-text RDF data, modularity, and interoperability through standard vocabularies. The developer experience is well-supported by detailed documentation and excellent tooling, particularly the `util/validate_pim.sh` script.

The primary architectural challenge is a significant "drift" between the documented best practices and the current state of the implementation. Several well-researched architectural improvements have been documented but not yet implemented, and the existing data validation mechanisms are not being used to their full potential.

The following suggestions are prioritized to address these gaps and build upon the project's solid foundation.

---

## High Priority Improvements

These items address major gaps in the project's data integrity and consistency.

### A1: Implement the Task Model Migration

- **Observation:** The `TASK_MODEL_EVALUATION.md` document provides an excellent, well-reasoned recommendation to migrate the task data model from the custom `pim:Task` vocabulary to the standard `schema:Action`. However, the core data (`data/tasks.ttl`) and all code that interacts with it (`export.py`, `web/sparql-client.js`) still use the old `pim:Task` model.
- **Suggestion:** Execute the migration plan outlined in the evaluation document. This involves updating the `data/tasks.ttl` file, all relevant SPARQL queries, and SHACL shapes to use `schema:Action` and its associated properties.
- **Rationale:** This is the single most impactful architectural improvement. It will significantly enhance the interoperability and semantic richness of the project's data, aligning it with widely used web standards.

### A2: Fix and Expand SHACL Validation

- **Observation:** The project's data validation strategy is its weakest area.
    1.  SHACL shapes, the most robust form of validation available here, only exist for "notes". Core domains like tasks, projects, and contacts have no formal schema validation.
    2.  The one existing shape file, `shapes/notes-shapes.ttl`, is **ineffective** because it targets the class `:Note`, while the data uses `schema:CreativeWork`.
- **Suggestion:**
    1.  Fix `shapes/notes-shapes.ttl` by changing `sh:targetClass` to `schema:CreativeWork`.
    2.  Create new SHACL shape files for all other core data domains, starting with `tasks-shapes.ttl`. This shape should enforce constraints based on the new `schema:Action` model (e.g., ensuring `schema:actionStatus` has the correct values).
- **Rationale:** A robust validation layer is critical for maintaining data quality and consistency, especially in a plain-text-based system. This change makes the validation strategy effective and comprehensive.

---

## Medium Priority Improvements

These items address inconsistencies and maintainability issues that affect the developer experience.

### B1: Align Documentation with Reality

- **Observation:** There are multiple instances of "documentation drift," where the documentation describes a desired or outdated state rather than the current implementation.
    - The CI process is documented as using Python-based tools but actually uses a Nix environment with Jena.
    - The data model for tasks is documented as `schema:Action` but implemented as `pim:Task`.
    - The URI naming conventions in the `README.md` do not match what is used in the data.
- **Suggestion:** Conduct a thorough review of all documentation and align it with the current state of the codebase. If the code is lagging behind a desired state (like the task model), the documentation should be updated to reflect the current reality while noting the intended future direction.
- **Rationale:** Accurate documentation is crucial for developer onboarding and long-term maintainability. Resolving these inconsistencies will prevent confusion and streamline development.

### B2: Centralize Configuration Management

- **Observation:** The `export.py` script uses a hardcoded list of `.ttl` files to load, which is inconsistent with the `util/validate_pim.sh` script that correctly uses `config/domains.yaml`.
- **Suggestion:** Refactor `export.py` to parse `config/domains.yaml` to get the list of data files to include in the export. This may require adding a lightweight YAML parsing library (like `PyYAML`) as a dependency or using a simple regex-based parser to avoid new dependencies.
- **Rationale:** Using a single, central configuration file for defining the project's data domains improves consistency and makes the system easier to extend.

### B3: Standardize the Tagging Vocabulary

- **Observation:** Notes are linked to tags using the custom, undefined property `:hasTag`. The tags themselves are correctly modeled as `skos:Concept`.
- **Suggestion:** Replace the use of `:hasTag` with a standard property, such as `dcterms:subject` or `schema:about`. This would involve updating `data/notes.ttl` and any SPARQL queries that rely on this property. A formal definition for the chosen property should be added to `data/base.ttl`.
- **Rationale:** Using standard, well-defined properties improves the interoperability and semantic clarity of the data, making it more understandable to other linked data tools.

### B4: Improve Code Robustness

- **Observation:**
    - The `ics_bridge.py` script uses brittle string manipulation to parse dates and times.
    - The `validate_pim.sh` script uses `grep` and `sed` to parse YAML files, which is not robust.
- **Suggestion:**
    - Refactor the date/time handling in `ics_bridge.py` to use Python's `datetime.fromisoformat` for more reliable parsing.
    - Consider adding a more robust YAML parser like `yq` to the Nix environment to make the validation script more resilient to formatting changes.
- **Rationale:** These changes will make the tooling more robust and less likely to fail on valid, but slightly different, data or configuration formats.

---

## Low Priority Improvements

These items are "nice-to-have" improvements that would polish the architecture but are less critical than the items above.

### C1: Externalize Queries and Templates

- **Observation:** SPARQL queries and HTML/CSS templates are embedded as multiline strings directly within the Python and JavaScript files.
- **Suggestion:** For better separation of concerns, consider moving SPARQL queries to dedicated `.sparql` files and using a simple templating engine (like Jinja2) for HTML generation in `export.py`.
- **Rationale:** This would improve maintainability, especially if the number of queries or the complexity of the HTML pages grows over time.

### C2: Clarify the Developer Setup Process

- **Observation:** The project can be set up using `pip` or `nix-shell`. However, only the `nix-shell` environment provides the Java-based Jena tools required to run the full `validate_pim.sh` script.
- **Suggestion:** Update the `README.md` and developer instructions to more clearly state that `nix-shell` is the primary, recommended development environment for access to all tooling.
- **Rationale:** This will prevent confusion for new developers and ensure everyone is using the same consistent, fully-featured environment.
