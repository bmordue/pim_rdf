/**
 * SPARQL Client for PIM RDF Dashboard
 * Provides utilities for querying the Fuseki SPARQL endpoint
 */

class SPARQLClient {
    constructor(endpoint = 'http://localhost:3030/pim/query') {
        this.endpoint = endpoint;
        this.prefixes = `
PREFIX : <https://ben.example/pim/>
PREFIX pim: <https://ben.example/ns/pim#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX schema: <https://schema.org/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX ical: <http://www.w3.org/2002/12/cal/ical#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        `;
    }

    /**
     * Execute a SPARQL query
     * @param {string} query - The SPARQL query
     * @returns {Promise<Array>} - Query results
     */
    async query(query) {
        const fullQuery = this.prefixes + query;
        
        try {
            const response = await fetch(this.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/sparql-query',
                    'Accept': 'application/sparql-results+json'
                },
                body: fullQuery
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return this.parseResults(data);
        } catch (error) {
            console.error('SPARQL query error:', error);
            throw new Error(`Query failed: ${error.message}`);
        }
    }

    /**
     * Parse SPARQL JSON results into a more convenient format
     * @param {Object} data - SPARQL JSON results
     * @returns {Array} - Parsed results
     */
    parseResults(data) {
        if (!data.results || !data.results.bindings) {
            return [];
        }

        return data.results.bindings.map(binding => {
            const result = {};
            for (const [key, value] of Object.entries(binding)) {
                result[key] = value.value;
            }
            return result;
        });
    }

    /**
     * Get all open tasks ordered by priority
     */
    async getOpenTasks() {
        const query = `
        SELECT ?task ?title ?priority ?status ?created
        WHERE {
            ?task a pim:Task ;
                  dcterms:title ?title ;
                  pim:priority ?priority ;
                  pim:status ?status .
            OPTIONAL { ?task dcterms:created ?created }
            FILTER(?status != "done")
        }
        ORDER BY ASC(?priority)
        `;
        return this.query(query);
    }

    /**
     * Get all tasks with optional filtering
     * @param {Object} filters - Filter options
     */
    async getAllTasks(filters = {}) {
        let whereClause = `
            ?task a pim:Task ;
                  dcterms:title ?title ;
                  pim:priority ?priority ;
                  pim:status ?status .
            OPTIONAL { ?task dcterms:created ?created }
        `;

        const filterConditions = [];
        
        if (filters.status) {
            filterConditions.push(`?status = "${filters.status}"`);
        }
        
        if (filters.priority) {
            filterConditions.push(`?priority = ${filters.priority}`);
        }

        if (filterConditions.length > 0) {
            whereClause += '\nFILTER(' + filterConditions.join(' && ') + ')';
        }

        let orderBy = 'ORDER BY ASC(?priority)';
        if (filters.sort === 'created') {
            orderBy = 'ORDER BY DESC(?created)';
        } else if (filters.sort === 'title') {
            orderBy = 'ORDER BY ?title';
        }

        const query = `
        SELECT ?task ?title ?priority ?status ?created
        WHERE {
            ${whereClause}
        }
        ${orderBy}
        `;

        return this.query(query);
    }

    /**
     * Get all notes with optional filtering
     * @param {Object} filters - Filter options
     */
    async getAllNotes(filters = {}) {
        let whereClause = `
            ?note a schema:CreativeWork ;
                  dcterms:title ?title ;
                  schema:text ?text .
            OPTIONAL { ?note dcterms:created ?created }
            OPTIONAL { ?note dcterms:creator ?creator }
        `;

        if (filters.search) {
            whereClause += `\nFILTER(CONTAINS(LCASE(?title), "${filters.search.toLowerCase()}") || CONTAINS(LCASE(?text), "${filters.search.toLowerCase()}"))`;
        }

        let orderBy = 'ORDER BY DESC(?created)';
        if (filters.sort === 'created-asc') {
            orderBy = 'ORDER BY ASC(?created)';
        } else if (filters.sort === 'title') {
            orderBy = 'ORDER BY ?title';
        }

        const query = `
        SELECT ?note ?title ?text ?created ?creator
        WHERE {
            ${whereClause}
        }
        ${orderBy}
        `;

        return this.query(query);
    }

    /**
     * Get dashboard statistics
     */
    async getDashboardStats() {
        const queries = {
            openTasks: `
                SELECT (COUNT(?task) AS ?count)
                WHERE {
                    ?task a pim:Task ;
                          pim:status ?status .
                    FILTER(?status != "done")
                }
            `,
            totalNotes: `
                SELECT (COUNT(?note) AS ?count)
                WHERE {
                    ?note a schema:CreativeWork .
                }
            `,
            projects: `
                SELECT (COUNT(?project) AS ?count)
                WHERE {
                    ?project a pim:Project .
                }
            `,
            events: `
                SELECT (COUNT(?event) AS ?count)
                WHERE {
                    ?event a ical:Vevent .
                }
            `
        };

        const results = {};
        for (const [key, query] of Object.entries(queries)) {
            try {
                const result = await this.query(query);
                results[key] = result.length > 0 ? parseInt(result[0].count) : 0;
            } catch (error) {
                console.error(`Error getting ${key}:`, error);
                results[key] = 0;
            }
        }

        return results;
    }

    /**
     * Get recent items for dashboard
     * @param {number} limit - Number of items to return
     */
    async getRecentItems(limit = 5) {
        const results = {};

        try {
            // Recent open tasks
            const tasksQuery = `
                SELECT ?task ?title ?priority ?status
                WHERE {
                    ?task a pim:Task ;
                          dcterms:title ?title ;
                          pim:priority ?priority ;
                          pim:status ?status .
                    OPTIONAL { ?task dcterms:created ?created }
                    FILTER(?status != "done")
                }
                ORDER BY ASC(?priority)
                LIMIT ${limit}
            `;
            results.tasks = await this.query(tasksQuery);

            // Recent notes
            const notesQuery = `
                SELECT ?note ?title ?created
                WHERE {
                    ?note a schema:CreativeWork ;
                          dcterms:title ?title .
                    OPTIONAL { ?note dcterms:created ?created }
                }
                ORDER BY DESC(?created)
                LIMIT ${limit}
            `;
            results.notes = await this.query(notesQuery);
        } catch (error) {
            console.error('Error getting recent items:', error);
            results.tasks = [];
            results.notes = [];
        }

        return results;
    }

    /**
     * Test connection to SPARQL endpoint
     */
    async testConnection() {
        try {
            const result = await this.query('SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }');
            return { 
                connected: true, 
                tripleCount: result.length > 0 ? parseInt(result[0].count) : 0 
            };
        } catch (error) {
            return { 
                connected: false, 
                error: error.message 
            };
        }
    }
}