<<<<<<< HEAD
# PIM RDF Web Interface

A simple web interface for browsing your RDF personal knowledge base.

## Features

- Browse different types of data: tasks, notes, contacts, projects, bookmarks, events, and tags
- Clean, responsive interface
- Connects to Apache Jena Fuseki SPARQL endpoint
- Shows data properties and relationships
- Direct link to raw SPARQL interface

## Setup

### Quick Start (with mock data)

For testing the interface with sample data:

```bash
cd /path/to/pim_rdf
./start_web_interface.sh --mock
```

This starts both a mock SPARQL server and the web interface.

### Production Setup

1. **Start Fuseki server** with your RDF data:
   ```bash
   cd /path/to/pim_rdf
   
   # Update config-pim.ttl with absolute paths to your .ttl files
   # Then start Fuseki:
   fuseki-server --config=config-pim.ttl
   ```

2. **Serve the web interface**:
   ```bash
   cd web
   python3 -m http.server 8080
   ```

3. **Open in browser**:
   - Web interface: http://localhost:8080
   - Raw SPARQL interface: http://localhost:3030/pim/query

## Notes

- The interface expects Fuseki to be running on `localhost:3030` with dataset name `pim`
- Update the `fusekiEndpoint` in `app.js` if your setup differs
- The interface uses CORS requests to query Fuseki, so both servers need to be running
- Data is queried dynamically when switching between views

## Customization

- Modify SPARQL queries in `app.js` to match your data schema
- Update CSS in `style.css` for different styling
- Add new views by extending the JavaScript and HTML structure
=======
# PIM RDF Interactive Web Dashboard

An interactive web dashboard for viewing and filtering personal information stored in RDF format.

## Features

- **Dashboard View**: Overview of tasks, notes, projects, and events with key statistics
- **Task Management**: Filter tasks by status and priority, sort by different criteria
- **Notes Browser**: Search through notes and sort by creation date or title
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Filtering**: Dynamic filtering and sorting without page reloads

## Setup

### Prerequisites

1. **Python dependencies** (for data validation and merging):
   ```bash
   pip3 install rdflib pyshacl pyyaml
   ```

2. **Apache Jena Fuseki** (for SPARQL endpoint):
   ```bash
   # Using nix-shell (recommended)
   nix-shell
   
   # Or download and install Apache Jena Fuseki manually
   ```

### Running the Dashboard

1. **Start the Fuseki server** with the PIM dataset:
   ```bash
   # From the repository root
   fuseki-server --config=data/config-pim.ttl
   ```
   
   The server will start at http://localhost:3030 with the dataset available at `/pim`.

2. **Open the web dashboard**:
   - Open `web/index.html` in a web browser
   - Or serve it with a simple HTTP server:
     ```bash
     cd web
     python3 -m http.server 8080
     # Open http://localhost:8080
     ```

### Alternative: Standalone Mode

If the Fuseki server is not available, the dashboard will automatically fall back to demo data mode using the sample data from the repository.

## Usage

### Navigation
- **Dashboard**: Overview with key statistics and recent items
- **Tasks**: Full task list with filtering by status, priority, and sorting options
- **Notes**: Notes browser with search functionality and sorting

### Filtering
- **Tasks**: Filter by status (todo/doing/done) and priority levels
- **Notes**: Full-text search across titles and content
- **Sorting**: Multiple sort options for both tasks and notes

### Responsive Design
- Desktop: Full multi-column layout with sidebar navigation
- Tablet: Responsive grid that adapts to screen size
- Mobile: Single-column layout with touch-friendly interface

## Technical Details

### Architecture
- **Frontend**: Vanilla JavaScript with modern ES6+ features
- **Styling**: CSS Grid and Flexbox for responsive layout
- **Data**: SPARQL queries against Apache Jena Fuseki endpoint
- **Fallback**: Demo data when SPARQL endpoint is unavailable

### Files
- `index.html`: Main HTML structure and layout
- `style.css`: Responsive CSS styling with modern design
- `sparql-client.js`: SPARQL client library for data fetching
- `dashboard.js`: Main application logic and UI interactions

### SPARQL Queries
The dashboard uses several SPARQL queries to fetch data:
- Dashboard statistics (counts by type)
- Task filtering and sorting
- Note search and sorting
- Recent items for dashboard overview

### Browser Support
- Modern browsers with ES6+ support
- Chrome, Firefox, Safari, Edge (recent versions)
- Mobile browsers on iOS and Android

## Customization

### Styling
Modify `style.css` to customize the appearance. The design uses CSS custom properties for easy theming.

### Queries
Update `sparql-client.js` to modify the SPARQL queries or add new data fetching methods.

### Layout
Modify `index.html` to change the layout structure or add new views.

## Troubleshooting

### SPARQL Endpoint Issues
- Ensure Fuseki server is running on http://localhost:3030
- Check that the `/pim` dataset is properly configured
- Verify the data files are properly merged in `build/merged.ttl`

### Data Issues
- Run `util/validate_pim.sh` to check data integrity
- Ensure all TTL files have valid syntax
- Check that the required prefixes are defined

### Browser Issues
- Open browser developer tools to check for JavaScript errors
- Verify that the files are being served correctly (no CORS issues)
- Clear browser cache if experiencing issues after updates
>>>>>>> github/main
