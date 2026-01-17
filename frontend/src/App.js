import { i18n } from './i18n.js';

export const App = {
  render() {
    return `
      <div class="app-layout">
        <!-- Sidebar (Desktop) -->
        <aside class="sidebar glass">
          <div class="logo-area">
            <h1 class="text-gradient">${i18n.t('brand')}</h1>
          </div>
          <nav class="side-nav">
             ${this.renderNavLinks()}
          </nav>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
          <header class="top-bar">
            <div class="search-box glass-bright">
              <input type="text" placeholder="${i18n.t('search_placeholder')}">
            </div>
            <div class="user-actions">
               <button class="btn-lang" id="lang-toggle">${i18n.lang === 'ar' ? 'FR' : 'عربي'}</button>
               <div class="avatar glass-bright">A</div>
            </div>
          </header>
          
          <section id="view-container" class="content-view"></section>
        </main>

        <!-- Bottom Nav (Mobile) -->
        <nav class="bottom-nav glass">
          ${this.renderNavLinks()}
        </nav>

        <!-- Upload Trigger (Mobile) -->
        <button class="fab-upload" id="global-upload">
          <span>+</span>
        </button>

        <!-- Global Dropzone Overlay -->
        <div id="global-dropzone">
           <div class="dropzone-msg">Déposez vos fichiers ici</div>
        </div>

        <!-- Upload Status Container -->
        <div id="upload-status-root"></div>
      </div>
    `;
  },

  renderNavLinks() {
    const icons = {
      home: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`,
      files: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>`,
      trash: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>`,
      settings: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>`
    };

    return `
      <a href="#/" class="nav-item active" data-nav="home">
        ${icons.home}
        <span>${i18n.t('nav_home')}</span>
      </a>
      <a href="#/files" class="nav-item" data-nav="files">
        ${icons.files}
        <span>${i18n.t('nav_files')}</span>
      </a>
      <a href="#/trash" class="nav-item" data-nav="trash">
        ${icons.trash}
        <span>${i18n.t('nav_trash')}</span>
      </a>
      <a href="#/settings" class="nav-item" data-nav="settings">
        ${icons.settings}
        <span>${i18n.t('nav_settings')}</span>
      </a>
    `;
  },

  initEventListeners() {
    document.getElementById('lang-toggle').addEventListener('click', () => {
      const nextLang = i18n.lang === 'ar' ? 'fr' : 'ar';
      i18n.setLanguage(nextLang);
    });

    // Global Drag & Drop logic
    window.addEventListener('dragover', (e) => {
      e.preventDefault();
      document.getElementById('global-dropzone').classList.add('active');
    });

    window.addEventListener('dragleave', (e) => {
      if (e.relatedTarget === null) {
        document.getElementById('global-dropzone').classList.remove('active');
      }
    });

    window.addEventListener('drop', (e) => {
      e.preventDefault();
      document.getElementById('global-dropzone').classList.remove('active');
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        this.simulateUpload(files[0]);
      }
    });
  },

  simulateUpload(file) {
    const root = document.getElementById('upload-status-root');
    import('./components/UploadOverlay.js').then(({ UploadOverlay }) => {
      let progress = 0;
      const interval = setInterval(() => {
        progress += 5;
        root.innerHTML = UploadOverlay.render(progress, file.name);
        if (progress >= 100) {
          clearInterval(interval);
          setTimeout(() => { root.innerHTML = ''; }, 3000);
        }
      }, 200);
    });
  }
};
