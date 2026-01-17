import './style.css';
import { App } from './App.js';
import { AuthView } from './views/AuthView.js';
import { DashboardView } from './views/DashboardView.js';
import { Router } from './router.js';
import { api } from './services/api.js';

const appContainer = document.querySelector('#app');

const renderView = async (htmlPromise) => {
  const container = document.getElementById('view-container');
  if (container) {
    container.innerHTML = await htmlPromise;
  }
};

const routes = {
  '/': async () => {
    if (!api.currentUser) return (window.location.hash = '/auth/login');
    toggleLayout(true);
    await renderView(DashboardView.render());
    DashboardView.loadItems();
  },
  '/files': async () => {
    if (!api.currentUser) return (window.location.hash = '/auth/login');
    toggleLayout(true);
    await renderView(DashboardView.render());
    DashboardView.loadItems();
  },
  '/trash': async () => {
    if (!api.currentUser) return (window.location.hash = '/auth/login');
    toggleLayout(true);
    renderView(`
      <div class="explorer">
        <h2 class="text-gradient">Corbeille</h2>
        <div class="glass-bright" style="margin-top: 2rem; padding: 3rem; border-radius: 1rem; text-align: center; color: var(--color-text-muted)">
           <p>Votre corbeille est vide</p>
        </div>
      </div>
    `);
  },
  '/settings': async () => {
    if (!api.currentUser) return (window.location.hash = '/auth/login');
    toggleLayout(true);
    renderView('<div class="explorer"><h2 class="text-gradient">Paramètres</h2></div>');
  },
  '/auth/:mode': (params) => {
    if (api.currentUser) return (window.location.hash = '/');
    toggleLayout(false);
    appContainer.innerHTML = AuthView.render(params.mode);
    AuthView.initEventListeners(params.mode);
  }
};

async function toggleLayout(show) {
  const hasLayout = !!document.querySelector('.app-layout');
  if (show && !hasLayout) {
    appContainer.innerHTML = App.render();
    App.initEventListeners();
  }
}

// Global App Initialization
(async () => {
  await api.getMe(); // Check if logged in
  const router = new Router(routes);
})();

// Sync active nav links
window.addEventListener('hashchange', () => {
  const hash = window.location.hash || '#/';
  document.querySelectorAll('.nav-item').forEach(item => {
    // Exact match for the href
    const itemHref = item.getAttribute('href');
    item.classList.toggle('active', itemHref === hash);
  });
});
