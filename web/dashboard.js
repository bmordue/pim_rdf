/**
 * PIM RDF Dashboard Main Application
 * Handles UI interactions and data display
 */

class Dashboard {
    constructor() {
        this.client = new SPARQLClient();
        this.currentView = 'dashboard';
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.checkConnection();
        this.loadView('dashboard');
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const view = e.target.dataset.view;
                this.loadView(view);
            });
        });

        // Task filters
        document.getElementById('task-status-filter').addEventListener('change', () => {
            this.loadTasks();
        });
        
        document.getElementById('task-priority-filter').addEventListener('change', () => {
            this.loadTasks();
        });
        
        document.getElementById('task-sort').addEventListener('change', () => {
            this.loadTasks();
        });

        // Notes filters
        document.getElementById('notes-search').addEventListener('input', 
            this.debounce(() => this.loadNotes(), 300)
        );
        
        document.getElementById('notes-sort').addEventListener('change', () => {
            this.loadNotes();
        });
    }

    async checkConnection() {
        try {
            const status = await this.client.testConnection();
            if (!status.connected) {
                this.showToast(`SPARQL endpoint not available: ${status.error}`, 'error');
                console.warn('SPARQL endpoint not available, using demo data');
                this.useDemoData = true;
            } else {
                console.log(`Connected to SPARQL endpoint. ${status.tripleCount} triples available.`);
                this.useDemoData = false;
            }
        } catch (error) {
            this.showToast('Connection check failed', 'error');
            this.useDemoData = true;
        }
    }

    loadView(viewName) {
        // Update navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === viewName);
        });

        // Update views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.toggle('active', view.id === `${viewName}-view`);
        });

        this.currentView = viewName;

        // Load view data
        switch (viewName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'tasks':
                this.loadTasks();
                break;
            case 'notes':
                this.loadNotes();
                break;
        }
    }

    async loadDashboard() {
        try {
            // Load statistics
            const stats = this.useDemoData ? this.getDemoStats() : await this.client.getDashboardStats();
            this.updateStats(stats);

            // Load recent items
            const recentItems = this.useDemoData ? this.getDemoRecentItems() : await this.client.getRecentItems();
            this.updateRecentTasks(recentItems.tasks);
            this.updateRecentNotes(recentItems.notes);
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    async loadTasks() {
        const listElement = document.getElementById('tasks-list');
        listElement.innerHTML = '<div class="loading">Loading tasks...</div>';

        try {
            const filters = {
                status: document.getElementById('task-status-filter').value,
                priority: document.getElementById('task-priority-filter').value,
                sort: document.getElementById('task-sort').value
            };

            const tasks = this.useDemoData ? this.getDemoTasks() : await this.client.getAllTasks(filters);
            this.renderTasks(tasks, listElement);
        } catch (error) {
            console.error('Error loading tasks:', error);
            listElement.innerHTML = '<div class="error">Failed to load tasks</div>';
        }
    }

    async loadNotes() {
        const listElement = document.getElementById('notes-list');
        listElement.innerHTML = '<div class="loading">Loading notes...</div>';

        try {
            const filters = {
                search: document.getElementById('notes-search').value,
                sort: document.getElementById('notes-sort').value
            };

            const notes = this.useDemoData ? this.getDemoNotes() : await this.client.getAllNotes(filters);
            this.renderNotes(notes, listElement);
        } catch (error) {
            console.error('Error loading notes:', error);
            listElement.innerHTML = '<div class="error">Failed to load notes</div>';
        }
    }

    updateStats(stats) {
        document.getElementById('open-tasks-count').textContent = stats.openTasks || 0;
        document.getElementById('notes-count').textContent = stats.totalNotes || 0;
        document.getElementById('projects-count').textContent = stats.projects || 0;
        document.getElementById('events-count').textContent = stats.events || 0;
    }

    updateRecentTasks(tasks) {
        const container = document.getElementById('recent-tasks-list');
        if (!tasks || tasks.length === 0) {
            container.innerHTML = '<div class="loading">No tasks found</div>';
            return;
        }

        container.innerHTML = tasks.map(task => `
            <div class="item-card">
                <div class="item-title">${this.escapeHtml(task.title)}</div>
                <div class="item-meta">
                    <span class="item-status status-${task.status}">${task.status}</span>
                    <span class="priority priority-${task.priority}">Priority ${task.priority}</span>
                </div>
            </div>
        `).join('');
    }

    updateRecentNotes(notes) {
        const container = document.getElementById('recent-notes-list');
        if (!notes || notes.length === 0) {
            container.innerHTML = '<div class="loading">No notes found</div>';
            return;
        }

        container.innerHTML = notes.map(note => `
            <div class="item-card">
                <div class="item-title">${this.escapeHtml(note.title)}</div>
                <div class="item-meta">
                    ${note.created ? `<span>Created: ${this.formatDate(note.created)}</span>` : ''}
                </div>
            </div>
        `).join('');
    }

    renderTasks(tasks, container) {
        if (!tasks || tasks.length === 0) {
            container.innerHTML = '<div class="loading">No tasks found</div>';
            return;
        }

        container.innerHTML = tasks.map(task => `
            <div class="item-card">
                <div class="item-title">${this.escapeHtml(task.title)}</div>
                <div class="item-meta">
                    <span class="item-status status-${task.status}">${task.status}</span>
                    <span class="priority priority-${task.priority}">Priority ${task.priority}</span>
                    ${task.created ? `<span>Created: ${this.formatDate(task.created)}</span>` : ''}
                </div>
            </div>
        `).join('');
    }

    renderNotes(notes, container) {
        if (!notes || notes.length === 0) {
            container.innerHTML = '<div class="loading">No notes found</div>';
            return;
        }

        container.innerHTML = notes.map(note => `
            <div class="item-card">
                <div class="item-title">${this.escapeHtml(note.title)}</div>
                <div class="item-meta">
                    ${note.created ? `<span>Created: ${this.formatDate(note.created)}</span>` : ''}
                    ${note.creator ? `<span>By: ${this.escapeHtml(note.creator)}</span>` : ''}
                </div>
                ${note.text ? `<div class="note-text">${this.escapeHtml(this.truncateText(note.text, 150))}</div>` : ''}
            </div>
        `).join('');
    }

    // Demo data methods (fallback when SPARQL endpoint is not available)
    getDemoStats() {
        return {
            openTasks: 1,
            totalNotes: 1,
            projects: 1,
            events: 1
        };
    }

    getDemoRecentItems() {
        return {
            tasks: [{
                title: "Finish RDF PIM design",
                status: "todo",
                priority: 2
            }],
            notes: [{
                title: "First RDF note",
                created: "2025-08-18T14:00:00Z"
            }]
        };
    }

    getDemoTasks() {
        return [{
            title: "Finish RDF PIM design",
            status: "todo",
            priority: 2,
            created: "2025-08-18T14:30:00Z"
        }];
    }

    getDemoNotes() {
        return [{
            title: "First RDF note",
            text: "This is a test note in the RDF knowledge base.",
            created: "2025-08-18T14:00:00Z"
        }];
    }

    // Utility methods
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    formatDate(dateString) {
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString();
        } catch {
            return dateString;
        }
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    showError(message) {
        document.querySelectorAll('.loading').forEach(el => {
            el.innerHTML = `<div class="error">${message}</div>`;
        });
    }

    showToast(message, type = 'error') {
        const toast = document.getElementById('error-toast');
        const content = toast.querySelector('.toast-content');
        
        content.textContent = message;
        toast.className = `toast ${type}`;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 5000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});