# Enhanced Google Takeout Location Data Ingestion

The `util/ingest_takeout.py` script has been significantly enhanced to extract detailed location information from Google Takeout archives. This document describes the comprehensive data fields now supported.

## Enhanced Data Extraction

### Classic Location History Format
For the traditional Location History JSON format (`locations` array), the following fields are now extracted:

#### Geographic Data
- **Coordinates**: `latitudeE7` / `longitudeE7` → `geo:lat`, `geo:long`, `schema:latitude`, `schema:longitude`
- **Altitude**: `altitude` → `schema:elevation` (integer)
- **Accuracy**: `accuracy` → `pim:accuracy` (meters, integer)

#### Movement Data  
- **Velocity**: `velocity` → `pim:velocity` (integer)
- **Heading**: `heading` → `pim:heading` (degrees, integer)

#### Temporal Data
- **Timestamp**: `timestampMs` → `pim:visitedOn`, `schema:dateCreated` (ISO datetime)

#### Activity Recognition
- **Activity Types**: `activity[].type` → `pim:activityType` (e.g., "Walking", "In Vehicle")
- **Activity Confidence**: `activity[].confidence` → `pim:activityConfidence` (integer 0-100)

#### Device/Source Information
- **Data Source**: `source` → `pim:dataSource` (e.g., "fused")
- **Device Tag**: `deviceTag` → `pim:deviceTag` (integer identifier)
- **Platform**: `platformType` → `pim:platformType` (e.g., "Android")

### Timeline Objects Format (Semantic Location History)

#### Place Visits (`placeVisit` objects)
Extracted as `schema:Place`, `schema:TouristAttraction`, and `pim:PlaceVisit`:

**Location Details:**
- **Coordinates**: Same as classic format
- **Place ID**: `location.placeId` → `dcterms:identifier`, `pim:googlePlaceId`
- **Name**: `location.name` → `schema:name`, `rdfs:label`
- **Address**: `location.address` / `location.formattedAddress` → `schema:address`
- **Semantic Type**: `location.semanticType` → `pim:semanticType` (e.g., "Type Home", "Type Work")
- **Plus Code**: `location.plusCode` → `pim:plusCode` (Open Location Code)

**Visit Details:**
- **Duration**: `duration.startTimestampMs` / `duration.endTimestampMs` → `schema:startDate`, `schema:endDate`, `schema:duration`
- **Center Point**: `centerLatE7` / `centerLngE7` → `pim:centerLatitude`, `pim:centerLongitude`

**Confidence Scores:**
- **Location Confidence**: `location.locationConfidence` → `pim:locationConfidence` (float 0.0-1.0)
- **Visit Confidence**: `visitConfidence` → `pim:visitConfidence` (float 0.0-1.0) 
- **Place Confidence**: `placeConfidence` → `pim:placeConfidence` (mapped from string to float)

**Nested Data:**
- **Child Visits**: `childVisits[]` → creates linked `pim:PlaceVisit` entities with `pim:hasChildVisit`
- **Alternative Places**: `otherCandidateLocations[]` → creates `pim:hasAlternativePlace` links

#### Activity Segments (`activitySegment` objects)
Extracted as `schema:TravelAction`, specific action types, and `pim:ActivitySegment`:

**Journey Details:**
- **Duration**: Same pattern as place visits → `schema:startTime`, `schema:endTime`
- **Distance**: `distance` → `schema:distance` (with units), `pim:distanceMeters` (float)
- **Activity Type**: `activityType` → `pim:activityType` + specific schema types
  - `IN_VEHICLE` → `schema:DriveAction`
  - `WALKING` → `schema:WalkAction`  
  - `ON_BICYCLE` → `schema:BicycleTrip`

**Route Information:**
- **Start Location**: `startLocation` → `schema:fromLocation` (linked `schema:GeoCoordinates`)
- **End Location**: `endLocation` → `schema:toLocation` (linked `schema:GeoCoordinates`)
- **Waypoint Path**: `waypointPath` → `pim:waypointCount`, `pim:pathDistanceMeters`

**Confidence Data:**
- **Overall Confidence**: `confidence` → `pim:confidence` (mapped from string)
- **Activity Possibilities**: `activities[].activityType` → `pim:possibleActivityType`

## RDF Schema Mapping

### Primary Vocabularies Used

1. **schema.org**: Primary vocabulary for places, actions, and geographic data
   - `schema:Place`, `schema:TouristAttraction`, `schema:Residence`
   - `schema:TravelAction`, `schema:DriveAction`, `schema:WalkAction`
   - `schema:GeoCoordinates` for precise location points
   - Standard properties: `name`, `address`, `latitude`, `longitude`, `startTime`, `endTime`, etc.

2. **WGS84 Geo**: Geographic coordinates
   - `geo:lat`, `geo:long` for primary coordinate representation

3. **Dublin Core Terms**: Metadata
   - `dcterms:created`, `dcterms:source`, `dcterms:identifier`

4. **Custom PIM Namespace**: Google-specific and detailed metadata
   - Confidence scores, device information, activity details
   - Google Place IDs, Plus Codes, semantic types
   - Technical accuracy and movement data

### Entity Types Generated

1. **Places** (`schema:Place` + `pim:Place`):
   - Basic location points with coordinates and metadata
   - Enhanced with accuracy, device info, activity context

2. **Place Visits** (`schema:Place` + `schema:TouristAttraction` + `pim:PlaceVisit`):
   - Named locations with visit duration and confidence
   - Rich metadata including addresses, Place IDs, semantic types
   - Support for nested child visits and alternative locations

3. **Travel Activities** (`schema:TravelAction` + specific types + `pim:ActivitySegment`):
   - Movement between locations with duration and distance
   - Activity type classification (driving, walking, cycling)
   - Route information with start/end coordinates

4. **Geographic Coordinates** (`schema:GeoCoordinates`):
   - Precise lat/lng points for activity start/end locations
   - Separate entities to allow reuse and detailed geographic modeling

## Usage Examples

### Processing Enhanced Data
```bash
# Run enhanced ingestion on a takeout archive
python3 util/ingest_takeout.py /path/to/takeout.zip

# The script now extracts significantly more detail:
# - 43 different RDF predicates (vs ~6 previously)
# - Place names, addresses, confidence scores
# - Visit durations, activity classifications  
# - Route information and waypoints
# - Device and source metadata
```

### Querying Enhanced Data
```sparql
# Find all place visits with names and durations
SELECT ?place ?name ?start ?end ?duration WHERE {
  ?place a pim:PlaceVisit ;
         schema:name ?name ;
         schema:startDate ?start ;
         schema:endDate ?end ;
         schema:duration ?duration .
}

# Find travel activities with distances over 1km
SELECT ?activity ?type ?distance ?start ?end WHERE {
  ?activity a schema:TravelAction ;
            pim:activityType ?type ;
            pim:distanceMeters ?distanceM ;
            schema:fromLocation ?start ;
            schema:toLocation ?end .
  FILTER(?distanceM > 1000)
}

# Get high-confidence places with addresses
SELECT ?place ?name ?address ?confidence WHERE {
  ?place a pim:PlaceVisit ;
         schema:name ?name ;
         schema:address ?address ;
         pim:placeConfidence ?confidence .
  FILTER(?confidence > 0.8)
}
```

## Data Volume and Processing

The enhanced ingestion now processes:
- **20 location records** from classic format (vs 10 previously)  
- **20 timeline objects** from semantic format (new)
- **Significantly more triples per entity**: ~21 triples for classic locations, ~24 for place visits, ~23 for activities

This provides much richer context for personal knowledge management while maintaining reasonable processing volumes for demonstration purposes.
