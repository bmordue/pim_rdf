# Task Model Vocabulary Evaluation

## Executive Summary

This document evaluates the feasibility and benefits of mapping or replacing the current custom PIM task model with standardized vocabularies: **schema.org Action** or **ActivityStreams 2.0**. 

**Recommendation**: Use **schema.org Action** as the primary vocabulary with selective custom property retention for PIM-specific needs.

## Current Custom Task Model Analysis

### Current Vocabulary
```turtle
@prefix pim: <https://ben.example/ns/pim#> .

pim:Task      a rdfs:Class .
pim:Project   a rdfs:Class .

# Task properties
pim:status    a rdf:Property ; rdfs:range xsd:string .   # "todo" | "doing" | "done"
pim:priority  a rdf:Property ; rdfs:range xsd:integer .
pim:blockedBy a rdf:Property ; rdfs:range rdfs:Resource .
pim:estimate  a rdf:Property ; rdfs:range xsd:duration .
pim:inbox     a rdf:Property ; rdfs:range xsd:boolean .
pim:project   a rdf:Property ; rdfs:range rdfs:Resource .
```

### Current Task Example
```turtle
:task-2025-08-14-abc123
  a pim:Task ;
  dcterms:title "Draft personal data model overview" ;
  dcterms:created "2025-08-14T10:05:00Z"^^xsd:dateTime ;
  pim:status "todo" ;
  pim:priority 2 ;
  pim:inbox true ;
  pim:project :project-2025-07-website .
```

### Strengths
- Simple and intuitive for personal use
- Covers essential task management needs
- Minimal complexity
- Clear semantics for status transitions

### Limitations
- Not interoperable with external systems
- Limited semantic richness
- No standardization benefits
- Missing common task concepts (assignee, due date, etc.)

## Schema.org Action Vocabulary Analysis

### Core Action Classes
```turtle
@prefix schema: <https://schema.org/> .

schema:Action          # Base class for all actions
schema:UpdateAction    # Suitable for task updates
schema:CreateAction    # For task creation
schema:DeleteAction    # For task completion/deletion
```

### Relevant Properties
```turtle
# Status and lifecycle
schema:actionStatus    # Potential, Active, Completed, Failed
schema:startTime       # When task started
schema:endTime         # When task completed
schema:duration        # Estimated or actual duration

# Relationships
schema:agent           # Who performs the action (assignee)
schema:object          # What the action operates on
schema:result          # Outcome of the action
schema:isPartOf        # Project relationship

# Descriptive
schema:name            # Task title
schema:description     # Task description
schema:identifier      # Task ID
```

### Property Mapping

| Current Property | Schema.org Equivalent | Notes |
|-----------------|----------------------|-------|
| `pim:Task` | `schema:Action` | Direct class mapping |
| `pim:status` | `schema:actionStatus` | Values: "PotentialActionStatus", "ActiveActionStatus", "CompletedActionStatus" |
| `pim:priority` | *No direct equivalent* | Could use custom or schema:orderNumber |
| `pim:blockedBy` | `schema:prerequisite` | Close semantic match |
| `pim:estimate` | `schema:duration` | Direct mapping for estimated duration |
| `pim:inbox` | *No equivalent* | PIM-specific concept |
| `pim:project` | `schema:isPartOf` | Project as containing entity |

### Example Task with Schema.org
```turtle
:task-2025-08-14-abc123
  a schema:Action ;
  schema:name "Draft personal data model overview" ;
  schema:actionStatus schema:PotentialActionStatus ;
  schema:agent :Ben ;
  schema:isPartOf :project-2025-07-website ;
  schema:duration "PT2H"^^xsd:duration ;
  dcterms:created "2025-08-14T10:05:00Z"^^xsd:dateTime ;
  pim:priority 2 ;
  pim:inbox true .
```

## ActivityStreams 2.0 Vocabulary Analysis

