#!/usr/bin/env python3
"""
Mock SPARQL server for testing the PIM RDF web interface.
This simulates Fuseki responses for development/testing purposes.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse

class MockSPARQLHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/pim/query':
            content_length = int(self.headers['Content-Length'])
            query = self.rfile.read(content_length).decode('utf-8')
            
            # Send CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/sparql-results+json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept')
            self.end_headers()
            
            # Mock response based on query content
            mock_response = self.generate_mock_response(query)
            self.wfile.write(json.dumps(mock_response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept')
        self.end_headers()
    
    def generate_mock_response(self, query):
        """Generate mock SPARQL JSON results based on query type"""
        
        if 'Task' in query:
            return {
                "results": {
                    "bindings": [
                        {
                            "uri": {"type": "uri", "value": "https://ben.example/pim/task/001"},
                            "title": {"type": "literal", "value": "Finish RDF PIM design"},
                            "status": {"type": "literal", "value": "todo"},
                            "priority": {"type": "literal", "value": "2"},
                            "assignedTo": {"type": "uri", "value": "https://ben.example/pim/Ben"},
                            "tags": {"type": "literal", "value": "https://ben.example/pim/tag/knowledge"}
                        },
                        {
                            "uri": {"type": "uri", "value": "https://ben.example/pim/task/002"},
                            "title": {"type": "literal", "value": "Create web interface"},
                            "status": {"type": "literal", "value": "doing"},
                            "priority": {"type": "literal", "value": "1"},
                            "assignedTo": {"type": "uri", "value": "https://ben.example/pim/Ben"}
                        }
                    ]
                }
            }
        
        elif 'Note' in query:
            return {
                "results": {
                    "bindings": [
                        {
                            "uri": {"type": "uri", "value": "https://ben.example/pim/note/001"},
                            "title": {"type": "literal", "value": "First RDF note"},
                            "description": {"type": "literal", "value": "This is a test note in the RDF knowledge base."},
                            "creator": {"type": "uri", "value": "https://ben.example/pim/Ben"},
                            "tags": {"type": "literal", "value": "https://ben.example/pim/tag/knowledge"}
                        }
                    ]
                }
            }
        
        elif 'Person' in query:
            return {
                "results": {
                    "bindings": [
                        {
                            "uri": {"type": "uri", "value": "https://ben.example/pim/Ben"},
                            "label": {"type": "literal", "value": "Ben Mordue"},
                            "email": {"type": "literal", "value": "ben@example.com"}
                        }
                    ]
                }
            }
        
        elif 'Project' in query:
            return {
                "results": {
                    "bindings": [
                        {
                            "uri": {"type": "uri", "value": "https://ben.example/pim/project/pim-system"},
                            "title": {"type": "literal", "value": "PIM RDF System"},
                            "description": {"type": "literal", "value": "Personal information management using RDF"}
                        }
                    ]
                }
            }
        
        # Default empty response
        return {
            "results": {
                "bindings": []
            }
        }

if __name__ == '__main__':
    server = HTTPServer(('localhost', 3030), MockSPARQLHandler)
    print("Mock SPARQL server running on http://localhost:3030")
    print("SPARQL endpoint: http://localhost:3030/pim/query")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down mock server...")
        server.server_close()