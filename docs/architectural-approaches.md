# Architectural Approaches to Personal Information Management

This document provides a high-level overview of two distinct architectural approaches to managing personal information: the "RDF-first" model that underpins this project, and an alternative "native-format" approach.

## 1. The RDF-First Approach

The core idea of the RDF-first approach is to create a single, unified data model for all personal information. Data from various sources—contacts, notes, events, bookmarks—is converted into a common format, the Resource Description Framework (RDF). This creates a personal knowledge graph.

### Key Characteristics
- **Unified Data Model:** All data conforms to a predefined set of ontologies (e.g., FOAF for people, SKOS for concepts, Schema.org for common entities).
- **Centralized Knowledge Graph:** Data is stored in one or more RDF files (e.g., Turtle/TTL), which collectively form a single, queryable graph.
- **Rich, Semantic Queries:** SPARQL can be used to perform complex queries that traverse relationships across different domains (e.g., "show me all notes written about people I met at events in the last month").
- **Data-as-Code:** The use of plain-text formats like Turtle allows the knowledge base to be versioned with tools like Git.

### Advantages
- **Powerful Queries:** The ability to query across different types of information is the primary strength of this approach.
- **Interoperability:** By using standard vocabularies, the data is highly interoperable with other RDF-based tools and systems.
- **Consistency:** A single data model enforces consistency across all information domains.

### Disadvantages
- **Upfront Investment:** Data must be converted into RDF, which requires building and maintaining import/export scripts. This can be a barrier to entry.
- **Loss of Fidelity:** Converting data to RDF can sometimes result in the loss of information specific to the original format.
- **Tooling:** While powerful, RDF and SPARQL are not as widely used as other data technologies, and the tooling can be less mature or user-friendly for some use cases.

### Real-World Parallels
- **Project Chandler:** This discontinued PIM aimed to create a unified, "free-form" information model, sharing the goal of a single, flexible representation for different data types.
- **Zettelkasten:** While typically less structured, the Zettelkasten method's emphasis on creating a networked web of thoughts mirrors RDF's linked data principles at a conceptual level.

## 2. The Native-Format Approach

The native-format approach (also known as "polyglot persistence") advocates for keeping data in its original, most suitable format. Instead of a single, unified data store, this approach uses a collection of specialized tools to work with a variety of file types.

### Key Characteristics
- **Best Tool for the Job:** Each type of data is stored in a format for which excellent tooling already exists (e.g., VCF for contacts, GeoJSON for locations, Markdown for notes).
- **Decentralized Data:** Information is spread across multiple files and formats.
- **Ad-Hoc Analysis:** Cross-domain queries and analysis are performed on an as-needed basis using scripts and command-line tools that can read and process the different formats.
- **Filesystem as Database:** The filesystem itself is the primary organizational tool.

### Advantages
- **Low Friction:** New information can be added easily, as there is no need for a conversion step. You can use any application that produces a standard file format.
- **Leverages Existing Tools:** This approach benefits from the rich ecosystem of existing tools for working with common data formats (e.g., `jq` for JSON, `ripgrep` for text search).
- **Resilience:** Since data is not tied to a single, monolithic system, the failure or obsolescence of one tool does not affect the others.

### Disadvantages
- **Complex Cross-Domain Queries:** Answering questions that span multiple data types can be difficult. For example, "show me all notes about people I met at events" would require scripting to parse VCF, iCalendar, and Markdown files and then join the information.
- **Inconsistency:** Without a unifying schema, it is easy for data to become inconsistent across different files and formats.
- **Discoverability:** It can be harder to get a holistic view of the data when it is spread across many different files and formats.

### Real-World Parallels
- **Datasette:** This project exemplifies a native-format approach. Its ecosystem includes tools to convert data from common formats like CSV and JSON into SQLite databases, which can then be instantly explored and published via a web interface and API. While a conversion step is often needed, it focuses on using a general-purpose, file-based database rather than a specialized graph model.
- **Personal Wikis:** A personal wiki is a collection of documents (often Markdown) that are linked together. This is a form of native-format PIM, where the primary data type is the text document.
- **KDE PIM (Kontact):** While presented as a unified suite, KDE PIM is composed of several applications, each managing its own data store. This is a form of native-format management at the application level, though the user sees an integrated whole.
