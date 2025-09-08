# Proposals for a Native-Format PIM Approach

This document outlines three concrete proposals for implementing a personal information management (PIM) system based on the "native-format" architecture, where data is kept in its original format—or a general-purpose one like SQLite—and processed with specialized tools.

## Proposal 1: The Datasette Ecosystem

This proposal centers around the [Datasette](https://datasette.io/) tool and its ecosystem. Datasette is a tool for exploring and publishing data. It is built on top of SQLite, but it can import data from a wide variety of formats.

### Core Idea
The core of this approach is to convert various data formats (VCF, iCal, GeoJSON, etc.) into a collection of SQLite databases. Datasette can then be used to provide a web-based UI for exploring, querying, and visualizing this data.

### Implementation
1.  **Data Ingestion:** Use tools like `sqlite-utils` to create command-line scripts that convert native-format files into SQLite tables. For example, a script could parse a `.vcf` file and create a `contacts` table in a `pim.db` SQLite file.
2.  **Data Exploration:** Run Datasette on the resulting SQLite files. This immediately provides a web interface for browsing the data, running SQL queries, and creating simple visualizations.
3.  **Ad-Hoc Analysis:** For more complex analysis, you can either use the Datasette API to pull data into other tools, or you can write Python scripts that directly query the SQLite databases.

### Advantages
-   **Rapid Prototyping:** It is very fast to get from raw files to a browsable, queryable web interface.
-   **Rich UI:** Datasette provides a user-friendly interface for non-technical users.
-   **Extensible:** The Datasette ecosystem includes many plugins for adding new functionality, such as full-text search, mapping, and charting.

## Proposal 2: The Command-Line First Approach

This proposal is for users who are comfortable working on the command line. It relies on a collection of standard Unix tools and specialized command-line utilities to work with data in its native format.

### Core Idea
The filesystem is the database. A collection of shell scripts and simple programs are used to perform CRUD (Create, Read, Update, Delete) operations and to run queries.

### Implementation
1.  **Data Storage:** Data is stored in a well-defined directory structure (e.g., `~/pim/contacts/`, `~/pim/notes/`).
2.  **Tooling:** A combination of general-purpose and specialized tools are used to manipulate the data.
    -   **General:** `grep`, `sed`, `awk`, `find` for text-based formats.
    -   **Specialized:** `jq` for JSON, `yq` for YAML, `vcf-cli` for VCF files, `ics-tools` for iCalendar.
3.  **Scripting:** Small shell or Python scripts are written to perform common tasks (e.g., a `find-contact` script that greps through `.vcf` files).

### Advantages
-   **Simplicity and Transparency:** This approach is very transparent. The data is just files, and the tools are standard.
-   **Composability:** The Unix philosophy of small, composable tools allows for powerful and flexible workflows.
-   **Minimal Dependencies:** This approach can be implemented with a very small set of dependencies, many of which are already installed on most systems.

## Proposal 3: The Hybrid Indexing Approach

This proposal offers a middle ground between the full RDF conversion and the pure native-format approach. It keeps data in its native format but creates a lightweight index to facilitate cross-domain querying.

### Core Idea
The original data files are the source of truth. A background process runs periodically to scan these files and update a search index. This index can then be queried to find information across different domains.

### Implementation
1.  **Data Storage:** As with the command-line approach, data is stored in native formats in a well-organized directory structure.
2.  **Indexing:** An indexing script is created. This script knows how to parse the different data formats and extracts key information to be indexed. There are several options for the index itself:
    -   **Full-Text Search Index:** Tools like [MeiliSearch](https://www.meilisearch.com/) or a simple SQLite FTS5 table can be used to create a powerful full-text search index.
    -   **Lightweight RDF Index:** The script could generate a small RDF file containing only the most important entities and relationships (e.g., names, dates, links between items). This would allow for some semantic querying without requiring a full data conversion.
3.  **Querying:** A simple query tool (e.g., a web interface or a command-line script) is created to interact with the index. The query results would typically be links to the original files.

### Advantages
-   **Balanced Approach:** This approach combines the low friction of native formats with some of the powerful query capabilities of a centralized index.
-   **Fast Queries:** Queries against a dedicated index will be much faster than ad-hoc parsing of files.
-   **Resilience:** If the index is lost or corrupted, it can be rebuilt from the original source files.