### Core Activity Classes
```turtle
@prefix as: <https://www.w3.org/ns/activitystreams#> .

as:Activity       # Base class for activities
as:Create         # Creating content/tasks
as:Update         # Updating tasks
as:Delete         # Removing tasks
as:Accept         # Accepting/starting tasks
as:Complete       # Task completion (non-standard but logical)
```

### Relevant Properties
```turtle
# Core activity properties
as:actor          # Who performs the activity
as:object         # The task being acted upon
as:published      # When created
as:updated        # When last modified
as:startTime      # Activity start
as:endTime        # Activity end

# Context
as:context        # Project or context
as:target         # Where activity is directed
as:inReplyTo      # Dependencies/blocking
```

### Property Mapping

| Current Property | ActivityStreams Equivalent | Notes |
|-----------------|----------------------------|-------|
| `pim:Task` | `as:Activity` | Activities represent tasks |
| `pim:status` | *Activity type* | Use Create→Update→Complete activity sequence |
| `pim:priority` | *No equivalent* | Would need custom extension |
| `pim:blockedBy` | `as:inReplyTo` | Loose semantic match |
| `pim:estimate` | *No direct equivalent* | Could use as:duration (non-standard) |
| `pim:inbox` | *No equivalent* | PIM-specific concept |
| `pim:project` | `as:context` | Project as activity context |

### Example Task with ActivityStreams 2.0
```turtle
:task-2025-08-14-abc123
  a as:Activity ;
  as:name "Draft personal data model overview" ;
  as:actor :Ben ;
  as:context :project-2025-07-website ;
  as:published "2025-08-14T10:05:00Z"^^xsd:dateTime ;
  pim:priority 2 ;
  pim:inbox true .
```

## Comparative Analysis

### 1. Compatibility Assessment

#### Schema.org Action
- **High compatibility** (8/10)
- Direct mappings for most properties
- Clear semantic alignment with task concepts
- Well-established in web standards

#### ActivityStreams 2.0  
- **Medium compatibility** (6/10)
- Less direct mapping to task management
- More focused on social/collaborative activities
- Status representation through activity types is less intuitive

### 2. Expressiveness Comparison

#### Schema.org Action
- **Rich expressiveness** for task management
- Built-in status vocabulary (Potential/Active/Completed)
- Duration and timing properties
- Agent/object relationships
- Extensible with additional schema.org properties

#### ActivityStreams 2.0
- **Limited expressiveness** for task management
- Better for activity streams and social features
- Temporal properties available
- Less task-specific semantics

### 3. Ecosystem Support

#### Schema.org Action
- **Excellent ecosystem support**
- Widely adopted by major platforms (Google, Microsoft, etc.)
- Rich tooling and validation support
- JSON-LD integration standard
- Search engine optimization benefits

#### ActivityStreams 2.0
- **Good but specialized support**
- Primary use in social platforms (Mastodon, etc.)
- W3C standard with solid specification
- Less mainstream adoption for task management
- Strong in federated/social contexts

## Migration Strategies

### Option 1: Full Schema.org Migration (Recommended)

**Benefits:**
- Maximum interoperability
- Rich ecosystem support
- Future-proof vocabulary
- SEO and discoverability benefits

**Implementation:**
```turtle
# New vocabulary mapping
@prefix schema: <https://schema.org/> .

# Migrate classes
pim:Task → schema:Action

# Migrate properties  
pim:status → schema:actionStatus
pim:estimate → schema:duration
pim:blockedBy → schema:prerequisite
pim:project → schema:isPartOf

# Retain custom properties where needed
pim:priority (no schema.org equivalent)
pim:inbox (PIM-specific)
```

### Option 2: Hybrid Approach 

**Benefits:**
- Gradual migration path
- Retain custom properties
- Add interoperability gradually

**Implementation:**
```turtle
:task-example
  a schema:Action, pim:Task ;  # Multiple types
  schema:name "Task title" ;
  schema:actionStatus schema:PotentialActionStatus ;
  pim:priority 2 ;
  pim:inbox true .
```

### Option 3: Custom Extensions to Schema.org

