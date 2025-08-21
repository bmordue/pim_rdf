# Feature Proposal: Improved Data/Logic Separation

## Executive Summary

This proposal addresses the need for cleaner separation between data and logic in the PIM RDF personal knowledge base project. While the project already demonstrates good domain-level separation (tasks, notes, contacts in separate TTL files), several areas mix application logic with data concerns, creating maintenance challenges and reducing flexibility.

## Problem Statement

### Current Issues

1. **Hardcoded Queries in Application Code**
   - The `validate_pim.py` script contains three SPARQL queries directly embedded in Python code
   - This makes queries non-reusable and requires code changes for query modifications
   - Queries are not discoverable or manageable as standalone artifacts

2. **Hardcoded Data Structure Dependencies**
   - The `merge_data_files()` function contains a hardcoded list: `['base.ttl', 'tasks.ttl', 'notes.ttl', ...]`
   - Adding new data domains requires modifying application code
   - The `validate_shacl_shapes()` function has hardcoded file mappings

3. **Mixed Configuration Concerns**
   - `config-pim.ttl` mixes server configuration with hardcoded data file paths
   - Infrastructure configuration is coupled with data location concerns

4. **Inconsistent Query Organization**
   - Some queries exist in the `queries/` directory as standalone files
   - Other queries are embedded in Python code
   - No clear pattern for when to use which approach

## Proposed Solution

### 1. Externalize All Queries

**Current State:**
```python
queries = [
    ("List all tasks", """
PREFIX pim: <https://ben.example/ns/pim#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?task ?title ?status ?priority
WHERE { ... }
""")
]
```

**Proposed State:**
- Move all embedded queries to the `queries/` directory
- Create standardized query files: `validation-list-tasks.sparql`, `validation-list-creativeworks.sparql`, `validation-count-by-type.sparql`
- Load queries dynamically from files at runtime

### 2. Configuration-Driven Data Discovery

**Current State:**
```python
data_files = ['base.ttl', 'tasks.ttl', 'notes.ttl', 'contacts.ttl', 
              'projects.ttl', 'bookmarks.ttl', 'events.ttl', 'tags.ttl']
```

**Proposed State:**
- Create a `config.yaml` or `config.ttl` file defining data domains and their properties
- Implement automatic discovery of TTL files based on naming conventions
- Support metadata about each domain (description, validation shapes, etc.)

### 3. Declarative Validation Configuration

**Current State:**
```python
data_files = {
    'notes.ttl': 'notes-shapes.ttl'
}
```

**Proposed State:**
- Define validation mappings in configuration files
- Support multiple validation shapes per data file
- Enable conditional validation based on data content

### 4. Enhanced Query Management

**Benefits:**
- **Discoverability**: All queries in one location with descriptive names
- **Reusability**: Queries can be used by validation, web interfaces, and command-line tools
- **Maintainability**: Non-programmers can modify queries without touching Python code
- **Testing**: Individual queries can be tested and documented separately

### 5. Flexible Configuration Architecture

**Proposed Structure:**
```
config/
  ├── domains.yaml          # Data domain definitions
  ├── validation.yaml       # SHACL validation mappings
  └── fuseki-template.ttl    # Fuseki config template

queries/
  ├── validation/           # Queries used by validation script
  │   ├── list-tasks.sparql
  │   ├── list-creativeworks.sparql
  │   └── count-by-type.sparql
  └── user/                 # User-defined queries
      ├── dashboard.sparql
      └── notes_tagged_rdf_last_30_days.sparql
```

## Implementation Plan

### Phase 1: Query Externalization
1. Extract embedded queries from `validate_pim.py` to `queries/validation/`
2. Implement query loading mechanism in validation script
3. Update documentation with query naming conventions

### Phase 2: Configuration-Driven Discovery
1. Create domain configuration file
2. Implement automatic TTL file discovery
3. Update merge and validation logic to use configuration

### Phase 3: Validation Enhancement
1. Create validation configuration mapping
2. Support multiple shapes per domain
3. Add validation rule documentation

### Phase 4: Template-Based Configuration
1. Create Fuseki configuration template
2. Implement configuration generation based on discovered domains
3. Remove hardcoded paths from configuration files

## Benefits

### Immediate Benefits
- **Reduced Code Coupling**: Application logic separated from data queries
- **Improved Maintainability**: Changes to queries don't require code changes
- **Better Organization**: Clear separation of concerns between components

### Long-term Benefits
- **Extensibility**: Easy to add new data domains without code modifications
- **Tool Integration**: Queries can be used by multiple tools and interfaces
- **Documentation**: Query files serve as documentation of system capabilities
- **Testing**: Individual components can be tested in isolation

## Migration Strategy

### Backward Compatibility
- All changes will maintain backward compatibility with existing TTL files
- Current `validate_pim.py` functionality will be preserved
- Gradual migration allows incremental adoption

### Risk Mitigation
- Phase-based implementation reduces integration risk
- Existing validation tests ensure no regression
- Configuration validation prevents misconfiguration

### Success Metrics
- Zero regression in existing functionality
- Reduced lines of code in `validate_pim.py`
- Improved query discoverability (all queries in `queries/` directory)
- Configuration-driven operation (no hardcoded lists)

## Alternative Approaches Considered

### 1. Status Quo
**Pros**: Simple, everything works
**Cons**: Maintenance burden, inflexibility, mixed concerns

### 2. Complete Rewrite
**Pros**: Clean slate design
**Cons**: High risk, breaks existing workflows, over-engineering for project size

### 3. Minimal Refactoring (Chosen Approach)
**Pros**: Addresses key issues, maintains compatibility, manageable scope
**Cons**: Some complexity remains

## Conclusion

This proposal addresses legitimate separation of concerns issues while maintaining the project's simplicity and effectiveness. The phased approach allows gradual improvement without disrupting existing workflows, making it a practical solution for enhancing the project's maintainability and extensibility.

The changes will transform the project from having hardcoded dependencies to a configuration-driven architecture, enabling easier maintenance and future enhancements while preserving all current functionality.