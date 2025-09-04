# SPARQL Query Flow

## Purpose
This diagram illustrates the sequence of events that occur when a user interacts with the web interface to query and view data. It shows the communication between the browser, the web application's JavaScript, and the backend SPARQL server.

## Diagram
```mermaid
sequenceDiagram
    participant User
    participant Browser as Web Browser
    participant WebApp as Web App (JavaScript)
    participant Fuseki as Apache Fuseki Server
    participant RDFData as RDF Graph (`merged.ttl`)

    User->>Browser: 1. Interacts with UI (e.g., clicks 'Show Tasks')
    Browser->>WebApp: 2. Triggers JavaScript event handler

    WebApp->>Fuseki: 3. Sends SPARQL query via HTTP Request
    note right of WebApp: Query is sent to /pim/query endpoint

    Fuseki->>RDFData: 4. Executes SPARQL query against the graph
    RDFData-->>Fuseki: 5. Returns raw query results

    Fuseki-->>WebApp: 6. Returns results in HTTP Response (JSON format)

    WebApp->>Browser: 7. Parses JSON results and updates the DOM
    Browser->>User: 8. Renders and displays the updated data
```

## Key Participants
- **User**: The person interacting with the system.
- **Web Browser**: Renders the HTML and executes the JavaScript of the web application.
- **Web App (JavaScript)**: The client-side code that handles user interactions, constructs SPARQL queries, communicates with the backend, and manipulates the DOM.
- **Apache Fuseki Server**: The backend SPARQL server that receives queries, executes them against the data, and returns results.
- **RDF Graph (`merged.ttl`)**: The actual data store that is queried by Fuseki.

## Notes
- This flow describes how the interactive web dashboard (`web/index.html`) works.
- A similar, but simpler, flow occurs when using the command-line query tool (`util/run_query.py`), where the script acts as the client instead of the browser and web app.

## Related Diagrams
- [Deployment Architecture](../architecture/deployment.md)
- [System Architecture Overview](../architecture/system-overview.md)
