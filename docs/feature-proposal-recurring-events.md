# Feature Proposal: Recurring Events and Tasks

**Author:** Jules
**Status:** Proposed
**Date:** 2025-09-02

## 1. Summary

This proposal outlines a system for managing recurring events and tasks within the PIM knowledge base. By incorporating the widely-used iCalendar Recurrence Rule standard (RRULE, RFC 5545), we can model repeating items like "weekly team meeting" or "daily workout" in a standard, interoperable way.

## 2. Motivation

Many personal and professional activities are not one-off events but recur on a regular basis. The current data model can only represent single instances of events and tasks. This has several limitations:

-   **Manual Duplication:** To schedule a weekly meeting, a user would have to manually create 52 separate events for the year.
-   **Difficult to Update:** Changing the time or description of a recurring event requires finding and updating all instances.
-   **Lack of Clarity:** It's impossible to query the system for the "rule" of a recurring event (e.g., "show me all my weekly tasks").
-   **Poor Interoperability:** Exported data lacks the recurrence information that calendar applications like Google Calendar or Apple Calendar rely on.

Adding support for recurrence rules will make the PIM system much more powerful for time management.

## 3. Proposed Solution

The core of the solution is to extend the data model to include the `RRULE` property from the iCalendar vocabulary. We will adopt the `ical` namespace, which is already in use, and add the `rrule` property.

### 3.1. Data Model Extension

We will use the `ical:rrule` property to store the recurrence rule as a string, following the RFC 5545 standard.

**Namespace Declaration (already in `base.ttl`):**
```turtle
@prefix ical: <http://www.w3.org/2002/12/cal/ical#> .
```

**Property Usage:**
The `ical:rrule` property will be attached to an `ical:Vevent` or a `pim:Task` (or `schema:Action`). The value is a string containing the rule.

**Example: A Weekly Recurring Event**
This event starts on September 15, 2025, and repeats every Monday at 10:30 AM until December 31, 2025.

```turtle
@prefix :      <https://ben.example/pim/> .
@prefix ical:  <http://www.w3.org/2002/12/cal/ical#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

:event-weekly-standup
  a ical:Vevent ;
  dcterms:title "Weekly Team Standup" ;
  ical:dtstart "2025-09-15T10:30:00Z"^^xsd:dateTime ;
  ical:duration "PT30M"^^xsd:duration ;
  ical:location "Virtual" ;
  ical:rrule "FREQ=WEEKLY;BYDAY=MO;UNTIL=20251231T235959Z" .
```

**Example: A Daily Recurring Task**
This task to "clear inbox" should appear every day.

```turtle
@prefix :      <https://ben.example/pim/> .
@prefix pim:   <https://ben.example/ns/pim#> .
@prefix ical:  <http://www.w3.org/2002/12/cal/ical#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .

:task-daily-inbox-review
  a pim:Task ;
  dcterms:title "Review and clear inbox" ;
  pim:status "todo" ;
  pim:priority 3 ;
  ical:dtstart "2025-09-03T09:00:00Z"^^xsd:dateTime ;
  ical:rrule "FREQ=DAILY" .
```

### 3.2. Querying and Application Logic

Handling recurring events requires application-level logic to "expand" the rule into a series of occurrences within a given time frame.

-   **SPARQL Queries:** Pure SPARQL cannot interpret `RRULE` strings. Instead, the application logic (in Python or JavaScript) will first query for all events and tasks. It will then iterate through the results, and for any item with an `ical:rrule`, it will use a library (like Python's `dateutil.rrule`) to generate the instances that fall within the desired window (e.g., "this week" or "this month").

-   **Web Interface:**
    -   The **Dashboard** would need to be updated to use this expansion logic to show upcoming recurring events and tasks.
    -   The proposed **Calendar View** would be the primary beneficiary. It would fetch all events and use the expansion logic to plot them on the calendar grid.

-   **ICS Export (`ics_bridge.py`):**
    -   The `ics_bridge.py` script will be updated to check for the `ical:rrule` property on an event.
    -   If present, the property will be passed directly into the generated `.ics` file, allowing calendar clients to handle the recurrence natively.

## 4. Implementation Plan

1.  **Library Evaluation:**
    -   Research and select a robust library for parsing and expanding `RRULE`s in Python (for the backend and query script) and JavaScript (for the web frontend).
    -   Python: `python-dateutil` is a strong candidate.
    -   JavaScript: `rrule.js` is a popular choice.

2.  **Update Data and Documentation:**
    -   Update `docs/` and `README.md` to document the use of `ical:rrule` for recurring items.
    -   Add examples of recurring events and tasks to the `examples/` directory.

3.  **Update `ics_bridge.py`:**
    -   Modify the script to read the `ical:rrule` triple from the RDF graph.
    -   Add the `RRULE:` property to the generated iCalendar event object.

4.  **Update Web Interface Logic:**
    -   Integrate an `RRULE` parsing library into the frontend JavaScript.
    -   Modify the data-fetching logic in `dashboard.js` (and the future `calendar.js`) to:
        1.  Fetch all events/tasks via SPARQL.
        2.  Identify items with an `ical:rrule`.
        3.  Generate future occurrences for a given date range (e.g., the next 30 days).
        4.  Merge the generated occurrences with the single-instance items before displaying them.

5.  **Update `run_query.py` (Optional):**
    -   Consider adding a flag to `util/run_query.py`, e.g., `--expand-recurring`, which would perform the `RRULE` expansion in Python and return a list of all occurrences within a specified timeframe. This would provide a powerful command-line tool for viewing upcoming events.

## 5. Benefits

-   **Efficiency:** Define a recurring event once, not dozens of times.
-   **Interoperability:** Greatly improves the utility of ICS exports.
-   **Clarity:** The data model accurately reflects the user's intent.
-   **Power:** Enables new kinds of views and queries, such as "show me my weekly commitments."
