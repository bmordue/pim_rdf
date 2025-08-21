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