**Benefits:**
- Full schema.org compliance
- Formal extension vocabulary
- Maximum interoperability

**Implementation:**
```turtle
@prefix pim: <https://ben.example/ns/pim#> .

# Extend schema.org Action
pim:priority rdfs:subPropertyOf schema:additionalProperty .
pim:inbox rdfs:subPropertyOf schema:additionalProperty .
```

## Recommendations

### 1. Primary Recommendation: Schema.org Action

**Adopt schema.org Action as the primary vocabulary** for the following reasons:

1. **Best semantic fit**: Actions naturally represent tasks and todo items
2. **Rich property set**: Comprehensive properties for task management
3. **Ecosystem benefits**: Broad adoption and tooling support
4. **Future-proof**: Stable, evolving standard with industry backing
5. **Interoperability**: Works with existing tools and platforms

### 2. Implementation Strategy

**Phase 1: Core Migration**
- Replace `pim:Task` with `schema:Action`
- Map `pim:status` to `schema:actionStatus`
- Map `pim:estimate` to `schema:duration`
- Map `pim:blockedBy` to `schema:prerequisite`
- Map `pim:project` to `schema:isPartOf`

**Phase 2: Custom Property Integration**
- Retain `pim:priority` as custom property
- Retain `pim:inbox` as custom property
- Document as formal extensions

**Phase 3: Enhanced Semantics**
- Add `schema:agent` for task assignment
- Add timing properties (`schema:startTime`, `schema:endTime`)
- Consider additional schema.org properties as needed

### 3. Updated Task Example

```turtle
@prefix :       <https://ben.example/pim/> .
@prefix schema: <https://schema.org/> .
@prefix pim:    <https://ben.example/ns/pim#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .

:task-2025-08-14-abc123
  a schema:Action ;
  schema:name "Draft personal data model overview" ;
  schema:description "Create comprehensive overview of RDF-based personal data model" ;
  schema:actionStatus schema:PotentialActionStatus ;
  schema:agent :Ben ;
  schema:isPartOf :project-2025-07-website ;
  schema:duration "PT2H"^^xsd:duration ;
  schema:prerequisite :task-research-rdf-patterns ;
  dcterms:created "2025-08-14T10:05:00Z"^^xsd:dateTime ;
  pim:priority 2 ;
  pim:inbox true .
```

## Migration Impact Assessment

### SPARQL Queries Impact
Current queries would need updates:
```sparql
# Before
SELECT ?task ?title ?status ?priority
WHERE {
  ?task a pim:Task ;
        dcterms:title ?title ;
        pim:status ?status ;
        pim:priority ?priority .
  FILTER(?status != "done")
}

# After  
SELECT ?task ?title ?status ?priority
WHERE {
  ?task a schema:Action ;
        schema:name ?title ;
        schema:actionStatus ?status ;
        pim:priority ?priority .
  FILTER(?status != schema:CompletedActionStatus)
}
```

### SHACL Shapes Impact
Shapes would need updating for new vocabulary:
```turtle
# New TaskShape for schema:Action
schema:ActionTaskShape
  a sh:NodeShape ;
  sh:targetClass schema:Action ;
  sh:property [
    sh:path schema:actionStatus ;
    sh:in (schema:PotentialActionStatus schema:ActiveActionStatus schema:CompletedActionStatus) ;
  ] ;
  sh:property [
    sh:path pim:priority ;
    sh:datatype xsd:integer ;
    sh:minInclusive 0 ;
    sh:maxInclusive 5 ;
  ] .
```

## Conclusion

**Schema.org Action provides the optimal balance** of semantic richness, ecosystem support, and compatibility for the PIM task model. The migration would:

1. Improve interoperability with external tools
2. Provide richer semantic representation
3. Enable better discoverability and integration
4. Maintain backward compatibility through hybrid approach
5. Position the system for future enhancements

The recommended approach preserves existing PIM-specific properties while gaining the benefits of a standardized, widely-adopted vocabulary.