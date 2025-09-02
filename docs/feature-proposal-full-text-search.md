# Feature Proposal: Full-Text Search Interface

## 1. Summary

This proposal outlines the implementation of a full-text search feature for the PIM RDF project. While the data is structured, much of its value is in text literals within notes, tasks, and other resources. A robust search interface would allow users to quickly find information across their entire knowledge base using keywords, similar to a personal search engine.

## 2. Problem

Currently, finding specific information requires either:
- Knowing which file the information is in and manually searching it.
- Writing a custom SPARQL query with `FILTER CONTAINS()` or `REGEX()` clauses.

These methods are inefficient for everyday use and require technical knowledge. There is no simple, user-friendly way to search for a term across all `.ttl` files at once. The `README.md` identifies this as a potential roadmap item ("Text search via Jena Text index").

## 3. Proposed Solution

Integrate a full-text search index with the Apache Jena Fuseki server and create a simple search interface in the web dashboard.

### Key Features

- **Global Search Bar:** A single search bar, prominently displayed in the web interface, that allows users to enter search terms.
- **Keyword Search:** Users can type one or more keywords to search across all text-based properties (e.g., `dcterms:title`, `dcterms:description`, `schema:text`).
- **Ranked Results:** Search results should be ranked by relevance, with the best matches appearing first.
- **Result Snippets:** The search results page should display the title of the resource, its type (e.g., Note, Task), and a snippet of the text containing the search term for context.
- **Direct Links:** Each search result should link directly to the detailed view of that resource in the web interface.

### Technical Approach

1.  **Backend (Jena Text Index):**
    -   Configure the Apache Jena Fuseki server to use its text indexing module (`jena-text`). This module leverages Apache Lucene to create a powerful search index from the RDF data.
    -   Create a configuration file (e.g., `fuseki-config.ttl`) that defines which properties should be indexed. For example, we would index `dcterms:title`, `schema:text`, `dcterms:description`, etc.
    -   The server will automatically keep the index in sync with the RDF data.
2.  **SPARQL Queries:**
    -   Use the `text:query` property in SPARQL to query the Lucene index. A typical query would look like this:
        ```sparql
        PREFIX text: <http://jena.apache.org/text#>
        SELECT ?subject ?title
        WHERE {
          ?subject text:query "my search term" ;
                   dcterms:title ?title .
        }
        ```
3.  **Frontend:**
    -   Add a search input component to the interactive dashboard.
    -   When the user submits a search, the frontend will execute the SPARQL query against the Fuseki endpoint.
    -   A new "Search Results" view will be created to display the results returned by the query.

## 4. Benefits

- **Greatly Increased Discoverability:** Users can find information instantly without needing to remember where it is stored.
- **Lower Barrier to Entry:** Makes the PIM more accessible to non-technical users who are comfortable with search interfaces.
- **Unlocks Value of Unstructured Data:** The value of detailed notes and descriptions is fully realized when they are easily searchable.
- **Efficient and Scalable:** Jena's text index is highly optimized and can handle a large amount of text data without significant performance degradation.

## 5. Next Steps

1.  **Setup Jena Text:** Configure a local Fuseki server with `jena-text` and create an index of the sample data.
2.  **Develop Search Query:** Write and test a SPARQL query that uses the `text:query` property.
3.  **Build UI Prototype:** Create a basic search bar and results page in the frontend application.
4.  **Integration:** Connect the UI to the backend query.
5.  **Refinement:** Add features like result highlighting and ranking.
