import { i18n } from '../i18n.js';

export const AuthView = {
    render(mode = 'login') {
        const isLogin = mode === 'login';

        return `
      <div class="auth-page">
        <div class="auth-card glass">
          <div class="auth-header">
            <h2 class="text-gradient">${isLogin ? i18n.t('auth_login') : i18n.t('auth_signup')}</h2>
            <p>${i18n.t('welcome')}</p>
          </div>
          
          <form class="auth-form" id="auth-form">
            <div class="form-group">
              <label>Email</label>
              <input type="email" placeholder="email@example.dz" required class="glass-bright">
            </div>
            
            <div class="form-group">
              <label>Password</label>
              <input type="password" placeholder="••••••••" required class="glass-bright">
            </div>
            
            ${!isLogin ? `
              <div class="form-group">
                <label>Confirm Password</label>
                <input type="password" placeholder="••••••••" required class="glass-bright">
              </div>
            ` : ''}
            
            <button type="submit" class="btn-primary">
              ${isLogin ? i18n.t('auth_login') : i18n.t('auth_signup')}
            </button>
          </form>
          
          <div class="auth-footer">
            <p>
              ${isLogin ? "Nouveau ici ?" : "Déjà un compte ?"} 
              <a href="#" id="toggle-auth">
                ${isLogin ? i18n.t('auth_signup') : i18n.t('auth_login')}
              </a>
            </p>
          </div>
        </div>
      </div>
    `;
    },

    initEventListeners(currentMode) {
        const toggleBtn = document.getElementById('toggle-auth');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                const newMode = currentMode === 'login' ? 'signup' : 'login';
                window.location.hash = `/auth/${newMode}`;
            });
        }

        const form = document.getElementById('auth-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                // Redirect to dashboard on logic (mock)
                window.location.hash = '/';
            });
        }
    }
};
