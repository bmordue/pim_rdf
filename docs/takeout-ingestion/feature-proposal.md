# Feature Proposal: Google Takeout Ingestion

## Executive Summary

This document proposes a new feature to enable the ingestion of a Google Takeout archive into the PIM RDF store. This would allow users to import a wide range of personal data from their Google account, significantly enriching their personal knowledge base. The initial implementation will focus on ingesting contacts, calendar events, and location history, with a clear path for expanding to other data types in the future.

## Problem Statement

The PIM RDF store is a powerful tool for managing personal information, but its utility is currently limited by the manual effort required to populate it with data. Users must manually create or convert their data into the required RDF format. This is a time-consuming and error-prone process, which limits the adoption and usefulness of the system.

Google Takeout provides a convenient way for users to download their data from various Google services. By providing a mechanism to ingest this data directly, we can automate the process of populating the PIM RDF store, making it much more valuable to users.

## Proposed Solution

We propose to develop a new ingestion script that can parse a Google Takeout archive and convert the data into RDF, suitable for inclusion in the PIM RDF store. The script will be designed to be extensible, allowing for the addition of new data types over time.

### Phase 1: Core Data Types

The initial implementation will focus on the following data types, which were specifically mentioned by the user or are core to a PIM system:

*   **Contacts:** Google Contacts data (in vCard format) will be converted to `foaf:Person` entities, consistent with the existing `contacts.ttl` schema.
*   **Calendar Events:** Google Calendar data (in iCalendar format) will be converted to `ical:Vevent` entities, consistent with the existing `events.ttl` schema.
*   **Location History:** Google Maps location history (as Semantic JSON) will be converted into a new `pim:Place` entity, with properties for location, date, and time.

### Additional Data Types for Future Consideration

Beyond the initial implementation, the ingestion script could be extended to handle a wide variety of other data types available in Google Takeout, including:

*   **Gmail:** Emails could be stored as `pim:Communication` entities.
*   **Google Drive:** Document metadata could be indexed as `pim:Document` entities.
*   **Google Photos:** Photo metadata could be ingested as `pim:Image` entities, with links to the photos themselves.
*   **Google Keep:** Notes and lists could be converted to `pim:Note` entities, similar to the existing `notes.ttl` schema.
*   **YouTube:** Watch history and playlists could be ingested to analyze media consumption habits.
*   **Google Chrome:** Bookmarks and browsing history could be imported into the existing `bookmarks.ttl` structure.
*   **Google Tasks:** Tasks could be imported into the existing `tasks.ttl` structure.

### RDF Schema Proposal

We will use existing standard vocabularies (like FOAF, iCal) where possible. For data types that don't have a clear standard, we will extend the existing `pim:` namespace.

Here's a sample of the proposed RDF for a new `pim:Place` entity:

```turtle
@prefix pim: <https://ben.example/pim/> .
@prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

:place-001 a pim:Place ;
    pim:locationName "Eiffel Tower" ;
    geo:lat "48.8584"^^xsd:float ;
    geo:long "2.2945"^^xsd:float ;
    pim:visitedOn "2023-04-01T14:00:00Z"^^xsd:dateTime .
```

## Implementation Plan

### Phase 1: Core Implementation (2-3 weeks)

1.  **Develop a parsing library for Google Takeout data.** This library will handle the unzipping of the archive and parsing the different file formats (vCard, iCalendar, JSON).
2.  **Implement RDF conversion for core data types.** This will involve writing mappers to convert the parsed data into RDF triples using the `rdflib` library.
3.  **Create a command-line ingestion script.** This script will take the path to a Google Takeout archive as input and generate the corresponding `.ttl` files.
4.  **Write unit tests for the parsing and conversion logic.**

### Phase 2: Integration and Documentation (1 week)

1.  **Integrate the ingestion script with the existing `validate_pim.sh` script.** This will allow users to easily ingest data as part of their regular workflow.
2.  **Update the `config/domains.yaml` to include the new data types.**
3.  **Write documentation for the new ingestion feature.** This will include instructions on how to use the script and how to extend it with new data types.

### Phase 3: Expansion to Additional Data Types (Ongoing)

After the initial implementation is complete, we can begin to add support for additional data types based on user feedback and priorities.

## Benefits

*   **Increased Utility:** The PIM RDF store will become much more useful as it can be easily populated with a rich set of personal data.
*   **Automation:** The ingestion script will automate a previously manual and error-prone process.
*   **Extensibility:** The modular design of the ingestion script will make it easy to add support for new data types in the future.

## Risks

*   **Google Takeout Format Changes:** The format of the Google Takeout archive may change over time, which could break the ingestion script. We will need to monitor for changes and update the script accordingly.
*   **Data Privacy:** The ingestion script will be handling sensitive personal data. We must ensure that the script is secure and that the user's data is handled responsibly. We will not be uploading any data to any servers. The script will run locally on the user's machine.
