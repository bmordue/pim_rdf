# Feature Proposal: Interactive Web Dashboard

## 1. Summary

This proposal outlines the development of a dynamic, interactive web dashboard to serve as the primary user interface for the PIM RDF project. The current system relies on static generation from SPARQL queries, which limits user interaction. An interactive dashboard would provide a richer, more responsive experience for viewing, filtering, and navigating personal data.

## 2. Problem

The current web interface (implied by the `dashboard.sparql` query and static generation roadmap item) is likely a static, read-only view of the data. Users cannot easily:
- Filter tasks by status, priority, or project.
- Sort notes by creation date or title.
- Quickly switch between different data views (e.g., tasks, notes, projects) without reloading the page.
- See real-time updates as they modify the underlying `.ttl` files.

This makes the interface less efficient and user-friendly than it could be.

## 3. Proposed Solution

Develop a single-page application (SPA) dashboard using a modern JavaScript framework (e.g., React, Vue, or Svelte) that interacts with a backend SPARQL endpoint. This would replace the static site generation process with a live, client-side UI.

### Key Features

- **Unified Dashboard View:** Display a summary of key information on a single screen:
  - Open tasks by priority.
  - Recently created notes.
  - Upcoming events.
  - Active projects.
- **Dynamic Filtering and Sorting:** Allow users to filter and sort data tables in real-time. For example:
  - Filter tasks by `status` ("todo", "doing", "done") or `priority`.
  - Sort notes by `dcterms:created` date.
  - Filter items by `tag`.
- **Drill-Down Capability:** Clicking on an item (e.g., a project) would navigate the user to a detailed view of that item, showing all its associated tasks, notes, and metadata.
- **Client-Side Rendering:** The UI will be rendered in the browser, fetching data from the SPARQL endpoint as needed. This will provide a fast and responsive user experience.
- **Responsive Design:** The dashboard will be usable on both desktop and mobile devices.

### Technical Approach

1.  **Backend:** Use the existing Apache Jena Fuseki server (as suggested in `README.md`) to serve the merged `build/merged.ttl` graph over a SPARQL endpoint. This requires no changes to the existing data layer.
2.  **Frontend:**
    -   Build a single-page application using a lightweight framework like Svelte or Vue for its simplicity and performance.
    -   Use a standard JavaScript library (like `sparql.js` or even `fetch`) to execute SPARQL queries against the Fuseki endpoint.
    -   Structure the UI into reusable components (e.g., `TaskList`, `NoteList`, `ProjectView`).
3.  **Queries:** Develop a set of parametric SPARQL queries to fetch the data needed for the dashboard. For example, a query to get tasks could accept parameters for status and project.

## 4. Benefits

- **Improved User Experience:** A dynamic and responsive interface makes managing personal data faster and more intuitive.
- **Deeper Data Exploration:** Users can easily discover connections and insights in their data through filtering and navigation.
- **Foundation for Future Features:** An interactive dashboard provides a solid foundation for adding more advanced features like data editing, real-time collaboration, or data visualization.
- **Alignment with Modern Web Standards:** Moves the project towards a more modern, maintainable, and extensible architecture.

## 5. Next Steps

1.  **Prototype:** Develop a proof-of-concept dashboard with one or two interactive components (e.g., a filterable task list).
2.  **Refine UI/UX:** Gather feedback on the prototype and refine the design.
3.  **Implementation:** Build out the full set of features described above.
4.  **Documentation:** Document the setup and usage of the new interactive dashboard.
