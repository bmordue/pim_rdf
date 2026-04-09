#!/usr/bin/env python3
"""
Export script for PIM RDF knowledge base.
Generates static HTML and JSON-LD snapshots from RDF/SPARQL data.
"""

import argparse
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, DCTERMS

# Define namespaces
PIM = Namespace("https://ben.example/pim/")
PIM_NS = Namespace("https://ben.example/ns/pim#")
SCHEMA = Namespace("https://schema.org/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
PROV = Namespace("http://www.w3.org/ns/prov#")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
ICAL = Namespace("http://www.w3.org/2002/12/cal/ical#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")


class PIMExporter:
    """Exports PIM RDF data to HTML and JSON-LD formats."""
    
    def __init__(self, data_dir="."):
        self.data_dir = Path(data_dir)
        self.graph = Graph()
        self._bind_namespaces()
        
    def _bind_namespaces(self):
        """Bind common namespaces to the graph."""
        self.graph.bind("", PIM)
        self.graph.bind("pim", PIM_NS)
        self.graph.bind("schema", SCHEMA)
        self.graph.bind("foaf", FOAF)
        self.graph.bind("dcterms", DCTERMS)
        self.graph.bind("skos", SKOS)
        self.graph.bind("prov", PROV)
        self.graph.bind("vcard", VCARD)
        self.graph.bind("ical", ICAL)
        self.graph.bind("xsd", XSD)
        
    def load_data(self):
        """Load all TTL files into the graph."""
        ttl_files = [
            "base.ttl",
            "tags.ttl", 
            "notes.ttl",
            "tasks.ttl",
            "projects.ttl",
            "bookmarks.ttl",
            "contacts.ttl",
            "events.ttl"
        ]
        
        for ttl_file in ttl_files:
            file_path = self.data_dir / ttl_file
            if file_path.exists():
                try:
                    self.graph.parse(file_path, format="turtle")
                    print(f"Loaded: {ttl_file}")
                except Exception as e:
                    print(f"Warning: Could not load {ttl_file}: {e}")
            else:
                print(f"Warning: {ttl_file} not found")
                
        # Load shapes if they exist
        shapes_dir = self.data_dir / "shapes"
        if shapes_dir.exists():
            for shape_file in shapes_dir.glob("*.ttl"):
                try:
                    self.graph.parse(shape_file, format="turtle")
                    print(f"Loaded: {shape_file}")
                except Exception as e:
                    print(f"Warning: Could not load {shape_file}: {e}")
                    
        print(f"Total triples loaded: {len(self.graph)}")
        
    def export_json_ld(self, output_file="export.jsonld"):
        """Export the entire knowledge base as JSON-LD."""
        output_path = Path(output_file)
        
        # Create context for more readable JSON-LD
        context = {
            "@base": str(PIM),
            "pim": str(PIM_NS),
            "schema": str(SCHEMA),
            "foaf": str(FOAF),
            "dcterms": str(DCTERMS),
            "skos": str(SKOS),
            "prov": str(PROV),
            "vcard": str(VCARD),
            "ical": str(ICAL),
            "xsd": str(XSD),
            "rdf": str(RDF),
            "rdfs": str(RDFS)
        }
        
        # Serialize to JSON-LD
        jsonld_data = self.graph.serialize(format="json-ld", context=context, indent=2)
        
        # Parse and reformat for better readability
        data = json.loads(jsonld_data)
        
        # Add metadata
        export_metadata = {
            "@context": context,
            "@graph": data if isinstance(data, list) else [data],
            "_export_metadata": {
                "exported_at": datetime.now().isoformat(),
                "total_triples": len(self.graph),
                "exporter": "PIM RDF Export Tool v1.0"
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_metadata, f, indent=2, ensure_ascii=False)
            
        print(f"JSON-LD export saved to: {output_path}")
        return output_path
        
    def _query_tasks(self):
        """Query for tasks data."""
        query = """
        PREFIX pim: <https://ben.example/ns/pim#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX : <https://ben.example/pim/>
        
        SELECT ?task ?title ?status ?priority ?assignedTo ?project ?tag
        WHERE {
            ?task a pim:Task .
            OPTIONAL { ?task dcterms:title ?title }
            OPTIONAL { ?task pim:status ?status }
            OPTIONAL { ?task pim:priority ?priority }
            OPTIONAL { ?task pim:assignedTo ?assignedTo }
            OPTIONAL { ?task pim:project ?project }
            OPTIONAL { ?task :hasTag ?tag }
        }
        ORDER BY ?priority ?title
        """
        return list(self.graph.query(query))
        
    def _query_notes(self):
        """Query for notes data.""" 
        query = """
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX schema: <https://schema.org/>
        PREFIX : <https://ben.example/pim/>
        
        SELECT ?note ?title ?description ?creator ?created ?tag
        WHERE {
            ?note a :Note .
            OPTIONAL { ?note dcterms:title ?title }
            OPTIONAL { ?note dcterms:description ?description }
            OPTIONAL { ?note dcterms:creator ?creator }
            OPTIONAL { ?note dcterms:created ?created }
            OPTIONAL { ?note :hasTag ?tag }
        }
        ORDER BY DESC(?created) ?title
        """
        return list(self.graph.query(query))
        
    def _query_projects(self):
        """Query for projects data."""
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX : <https://ben.example/pim/>
        
        SELECT ?project ?label ?task
        WHERE {
            ?project a :Project .
            OPTIONAL { ?project rdfs:label ?label }
            OPTIONAL { ?project :hasTask ?task }
        }
        ORDER BY ?label
        """
        return list(self.graph.query(query))
        
    def _query_dashboard(self):
        """Query dashboard data - open tasks by priority."""
        query = """
        PREFIX pim: <https://ben.example/ns/pim#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        
        SELECT ?task ?title ?priority ?status
        WHERE {
            ?task a pim:Task ;
                  dcterms:title ?title ;
                  pim:priority ?priority .
            OPTIONAL { ?task pim:status ?status }
            FILTER(!BOUND(?status) || ?status != "done")
        }
        ORDER BY ASC(?priority) ?title
        """
        return list(self.graph.query(query))
        
    def export_html(self, output_dir="html_export"):
        """Export knowledge base as static HTML."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate index page
        self._generate_index_html(output_path)
        
        # Generate individual pages
        self._generate_tasks_html(output_path)
        self._generate_notes_html(output_path)
        self._generate_projects_html(output_path)
        
        # Copy basic CSS
        self._generate_css(output_path)
        
        print(f"HTML export saved to: {output_path}")
        return output_path
        
    def _generate_css(self, output_path):
        """Generate basic CSS for the HTML export."""
        css_content = """
body {
    font-family: system-ui, -apple-system, sans-serif;
    line-height: 1.6;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f9f9f9;
}

header {
    background: #2c3e50;
    color: white;
    padding: 20px;
    margin: -20px -20px 30px -20px;
    border-radius: 0 0 8px 8px;
}

h1, h2, h3 {
    color: #2c3e50;
}

nav {
    background: white;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 30px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

nav a {
    color: #3498db;
    text-decoration: none;
    margin-right: 20px;
    font-weight: 500;
}

nav a:hover {
    text-decoration: underline;
}

.content {
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

th {
    background-color: #f8f9fa;
    font-weight: 600;
}

tr:hover {
    background-color: #f8f9fa;
}

.priority-high { color: #e74c3c; font-weight: bold; }
.priority-medium { color: #f39c12; }
.priority-low { color: #27ae60; }

.status-done { text-decoration: line-through; opacity: 0.6; }

.uri { 
    font-family: monospace; 
    font-size: 0.9em; 
    color: #666; 
    word-break: break-all;
}

.metadata {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #eee;
    font-size: 0.9em;
    color: #666;
}

.card {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.tag {
    background: #3498db;
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    margin-right: 5px;
}
"""
        
        with open(output_path / "style.css", 'w') as f:
            f.write(css_content)
    
    def _html_template(self, title, content, current_page=""):
        """Generate HTML template with navigation."""
        nav_items = [
            ("index.html", "Dashboard", "dashboard"),
            ("tasks.html", "Tasks", "tasks"),
            ("notes.html", "Notes", "notes"), 
            ("projects.html", "Projects", "projects")
        ]
        
        nav_html = ""
        for href, label, page_id in nav_items:
            active = ' style="text-decoration: underline; font-weight: bold;"' if page_id == current_page else ''
            nav_html += f'<a href="{href}"{active}>{label}</a>'
            
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - PIM RDF Knowledge Base</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1>PIM RDF Knowledge Base</h1>
        <p>Personal knowledge base powered by RDF/Turtle</p>
    </header>
    
    <nav>
        {nav_html}
    </nav>
    
    <div class="content">
        {content}
    </div>
    
    <div class="metadata">
        <p>Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total triples: {len(self.graph)}</p>
    </div>
</body>
</html>"""

    def _format_uri(self, uri):
        """Format URI for display, preferring local names."""
        if uri:
            uri_str = str(uri)
            if uri_str.startswith(str(PIM)):
                return uri_str.replace(str(PIM), ":")
            elif uri_str.startswith(str(PIM_NS)):
                return uri_str.replace(str(PIM_NS), "pim:")
            return uri_str
        return ""
        
    def _generate_index_html(self, output_path):
        """Generate dashboard/index HTML page."""
        dashboard_results = self._query_dashboard()
        
        content = f"""
        <h2>Dashboard</h2>
        <p>Welcome to your personal knowledge base. Here's an overview of your open tasks.</p>
        
        <h3>Open Tasks by Priority</h3>
        <table>
            <thead>
                <tr>
                    <th>Task</th>
                    <th>Title</th>
                    <th>Priority</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for row in dashboard_results:
            task_uri = self._format_uri(row.task)
            title = str(row.title) if row.title else "Untitled"
            priority = str(row.priority) if row.priority else "N/A"
            status = str(row.status) if row.status else "open"
            
            priority_class = ""
            if priority.isdigit():
                p = int(priority)
                if p <= 1:
                    priority_class = "priority-high"
                elif p <= 3:
                    priority_class = "priority-medium"
                else:
                    priority_class = "priority-low"
                    
            status_class = "status-done" if status == "done" else ""
            
            content += f"""
                <tr class="{status_class}">
                    <td class="uri">{task_uri}</td>
                    <td>{title}</td>
                    <td class="{priority_class}">{priority}</td>
                    <td>{status}</td>
                </tr>
            """
            
        content += """
            </tbody>
        </table>
        """
        
        html = self._html_template("Dashboard", content, "dashboard")
        
        with open(output_path / "index.html", 'w', encoding='utf-8') as f:
            f.write(html)
            
    def _generate_tasks_html(self, output_path):
        """Generate tasks HTML page."""
        tasks_results = self._query_tasks()
        
        content = f"""
        <h2>Tasks</h2>
        <p>All tasks in the knowledge base.</p>
        
        <table>
            <thead>
                <tr>
                    <th>Task</th>
                    <th>Title</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Assigned To</th>
                    <th>Project</th>
                    <th>Tags</th>
                </tr>
            </thead>
            <tbody>
        """
        
        # Group results by task
        task_data = {}
        for row in tasks_results:
            task_uri = str(row.task)
            if task_uri not in task_data:
                task_data[task_uri] = {
                    'uri': self._format_uri(row.task),
                    'title': str(row.title) if row.title else "Untitled",
                    'status': str(row.status) if row.status else "open",
                    'priority': str(row.priority) if row.priority else "N/A",
                    'assignedTo': self._format_uri(row.assignedTo) if row.assignedTo else "",
                    'project': self._format_uri(row.project) if row.project else "",
                    'tags': set()
                }
            if row.tag:
                task_data[task_uri]['tags'].add(self._format_uri(row.tag))
        
        for task_uri, data in task_data.items():
            priority_class = ""
            if data['priority'].isdigit():
                p = int(data['priority'])
                if p <= 1:
                    priority_class = "priority-high"
                elif p <= 3:
                    priority_class = "priority-medium"
                else:
                    priority_class = "priority-low"
                    
            status_class = "status-done" if data['status'] == "done" else ""
            
            tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in data['tags']])
            
            content += f"""
                <tr class="{status_class}">
                    <td class="uri">{data['uri']}</td>
                    <td>{data['title']}</td>
                    <td>{data['status']}</td>
                    <td class="{priority_class}">{data['priority']}</td>
                    <td class="uri">{data['assignedTo']}</td>
                    <td class="uri">{data['project']}</td>
                    <td>{tags_html}</td>
                </tr>
            """
            
        content += """
            </tbody>
        </table>
        """
        
        html = self._html_template("Tasks", content, "tasks")
        
        with open(output_path / "tasks.html", 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_notes_html(self, output_path):
        """Generate notes HTML page."""
        notes_results = self._query_notes()
        
        content = f"""
        <h2>Notes</h2>
        <p>All notes in the knowledge base.</p>
        """
        
        # Group results by note
        note_data = {}
        for row in notes_results:
            note_uri = str(row.note)
            if note_uri not in note_data:
                note_data[note_uri] = {
                    'uri': self._format_uri(row.note),
                    'title': str(row.title) if row.title else "Untitled",
                    'description': str(row.description) if row.description else "",
                    'creator': self._format_uri(row.creator) if row.creator else "",
                    'created': str(row.created) if row.created else "",
                    'tags': set()
                }
            if row.tag:
                note_data[note_uri]['tags'].add(self._format_uri(row.tag))
        
        for note_uri, data in note_data.items():
            tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in data['tags']])
            
            content += f"""
            <div class="card">
                <h3>{data['title']}</h3>
                <p class="uri">URI: {data['uri']}</p>
                {f'<p><strong>Description:</strong> {data["description"]}</p>' if data['description'] else ''}
                {f'<p><strong>Creator:</strong> <span class="uri">{data["creator"]}</span></p>' if data['creator'] else ''}
                {f'<p><strong>Created:</strong> {data["created"]}</p>' if data['created'] else ''}
                {f'<p><strong>Tags:</strong> {tags_html}</p>' if data['tags'] else ''}
            </div>
            """
            
        html = self._html_template("Notes", content, "notes")
        
        with open(output_path / "notes.html", 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_projects_html(self, output_path):
        """Generate projects HTML page."""
        projects_results = self._query_projects()
        
        content = f"""
        <h2>Projects</h2>
        <p>All projects in the knowledge base.</p>
        """
        
        # Group results by project
        project_data = {}
        for row in projects_results:
            project_uri = str(row.project)
            if project_uri not in project_data:
                project_data[project_uri] = {
                    'uri': self._format_uri(row.project),
                    'label': str(row.label) if row.label else "Unnamed Project",
                    'tasks': set()
                }
            if row.task:
                project_data[project_uri]['tasks'].add(self._format_uri(row.task))
        
        for project_uri, data in project_data.items():
            tasks_html = ""
            if data['tasks']:
                tasks_html = "<ul>"
                for task in data['tasks']:
                    tasks_html += f'<li class="uri">{task}</li>'
                tasks_html += "</ul>"
            
            content += f"""
            <div class="card">
                <h3>{data['label']}</h3>
                <p class="uri">URI: {data['uri']}</p>
                {f'<p><strong>Tasks:</strong></p>{tasks_html}' if data['tasks'] else '<p>No tasks assigned</p>'}
            </div>
            """
            
        html = self._html_template("Projects", content, "projects")
        
        with open(output_path / "projects.html", 'w', encoding='utf-8') as f:
            f.write(html)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Export PIM RDF knowledge base to HTML and JSON-LD")
    parser.add_argument("--data-dir", default=".", help="Directory containing TTL files (default: current directory)")
    parser.add_argument("--html", action="store_true", help="Export to HTML")
    parser.add_argument("--json-ld", action="store_true", help="Export to JSON-LD")
    parser.add_argument("--html-dir", default="html_export", help="Output directory for HTML export")
    parser.add_argument("--json-file", default="export.jsonld", help="Output file for JSON-LD export")
    parser.add_argument("--all", action="store_true", help="Export both HTML and JSON-LD")
    
    args = parser.parse_args()
    
    if not (args.html or args.json_ld or args.all):
        parser.error("Must specify at least one export format: --html, --json-ld, or --all")
    
    exporter = PIMExporter(args.data_dir)
    
    print("Loading RDF data...")
    exporter.load_data()
    
    if args.all or args.html:
        print("\nExporting to HTML...")
        exporter.export_html(args.html_dir)
        
    if args.all or args.json_ld:
        print("\nExporting to JSON-LD...")
        exporter.export_json_ld(args.json_file)
        
    print("\nExport complete!")


if __name__ == "__main__":
    main()