# Class Relationships Diagram

## Purpose
This diagram shows the main RDF classes used in the `pim_rdf` knowledge base and the relationships (properties) that link them. It provides a conceptual overview of the data model.

## Diagram
```mermaid
classDiagram
    direction TB

    class Task {
        <<RDF Class: pim:Task / schema:Action>>
        +dcterms:title
        +pim:status
        +pim:priority
        +dcterms:created
    }

    class Project {
        <<RDF Class: pim:Project>>
        +dcterms:title
        +dcterms:description
    }

    class Note {
        <<RDF Class: schema:CreativeWork>>
        +dcterms:title
        +schema:text
        +dcterms:created
    }

    class Contact {
        <<RDF Class: foaf:Person>>
        +foaf:name
        +foaf:mbox
        +foaf:phone
    }

    class Event {
        <<RDF Class: ical:Vevent>>
        +dcterms:title
        +ical:dtstart
        +ical:location
    }

    class Tag {
        <<RDF Class: skos:Concept>>
        +skos:prefLabel
    }

    Task "1" -- "0..1" Project : pim:project
    Task "N" -- "M" Tag : dcterms:subject
    Note "N" -- "M" Tag : dcterms:subject
    Event "N" -- "M" Tag : dcterms:subject
```

## Key Components
- **Task (`pim:Task` or `schema:Action`)**: Represents a to-do item. It has a title, status, priority, and can be linked to a project.
- **Project (`pim:Project`)**: A container for tasks.
- **Note (`schema:CreativeWork`)**: A piece of text, like a note or a document.
- **Contact (`foaf:Person`)**: Represents a person with contact details.
- **Event (`ical:Vevent`)**: A calendar event with a date and location.
- **Tag (`skos:Concept`)**: A keyword or topic that can be used to categorize other resources.

## Notes
- The diagram uses common RDF vocabularies like `dcterms` (Dublin Core), `foaf` (Friend of a Friend), `ical`, and `skos` to model entities.
- The `pim:` prefix refers to the small, custom vocabulary defined in this project for concepts not covered by standard vocabularies.
- The `dcterms:subject` property is used to link resources to tags.
- The model is evolving, with a recommendation to use `schema:Action` instead of `pim:Task`.

## Related Diagrams
- [Module Dependencies](./dependencies.md)
