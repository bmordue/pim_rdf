// PIM RDF Browser JavaScript

class RDFBrowser {
    constructor() {
        this.fusekiEndpoint = 'http://localhost:3030/pim/query';
        this.currentView = 'tasks';
        this.initializeUI();
        this.loadInitialData();
    }

    initializeUI() {
        // Navigation buttons
        const navButtons = document.querySelectorAll('.nav-btn');
        navButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const viewName = e.target.id.replace('Btn', '');
                this.switchView(viewName);
            });
        });
    }

    switchView(viewName) {
        // Update navigation
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(viewName + 'Btn').classList.add('active');

        // Update views
        document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
        document.getElementById(viewName + 'View').classList.add('active');

        this.currentView = viewName;
        this.loadData(viewName);
    }

    loadInitialData() {
        this.loadData('tasks');
    }

    async loadData(type) {
        const container = document.getElementById(type + 'Data');
        this.showLoading();
        this.hideError();

        try {
            let query;
            switch (type) {
                case 'tasks':
                    query = this.getTasksQuery();
                    break;
                case 'notes':
                    query = this.getNotesQuery();
                    break;
                case 'contacts':
                    query = this.getContactsQuery();
                    break;
                case 'projects':
                    query = this.getProjectsQuery();
                    break;
                case 'bookmarks':
                    query = this.getBookmarksQuery();
                    break;
                case 'events':
                    query = this.getEventsQuery();
                    break;
                case 'tags':
                    query = this.getTagsQuery();
                    break;
                default:
                    query = this.getGenericQuery(type);
            }

            const data = await this.executeSparqlQuery(query);
            this.hideLoading();
            this.renderData(container, data, type);
        } catch (error) {
            this.hideLoading();
            this.showError(`Failed to load ${type}: ${error.message}`);
        }
    }

    async executeSparqlQuery(query) {
        const response = await fetch(this.fusekiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/sparql-query',
                'Accept': 'application/sparql-results+json'
            },
            body: query
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return data.results.bindings;
    }

    renderData(container, data, type) {
        if (data.length === 0) {
            container.innerHTML = '<p class="no-data">No data found.</p>';
            return;
        }

        let html = '';
        data.forEach(item => {
            html += this.renderItem(item, type);
        });
        container.innerHTML = html;
    }

    renderItem(item, type) {
        const uri = item.uri ? item.uri.value : '';
        const title = item.title ? item.title.value : (item.label ? item.label.value : 'Untitled');
        const description = item.description ? item.description.value : '';
        
        let html = `<div class="item">`;
        html += `<div class="item-title">${this.escapeHtml(title)}</div>`;
        
        if (description) {
            html += `<div class="item-description">${this.escapeHtml(description)}</div>`;
        }

        // Add type-specific properties
        if (type === 'tasks') {
            const status = item.status ? item.status.value : '';
            const priority = item.priority ? item.priority.value : '';
            const assignedTo = item.assignedTo ? item.assignedTo.value : '';

            if (status) {
                html += `<span class="item-property status-${status}">${status}</span>`;
            }
            if (priority) {
                html += `<span class="item-property">Priority: ${priority}</span>`;
            }
            if (assignedTo) {
                html += `<span class="item-property">Assigned: ${this.getShortUri(assignedTo)}</span>`;
            }
        } else if (type === 'notes') {
            const creator = item.creator ? item.creator.value : '';
            const created = item.created ? item.created.value : '';

            if (creator) {
                html += `<span class="item-property">Creator: ${this.getShortUri(creator)}</span>`;
            }
            if (created) {
                html += `<span class="item-property">Created: ${created}</span>`;
            }
        } else if (type === 'contacts') {
            const email = item.email ? item.email.value : '';
            const phone = item.phone ? item.phone.value : '';

            if (email) {
                html += `<span class="item-property">Email: ${email}</span>`;
            }
            if (phone) {
                html += `<span class="item-property">Phone: ${phone}</span>`;
            }
        }

        // Add tags if present
        if (item.tags) {
            const tags = item.tags.value.split(',');
            tags.forEach(tag => {
                if (tag.trim()) {
                    html += `<span class="item-property">#${this.getShortUri(tag.trim())}</span>`;
                }
            });
        }

        if (uri) {
            html += `<div class="item-uri">${this.getShortUri(uri)}</div>`;
        }

        html += `</div>`;
        return html;
    }

    getTasksQuery() {
        return `
            PREFIX : <https://ben.example/pim/>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX pim: <https://ben.example/ns/pim#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            SELECT ?uri ?title ?status ?priority ?assignedTo ?description
                   (GROUP_CONCAT(DISTINCT ?tag; separator=",") as ?tags)
            WHERE {
                ?uri a :Task .
                OPTIONAL { ?uri dcterms:title ?title }
                OPTIONAL { ?uri :status ?status }
                OPTIONAL { ?uri :priority ?priority }
                OPTIONAL { ?uri :assignedTo ?assignedTo }
                OPTIONAL { ?uri dcterms:description ?description }
                OPTIONAL { ?uri :hasTag ?tag }
            }
            GROUP BY ?uri ?title ?status ?priority ?assignedTo ?description
            ORDER BY ?priority ?title
        `;
    }

    getNotesQuery() {
        return `
            PREFIX : <https://ben.example/pim/>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX schema: <https://schema.org/>

            SELECT ?uri ?title ?description ?creator ?created
                   (GROUP_CONCAT(DISTINCT ?tag; separator=",") as ?tags)
            WHERE {
                ?uri a :Note .
                OPTIONAL { ?uri dcterms:title ?title }
                OPTIONAL { ?uri dcterms:description ?description }
                OPTIONAL { ?uri dcterms:creator ?creator }
                OPTIONAL { ?uri dcterms:created ?created }
                OPTIONAL { ?uri :hasTag ?tag }
            }
            GROUP BY ?uri ?title ?description ?creator ?created
            ORDER BY ?created ?title
        `;
    }

    getContactsQuery() {
        return `
            PREFIX : <https://ben.example/pim/>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
            PREFIX schema: <https://schema.org/>

            SELECT ?uri ?title ?label ?email ?phone ?description
            WHERE {
                {
                    ?uri a :Person .
                } UNION {
                    ?uri a foaf:Person .
                } UNION {
                    ?uri a schema:Person .
                }
                OPTIONAL { ?uri dcterms:title ?title }
                OPTIONAL { ?uri rdfs:label ?label }
                OPTIONAL { ?uri :email ?email }
                OPTIONAL { ?uri foaf:mbox ?email }
                OPTIONAL { ?uri vcard:hasEmail ?email }
                OPTIONAL { ?uri :phone ?phone }
                OPTIONAL { ?uri vcard:hasTelephone ?phone }
                OPTIONAL { ?uri dcterms:description ?description }
            }
            ORDER BY ?label ?title
        `;
    }

    getProjectsQuery() {
        return `
            PREFIX : <https://ben.example/pim/>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX pim: <https://ben.example/ns/pim#>

            SELECT ?uri ?title ?description ?status
            WHERE {
                {
                    ?uri a :Project .
                } UNION {
                    ?uri a pim:Project .
                }
                OPTIONAL { ?uri dcterms:title ?title }
                OPTIONAL { ?uri dcterms:description ?description }
                OPTIONAL { ?uri :status ?status }
                OPTIONAL { ?uri pim:status ?status }
            }
            ORDER BY ?title
        `;
    }

    getBookmarksQuery() {
        return `
            PREFIX : <https://ben.example/pim/>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX schema: <https://schema.org/>

            SELECT ?uri ?title ?url ?description ?created
            WHERE {
                {
                    ?uri a :Bookmark .
                } UNION {
                    ?uri a schema:BookmarkAction .
                }
                OPTIONAL { ?uri dcterms:title ?title }
                OPTIONAL { ?uri :url ?url }
                OPTIONAL { ?uri schema:url ?url }
                OPTIONAL { ?uri dcterms:description ?description }
                OPTIONAL { ?uri dcterms:created ?created }
            }
            ORDER BY ?created ?title
        `;
    }

    getEventsQuery() {
        return `
            PREFIX : <https://ben.example/pim/>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX ical: <http://www.w3.org/2002/12/cal/ical#>
            PREFIX schema: <https://schema.org/>

            SELECT ?uri ?title ?description ?startDate ?endDate ?location
            WHERE {
                {
                    ?uri a :Event .
                } UNION {
                    ?uri a ical:Vevent .
                } UNION {
                    ?uri a schema:Event .
                }
                OPTIONAL { ?uri dcterms:title ?title }
                OPTIONAL { ?uri dcterms:description ?description }
                OPTIONAL { ?uri :startDate ?startDate }
                OPTIONAL { ?uri ical:dtstart ?startDate }
                OPTIONAL { ?uri schema:startDate ?startDate }
                OPTIONAL { ?uri :endDate ?endDate }
                OPTIONAL { ?uri ical:dtend ?endDate }
                OPTIONAL { ?uri schema:endDate ?endDate }
                OPTIONAL { ?uri :location ?location }
                OPTIONAL { ?uri schema:location ?location }
            }
            ORDER BY ?startDate ?title
        `;
    }

    getTagsQuery() {
        return `
            PREFIX : <https://ben.example/pim/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX dcterms: <http://purl.org/dc/terms/>

            SELECT ?uri ?title ?label ?description
                   (COUNT(?tagged) as ?usage)
            WHERE {
                {
                    ?uri a :Tag .
                } UNION {
                    ?uri a skos:Concept .
                }
                OPTIONAL { ?uri dcterms:title ?title }
                OPTIONAL { ?uri rdfs:label ?label }
                OPTIONAL { ?uri skos:prefLabel ?label }
                OPTIONAL { ?uri dcterms:description ?description }
                OPTIONAL { ?tagged :hasTag ?uri }
            }
            GROUP BY ?uri ?title ?label ?description
            ORDER BY DESC(?usage) ?label ?title
        `;
    }

    getShortUri(uri) {
        if (!uri) return '';
        return uri.replace('https://ben.example/pim/', ':')
                 .replace('https://ben.example/ns/pim#', 'pim:')
                 .replace('http://purl.org/dc/terms/', 'dcterms:')
                 .replace('https://schema.org/', 'schema:')
                 .replace('http://xmlns.com/foaf/0.1/', 'foaf:')
                 .replace('http://www.w3.org/2004/02/skos/core#', 'skos:');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    }

    showError(message) {
        const errorEl = document.getElementById('error');
        errorEl.textContent = message;
        errorEl.classList.remove('hidden');
    }

    hideError() {
        document.getElementById('error').classList.add('hidden');
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new RDFBrowser();
});