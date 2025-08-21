#!/bin/bash
# Start script for PIM RDF Web Interface
#
# This script helps start both the Fuseki server and web interface.
# For production use, replace the mock server with real Fuseki.

echo "PIM RDF Web Interface Starter"
echo "============================="

# Check if we're using mock data or real Fuseki
if [ "$1" = "--mock" ]; then
    echo "Starting with mock SPARQL server..."
    echo ""
    echo "Starting mock SPARQL server on port 3030..."
    cd web
    python3 mock_server.py &
    MOCK_PID=$!
    
    echo "Starting web server on port 8080..."
    python3 -m http.server 8080 &
    WEB_PID=$!
    
    echo ""
    echo "Servers started!"
    echo "- Web interface: http://localhost:8080"
    echo "- Mock SPARQL endpoint: http://localhost:3030/pim/query"
    echo ""
    echo "Press Ctrl+C to stop both servers..."
    
    # Wait for interrupt and clean up
    trap "echo 'Stopping servers...'; kill $MOCK_PID $WEB_PID 2>/dev/null; exit" INT
    wait
else
    echo "For real use, you need to:"
    echo "1. Start Fuseki with your RDF data:"
    echo "   fuseki-server --config=config-pim.ttl"
    echo ""
    echo "2. In another terminal, start the web interface:"
    echo "   cd web && python3 -m http.server 8080"
    echo ""
    echo "3. Open http://localhost:8080 in your browser"
    echo ""
    echo "For testing with mock data, run:"
    echo "   $0 --mock"
fi