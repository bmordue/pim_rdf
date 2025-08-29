# Feature Proposal: Calendar View for Events

## 1. Summary

This proposal outlines the creation of a calendar view within the web interface to display events from the `events.ttl` file. The PIM uses the iCal vocabulary to model events, but a plain list is not an intuitive way to visualize time-based data. A graphical calendar view would provide a familiar and effective way to manage schedules.

## 2. Problem

Events are currently stored in `data/events.ttl` using standard iCal properties like `ical:dtstart` (start time) and `ical:summary` (title). However, the current interface, being statically generated, likely just lists these events. This makes it difficult to:
- See an overview of a week or month.
- Identify scheduling conflicts or free time.
- Intuitively grasp one's schedule.

The `README.md` mentions an "ICS bridge" to generate `.ics` files, which is useful for exporting to other calendar applications, but doesn't address the need for a native view within the PIM itself.

## 3. Proposed Solution

Integrate a JavaScript calendar library into the interactive web dashboard to render a full-featured calendar view.

### Key Features

- **Monthly, Weekly, and Daily Views:** Allow users to switch between different calendar resolutions.
- **Event Display:** Events from `events.ttl` will be displayed as blocks on the calendar, showing their title and start/end times.
- **Event Details:** Clicking on an event will open a modal or sidebar showing all its details (description, location, status, etc.).
- **Navigation:** Users can easily navigate to the next/previous month or week.
- **Read-Only (Initially):** The initial implementation will focus on displaying events. Creating and editing events directly from the calendar can be a future enhancement.

### Technical Approach

1.  **Frontend (Calendar Library):**
    -   Choose a mature and lightweight JavaScript calendar library. Good options include:
        -   **FullCalendar:** Very powerful and feature-rich, but may be overkill.
        -   **Toast UI Calendar:** Good-looking and has the necessary features.
        -   **V-Calendar / vue-cal:** Good options if Vue.js is chosen for the dashboard.
    -   Create a new "Calendar" page/component within the single-page application.
    -   Initialize the calendar library in this component.
2.  **SPARQL Query:**
    -   Write a SPARQL query to fetch all resources of type `ical:Vevent`.
    -   The query will retrieve essential properties for display: `ical:summary`, `ical:dtstart`, `ical:dtend`, `ical:description`, `ical:location`.
    -   The query will be executed when the calendar view is loaded.
3.  **Data Transformation:**
    -   The frontend will fetch the event data from the SPARQL endpoint.
    -   A simple transformation function will be written in JavaScript to convert the SPARQL JSON results into the event format required by the chosen calendar library.
    -   The transformed data will then be passed to the calendar component for rendering.

## 4. Benefits

- **Intuitive Time Management:** A calendar is the universally understood interface for managing schedules.
- **Enhanced Data Visualization:** Provides a much richer view of event data than a simple list.
- **Centralized View:** Users can see their PIM-managed events directly within the application, without needing to export them to a separate calendar tool.
- **Foundation for Advanced Scheduling:** This feature lays the groundwork for future enhancements like event creation, editing, and integration with tasks.

## 5. Next Steps

1.  **Library Evaluation:** Select and test a suitable JavaScript calendar library.
2.  **Query Development:** Create and test the SPARQL query to fetch event data.
3.  **Prototype:** Build a basic calendar page that fetches and displays events from the sample data.
4.  **Integration:** Add the calendar view to the main dashboard navigation.
5.  **Refinement:** Implement features like the event details modal and view switching (month/week/day).
