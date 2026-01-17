import { i18n } from '../i18n.js';
import { api } from '../services/api.js';

export const DashboardView = {
  currentPath: [], // Array of {id, name}

  async render(parentId = null) {
    // Return shell first, items will be loaded via init
    return `
            <div class="explorer">
                <div class="explorer-header" id="explorer-header-inner">
                    ${this.renderBreadcrumbs()}
                    
                    <div class="explorer-actions">
                        <button class="btn-action glass-bright" id="new-folder-btn">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 18H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h3l2 2h7a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-3"/><circle cx="12" cy="12" r="3"/></svg>
                            <span>${i18n.t('new_folder')}</span>
                        </button>
                        <button class="btn-action glass-bright grad-premium" id="upload-btn" style="border: none">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
                            <span>${i18n.t('upload_cta')}</span>
                        </button>
                    </div>
                </div>

                <div class="file-grid" id="file-grid">
                    <div style="grid-column: 1/-1; text-align: center; padding: 4rem; color: var(--color-text-muted)">
                        ${i18n.lang === 'ar' ? 'جاري تحميل الملفات...' : 'Chargement des fichiers...'}
                    </div>
                </div>
            </div>
        `;
  },

  renderBreadcrumbs() {
    const rootName = i18n.t('nav_files');
    let html = `
            <div class="breadcrumbs" id="breadcrumbs-nav">
                <a href="#" class="breadcrumb-item" data-id="root">${rootName}</a>
        `;

    this.currentPath.forEach((folder, index) => {
      html += `
                <span class="separator">/</span>
                <span class="current">${folder.name}</span>
            `;
    });

    html += '</div>';
    return html;
  },

  async loadItems() {
    const grid = document.getElementById('file-grid');
    if (!grid) return;

    const parentId = this.currentPath.length > 0 ? this.currentPath[this.currentPath.length - 1].id : null;

    try {
      const items = await api.listFiles(parentId);

      if (items.length === 0) {
        grid.innerHTML = `
                    <div style="grid-column: 1/-1; text-align: center; padding: 5rem; color: var(--color-text-muted); width: 100%">
                        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="margin-bottom: 1rem; opacity: 0.3"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9Z"/><path d="M13 2v7h7"/></svg>
                        <p>${i18n.t('empty_files')}</p>
                    </div>
                `;
      } else {
        grid.innerHTML = items.map(item => this.renderItem(item)).join('');
      }
      this.initEventListeners(items);
    } catch (err) {
      grid.innerHTML = `<div style="grid-column: 1/-1; color: var(--color-error); text-align: center; padding: 2rem;">${err.message}</div>`;
    }
  },

  renderItem(item) {
    const isFolder = item.is_folder || false;
    const iconColor = isFolder ? 'var(--color-accent)' : 'var(--color-primary-light)';

    return `
            <div class="file-item ${isFolder ? 'folder' : 'file'} glass-bright" data-id="${item.id}" data-name="${item.filename}" data-folder="${isFolder}">
                <div class="file-icon">
                    ${isFolder
        ? `<svg width="40" height="40" viewBox="0 0 24 24" fill="${iconColor}" stroke="none"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93l-2.73-2.73A1.977 1.977 0 0 0 8.04 2H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2z"/></svg>`
        : this.getIconForType(item.filename.split('.').pop().toLowerCase())
      }
                </div>
                <div class="file-info" style="pointer-events: none">
                    <span class="file-name" title="${item.filename}">${item.filename}</span>
                    <span class="file-meta">${isFolder ? `... ${i18n.t('items')}` : this.formatSize(item.total_size)}</span>
                </div>
                <button class="file-more">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>
                </button>
            </div>
        `;
  },

  initEventListeners(items) {
    document.querySelectorAll('.file-item').forEach(el => {
      el.addEventListener('click', (e) => {
        if (e.target.closest('.file-more')) return;

        const id = el.dataset.id;
        const name = el.dataset.name;
        const isFolder = el.dataset.folder === 'true';

        if (isFolder) {
          this.currentPath.push({ id, name });
          this.refresh();
        } else {
          window.open(`/api/files/${id}/download`, '_blank');
        }
      });
    });

    document.getElementById('upload-btn')?.addEventListener('click', () => {
      document.getElementById('global-upload-btn')?.click();
    });

    document.getElementById('new-folder-btn')?.addEventListener('click', async () => {
      const name = prompt(i18n.t('new_folder'));
      if (name) {
        const parentId = this.currentPath.length > 0 ? this.currentPath[this.currentPath.length - 1].id : null;
        try {
          await api.createFolder(name, parentId);
          this.refresh();
        } catch (err) { alert(err.message); }
      }
    });

    document.querySelector('[data-id="root"]')?.addEventListener('click', (e) => {
      e.preventDefault();
      this.currentPath = [];
      this.refresh();
    });
  },

  refresh() {
    const container = document.getElementById('view-container');
    if (container) {
      this.render().then(html => {
        container.innerHTML = html;
        this.loadItems();
      });
    }
  },

  getIconForType(ext) {
    const color = 'var(--color-primary-light)';
    if (['pdf'].includes(ext)) return `<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>`;
    if (['jpg', 'jpeg', 'png', 'svg'].includes(ext)) return `<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>`;
    return `<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>`;
  },

  formatSize(bytes) {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }
};
