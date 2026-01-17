import { i18n } from '../i18n.js';
import { api } from '../services/api.js';

export const AuthView = {
  render(mode = 'login') {
    const isLogin = mode === 'login';

    return `
      <div class="auth-page">
        <div class="auth-card glass">
          <div class="auth-header">
            <img src="/logo.png" alt="Logo" style="width: 80px; height: 80px; margin-bottom: 1rem;">
            <h1 class="text-gradient" style="font-size: 2.5rem; margin-bottom: 0.5rem">${i18n.t('brand')}</h1>
            <h2 style="font-weight: 500">${isLogin ? i18n.t('auth_login') : i18n.t('auth_signup')}</h2>
            <p style="margin-top: 0.5rem">${i18n.t('welcome')}</p>
          </div>
          
          <form class="auth-form" id="auth-form">
            <div id="auth-error" class="text-accent" style="color: var(--color-error); font-size: 0.9rem; text-align: center; display: none;"></div>
            
            ${!isLogin ? `
              <div class="form-group">
                <label>${i18n.lang === 'ar' ? 'الاسم' : 'Nom'}</label>
                <input type="text" id="display_name" placeholder="John Doe" class="glass-bright">
              </div>
            ` : ''}

            <div class="form-group">
              <label>Email</label>
              <input type="email" id="email" placeholder="name@example.dz" required class="glass-bright">
            </div>
            
            <div class="form-group">
              <label>${i18n.lang === 'ar' ? 'كلمة المرور' : 'Mot de passe'}</label>
              <input type="password" id="password" placeholder="••••••••" required class="glass-bright">
            </div>
            
            <button type="submit" class="btn-primary" id="submit-btn" style="margin-top: 1rem">
              ${isLogin ? i18n.t('auth_login') : i18n.t('auth_signup')}
            </button>
          </form>
          
          <div class="auth-footer">
            <p>
              ${isLogin ? (i18n.lang === 'ar' ? "ليس لديك حساب؟" : "Nouveau ici ?") : (i18n.lang === 'ar' ? "لديك حساب؟" : "Déjà un compte ?")} 
              <br>
              <a href="#/auth/${isLogin ? 'signup' : 'login'}" style="display: inline-block; margin-top: 0.5rem; font-weight: 600; color: var(--color-accent)">
                ${isLogin ? i18n.t('auth_signup') : i18n.t('auth_login')}
              </a>
            </p>
          </div>
        </div>
      </div>
    `;
  },

  initEventListeners(currentMode) {
    const form = document.getElementById('auth-form');
    const errorEl = document.getElementById('auth-error');
    const submitBtn = document.getElementById('submit-btn');

    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const displayName = document.getElementById('display_name')?.value;

        errorEl.style.display = 'none';
        submitBtn.disabled = true;
        submitBtn.textContent = i18n.lang === 'ar' ? 'جاري التحميل...' : 'Chargement...';

        try {
          if (currentMode === 'login') {
            await api.login(email, password);
          } else {
            await api.register({ email, password, display_name: displayName });
          }
          // Success -> Dashboard
          window.location.hash = '/';
          window.location.reload(); // Force app re-render with new user state
        } catch (err) {
          errorEl.textContent = err.message;
          errorEl.style.display = 'block';
          submitBtn.disabled = false;
          submitBtn.textContent = currentMode === 'login' ? i18n.t('auth_login') : i18n.t('auth_signup');
        }
      });
    }
  }
};
