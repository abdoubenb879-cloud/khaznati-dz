/**
 * Khaznati DZ - Main Application Logic
 * خزنتي - المنطق الرئيسي
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Systems
    Toast.init();
    I18n.init();

    // Setup Global Event Listeners
    setupGlobalEvents();

    // Handle specific page logic based on URL/Content
    handlePageLogic();
});

/**
 * Setup global UI events (Language switcher, mobile menu, etc.)
 */
function setupGlobalEvents() {
    // Language Switcher Toggle
    const langToggle = document.getElementById('lang-toggle');
    const langDropdown = document.getElementById('lang-dropdown');

    if (langToggle && langDropdown) {
        langToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            langToggle.classList.toggle('open');
            langDropdown.classList.toggle('open');
        });

        // Language Selection
        document.querySelectorAll('.lang-option').forEach(btn => {
            btn.addEventListener('click', () => {
                const lang = btn.dataset.lang;
                I18n.setLocale(lang);
                langToggle.classList.remove('open');
                langDropdown.classList.remove('open');
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!langToggle.contains(e.target)) {
                langToggle.classList.remove('open');
                langDropdown.classList.remove('open');
            }
        });
    }

    // Mobile Menu Toggle
    const menuToggle = document.getElementById('mobile-menu-toggle');
    const mainNav = document.querySelector('.main-nav');

    if (menuToggle && mainNav) {
        menuToggle.addEventListener('click', () => {
            menuToggle.classList.toggle('open');
            // Toggle visibility class for mobile nav (needs CSS support)
            // For now just logging, CSS implementation can be added in V1 polish
            console.log('Mobile menu toggled');
        });
    }

    // Password Visibility Toggle
    document.querySelectorAll('.password-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.previousElementSibling;
            if (input && input.type) {
                if (input.type === 'password') {
                    input.type = 'text';
                    // Optional: change icon to "eye-off"
                    btn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;
                } else {
                    input.type = 'password';
                    // Optional: change icon back to "eye"
                    btn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;
                }
            }
        });
    });
}

/**
 * Handle page-specific logic
 */
function handlePageLogic() {
    // Login Form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = loginForm.email.value;
            const password = loginForm.password.value;
            const rememberMe = loginForm.remember_me?.checked || false;

            // Basic client-side validation
            if (!email || !password) {
                Toast.error(I18n.translate('valid.required'));
                return;
            }

            Loading.show();
            Form.disable(loginForm);

            try {
                // TODO: Replace with actual API call when backend is running
                // const res = await API.post('/auth/login', { email, password, remember_me: rememberMe });

                // Mock success for now since backend might not be on same port yet
                console.log('Login attempt:', { email, password, rememberMe });

                // Simulate network delay
                await new Promise(r => setTimeout(r, 1000));

                Toast.success(I18n.translate('success'));
                // window.location.href = '/dashboard';
            } catch (err) {
                Toast.error(err.message || I18n.translate('error'));
            } finally {
                Loading.hide();
                Form.enable(loginForm);
            }
        });
    }

    // Register Form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const data = Form.getData(registerForm);

            // Validation
            if (data.password !== data.password_confirm) {
                Form.setErrors(registerForm, { password_confirm: I18n.translate('valid.password_match') });
                return;
            }

            if (data.password.length < 8) {
                Form.setErrors(registerForm, { password: I18n.translate('valid.password_min') });
                return;
            }

            Loading.show();
            Form.disable(registerForm);

            try {
                // TODO: Replace with actual API call
                console.log('Register attempt:', data);

                await new Promise(r => setTimeout(r, 1500));

                Toast.success(I18n.translate('auth.register_cta') + ' ' + I18n.translate('success'));
                // window.location.href = '/login';
            } catch (err) {
                Toast.error(err.message || I18n.translate('error'));
            } finally {
                Loading.hide();
                Form.enable(registerForm);
            }
        });
    }
}
