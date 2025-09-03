# Feature Proposal: Web-based Data Entry

**Author:** Jules
**Status:** Proposed
**Date:** 2025-09-02

## 1. Summary

This proposal outlines the addition of a web-based data entry system to the PIM application. The goal is to allow users to create new entities (such as notes, tasks, and bookmarks) directly from the web interface, lowering the barrier to entry and improving the convenience of daily use.

## 2. Motivation

Currently, adding data to the knowledge base requires users to manually edit `.ttl` files. This workflow is powerful for bulk editing and for users comfortable with RDF syntax, but it has several drawbacks:

-   **High Barrier to Entry:** New users must learn Turtle syntax before they can contribute.
-   **Inconvenience for Quick Capture:** Adding a simple note or task is cumbersome, especially on mobile devices.
-   **Error-Prone:** Manual editing can easily lead to syntax errors or violations of SHACL shapes.

A web-based form for data entry would make the system more accessible and easier to use for quick, atomic additions, complementing the existing file-based workflow.

## 3. Proposed Solution

The solution involves creating simple, intuitive web forms for each entity type and a backend API endpoint to handle form submissions, convert them to RDF, and append them to the appropriate `.ttl` file.

### 3.1. Frontend and UI/UX

-   **"Add New" Button:** A prominent "Add New" button will be added to the main dashboard and relevant pages (e.g., a "+" icon in the header).
-   **Entity Selection:** Clicking the button would reveal a choice of which entity to create (e.g., "Note", "Task", "Bookmark").
-   **Dynamic Forms:** Selecting an entity type will display a simple, clean form with fields corresponding to the data model. For example, the "Add Task" form would include:
    -   Title (text input)
    -   Project (dropdown, populated from existing `pim:Project` entities)
    -   Priority (number input or select)
    -   Status (dropdown: "todo", "doing", "done")
    -   Description (textarea, optional)
-   **Client-side Validation:** Basic client-side validation (e.g., for required fields) will provide immediate feedback.
-   **Technology:** The forms can be built using the existing lightweight stack (HTML, CSS, vanilla JavaScript) to keep the frontend simple and fast.

**Mockup: "Add Task" Form**

```
+------------------------------------------+
| Add New Task                             |
+------------------------------------------+
|                                          |
| Title: [______________________________]  |
|                                          |
| Project: [Select a project ▼]            |
|                                          |
| Priority: [ (2) ▼]  (0-5)                |
|                                          |
| Status: [todo ▼]                         |
|                                          |
| Description:                             |
| [______________________________________] |
| [______________________________________] |
|                                          |
|                [Create Task] [Cancel]    |
+------------------------------------------+
```

### 3.2. Backend API

A new API endpoint, e.g., `POST /api/add`, will be created to handle form submissions. This could be implemented in the existing `web/mock_server.py` or a new, more robust Python web server (e.g., using Flask or FastAPI).

-   **Request Format:** The frontend will send a JSON object representing the form data.
    ```json
    {
      "type": "task",
      "data": {
        "title": "Draft blog post",
        "project": "https://ben.example/pim/project-2025-07-website",
        "priority": 3,
        "status": "todo",
        "description": "A quick draft of the main points."
      }
    }
    ```
-   **Processing:**
    1.  The endpoint receives the JSON payload.
    2.  It validates and sanitizes the input data to prevent injection attacks.
    3.  It generates a new, unique URI for the entity (e.g., using the `date + short id` convention).
    4.  It constructs the RDF triples in Turtle format using a template or `rdflib`.
    5.  It appends the new triples to the corresponding file (e.g., `data/tasks.ttl`).

### 3.3. Data Handling

-   **File Locking:** To prevent data corruption from concurrent writes, the backend must implement a file locking mechanism when opening a `.ttl` file for appending.
-   **Configuration-driven:** The backend should use `config/domains.yaml` to determine the correct file path for a given entity type.
-   **Pre-write Validation:** Before appending data, the server should validate the generated triples. This can be done by creating a temporary in-memory graph with the new data and running SHACL validation. The data is only appended to the `.ttl` file if validation passes, preventing data corruption and avoiding complex rollback logic.

## 4. Implementation Plan

1.  **Backend Setup:**
    -   Choose a lightweight Python web framework (e.g., Flask).
    -   Create a new `web/server.py` to house the API endpoint.
    -   Implement the `POST /api/add` endpoint.
    -   Implement logic for URI generation, RDF serialization, and file appending with locking.

2.  **Frontend Development:**
    -   Modify `web/index.html` to include an "Add New" button and a modal container for the forms.
    -   Create the HTML and JavaScript for the "Add Task" form as a first example.
    -   Write the JavaScript to handle form submission, send the data to the API, and process the response (e.g., show a success message or clear the form).

3.  **Integration and Configuration:**
    -   Update `util/start_web_interface.sh` to run the new Python server instead of a simple `http.server`.
    -   Ensure the server has access to the data and config directories.
    -   Populate dropdowns (like the projects list) by making a `GET` request to the SPARQL endpoint.

4.  **Expansion:**
    -   After the "Add Task" functionality is working, create forms for other entities like `schema:CreativeWork` (Note) and `schema:BookmarkAction` (Bookmark).

## 5. Security Considerations

-   **Input Sanitization:** All user-provided data must be rigorously sanitized before being written to files to prevent Cross-Site Scripting (XSS) or other injection attacks.
-   **Authentication (Future Scope):** Initially, the server will run locally and be trusted. For a publicly hosted version, this endpoint would need to be protected by an authentication and authorization layer.
-   **Error Handling:** The API should handle errors gracefully and provide meaningful feedback to the user without exposing sensitive system information.
