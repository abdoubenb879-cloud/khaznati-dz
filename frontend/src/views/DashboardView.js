import { i18n } from '../i18n.js';

export const DashboardView = {
    render(files = []) {
        return `
      <div class="explorer">
        <div class="explorer-header">
           <div class="breadcrumbs">
             <a href="#/files" class="breadcrumb-item">Mes Fichiers</a>
             <span class="separator">/</span>
             <span class="current">Documents</span>
           </div>
           
           <div class="explorer-actions">
             <button class="btn-action glass-bright">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
                <span>Upload</span>
             </button>
           </div>
        </div>

        <div class="file-grid">
          ${this.renderFolders()}
          ${this.renderFiles(files)}
        </div>
      </div>
    `;
    },

    renderFolders() {
        const folders = ['Projets', 'Photos', 'Factures'];
        return folders.map(name => `
      <div class="file-item folder glass-bright">
        <div class="file-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="var(--color-primary)" stroke="none"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93l-2.73-2.73A1.977 1.977 0 0 0 8.04 2H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2z"/></svg>
        </div>
        <div class="file-info">
          <span class="file-name">${name}</span>
          <span class="file-meta">5 fichiers</span>
        </div>
      </div>
    `).join('');
    },

    renderFiles(files) {
        const dummyFiles = [
            { name: 'Rapport_Final.pdf', size: '1.2 MB', type: 'pdf' },
            { name: 'Design_Logo.svg', size: '450 KB', type: 'image' },
            { name: 'Vacances_Tipaza.jpg', size: '3.4 MB', type: 'image' }
        ];

        return dummyFiles.map(file => `
      <div class="file-item file glass-bright">
        <div class="file-icon">
          ${this.getIconForType(file.type)}
        </div>
        <div class="file-info">
          <span class="file-name">${file.name}</span>
          <span class="file-meta">${file.size}</span>
        </div>
        <button class="file-more">
           <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>
        </button>
      </div>
    `).join('');
    },

    getIconForType(type) {
        if (type === 'pdf') return `<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>`;
        return `<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>`;
    }
};
