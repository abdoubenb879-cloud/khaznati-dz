/**
 * Khaznati DZ - Internationalization (i18n)
 * خزنتي - الترجمة
 */

const translations = {
    // =========================================================================
    // ARABIC (Default)
    // =========================================================================
    ar: {
        // General
        'app.name': 'خزنتي',
        'app.tagline': 'تخزينك السحابي الجزائري',
        'loading': 'جاري التحميل...',
        'error': 'حدث خطأ',
        'success': 'تم بنجاح',

        // Actions
        'save': 'حفظ',
        'cancel': 'إلغاء',
        'delete': 'حذف',
        'edit': 'تعديل',
        'close': 'إغلاق',
        'confirm': 'تأكيد',
        'login': 'تسجيل الدخول',
        'register': 'إنشاء حساب',
        'logout': 'تسجيل الخروج',

        // Navigation
        'nav.home': 'الرئيسية',
        'nav.files': 'ملفاتي',
        'nav.recent': 'الأخيرة',
        'nav.shared': 'المشاركة',
        'nav.trash': 'المحذوفات',
        'nav.settings': 'الإعدادات',

        // Auth
        'auth.email': 'البريد الإلكتروني',
        'auth.password': 'كلمة المرور',
        'auth.password_confirm': 'تأكيد كلمة المرور',
        'auth.name': 'الاسم الكامل',
        'auth.remember': 'تذكرني',
        'auth.forgot_password': 'نسيت كلمة المرور؟',
        'auth.no_account': 'ليس لديك حساب؟',
        'auth.have_account': 'لديك حساب بالفعل؟',
        'auth.register_title': 'أنشئ حسابك في خزنتي',
        'auth.login_title': 'مرحباً بعودتك',
        'auth.register_cta': 'سجل الآن',

        // Validation
        'valid.required': 'هذا الحقل مطلوب',
        'valid.email': 'بريد إلكتروني غير صالح',
        'valid.password_min': 'يجب أن تكون كلمة المرور 8 أحرف على الأقل',
        'valid.password_match': 'كلمات المرور غير متطابقة',

        // File Manager
        'files.upload': 'رفع ملف',
        'files.new_folder': 'مجلد جديد',
        'files.empty': 'لا توجد ملفات هنا',
        'files.search': 'بحث...',
        'files.size': 'الحجم',
        'files.date': 'التاريخ',

        // Landing
        'landing.hero_title': 'خزّن ملفاتك بأمان،<br>وين ما كنت في الجزائر',
        'landing.hero_desc': 'مساحة تخزين سحابية سريعة، آمنة، ومصممة خصيصاً للجزائريين. جربها باطل اليوم.',
        'landing.cta_primary': 'ابدا تجربتك المجانية',
        'landing.cta_secondary': 'تعرف علينا',
        'landing.feature_1': 'سريع وسهل',
        'landing.feature_1_desc': 'يعمل مليح حتى مع انترنت ضعيفة',
        'landing.feature_2': 'خصوصية مضمونة',
        'landing.feature_2_desc': 'ملفاتك مشفرة ومؤمنة 100%',
        'landing.feature_3': 'واجهة بالعربية',
        'landing.feature_3_desc': 'كلش مفهوم وواضح بلغتنا',
    },

    // =========================================================================
    // FRENCH
    // =========================================================================
    fr: {
        // General
        'app.name': 'Khaznati DZ',
        'app.tagline': 'Votre Cloud Algérien',
        'loading': 'Chargement...',
        'error': 'Une erreur est survenue',
        'success': 'Succès',

        // Actions
        'save': 'Enregistrer',
        'cancel': 'Annuler',
        'delete': 'Supprimer',
        'edit': 'Modifier',
        'close': 'Fermer',
        'confirm': 'Confirmer',
        'login': 'Connexion',
        'register': 'Inscription',
        'logout': 'Déconnexion',

        // Navigation
        'nav.home': 'Accueil',
        'nav.files': 'Mes Fichiers',
        'nav.recent': 'Récents',
        'nav.shared': 'Partagés',
        'nav.trash': 'Corbeille',
        'nav.settings': 'Paramètres',

        // Auth
        'auth.email': 'Email',
        'auth.password': 'Mot de passe',
        'auth.password_confirm': 'Confirmer le mot de passe',
        'auth.name': 'Nom complet',
        'auth.remember': 'Se souvenir de moi',
        'auth.forgot_password': 'Mot de passe oublié ?',
        'auth.no_account': 'Pas encore de compte ?',
        'auth.have_account': 'Déjà un compte ?',
        'auth.register_title': 'Créez votre compte Khaznati',
        'auth.login_title': 'Bon retour',
        'auth.register_cta': 'S\'inscrire',

        // Validation
        'valid.required': 'Ce champ est requis',
        'valid.email': 'Email invalide',
        'valid.password_min': 'Le mot de passe doit contenir au moins 8 caractères',
        'valid.password_match': 'Les mots de passe ne correspondent pas',

        // File Manager
        'files.upload': 'Importer',
        'files.new_folder': 'Nouveau dossier',
        'files.empty': 'Aucun fichier ici',
        'files.search': 'Rechercher...',
        'files.size': 'Taille',
        'files.date': 'Date',

        // Landing
        'landing.hero_title': 'Stockez vos fichiers en sécurité,<br>partout en Algérie',
        'landing.hero_desc': 'Un espace cloud rapide, sécurisé et conçu pour les Algériens. Essayez-le gratuitement aujourd\'hui.',
        'landing.cta_primary': 'Commencer gratuitement',
        'landing.cta_secondary': 'En savoir plus',
        'landing.feature_1': 'Rapide & Simple',
        'landing.feature_1_desc': 'Optimisé pour les connexions locales',
        'landing.feature_2': 'Confidentialité',
        'landing.feature_2_desc': 'Vos fichiers sont 100% sécurisés',
        'landing.feature_3': 'Interface Locale',
        'landing.feature_3_desc': 'Disponible en Arabe et Français',
    },

    // =========================================================================
    // ENGLISH
    // =========================================================================
    en: {
        // General
        'app.name': 'Khaznati DZ',
        'app.tagline': 'Your Algerian Cloud',
        'loading': 'Loading...',
        'error': 'An error occurred',
        'success': 'Success',

        // Actions
        'save': 'Save',
        'cancel': 'Cancel',
        'delete': 'Delete',
        'edit': 'Edit',
        'close': 'Close',
        'confirm': 'Confirm',
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',

        // Navigation
        'nav.home': 'Home',
        'nav.files': 'My Files',
        'nav.recent': 'Recent',
        'nav.shared': 'Shared',
        'nav.trash': 'Trash',
        'nav.settings': 'Settings',

        // Auth
        'auth.email': 'Email',
        'auth.password': 'Password',
        'auth.password_confirm': 'Confirm Password',
        'auth.name': 'Full Name',
        'auth.remember': 'Remember me',
        'auth.forgot_password': 'Forgot password?',
        'auth.no_account': 'Don\'t have an account?',
        'auth.have_account': 'Already have an account?',
        'auth.register_title': 'Create your Khaznati account',
        'auth.login_title': 'Welcome back',
        'auth.register_cta': 'Sign up now',

        // Validation
        'valid.required': 'This field is required',
        'valid.email': 'Invalid email address',
        'valid.password_min': 'Password must be at least 8 characters',
        'valid.password_match': 'Passwords do not match',

        // File Manager
        'files.upload': 'Upload',
        'files.new_folder': 'New Folder',
        'files.empty': 'No files here',
        'files.search': 'Search...',
        'files.size': 'Size',
        'files.date': 'Date',

        // Landing
        'landing.hero_title': 'Secure Cloud Storage<br>for Everyone in Algeria',
        'landing.hero_desc': 'Fast, secure, and built for local needs. Start your free storage today.',
        'landing.cta_primary': 'Get Started Free',
        'landing.cta_secondary': 'Learn More',
        'landing.feature_1': 'Fast & Simple',
        'landing.feature_1_desc': 'Works great on local networks',
        'landing.feature_2': 'Secure & Private',
        'landing.feature_2_desc': 'Your files are safe with us',
        'landing.feature_3': 'Local Experience',
        'landing.feature_3_desc': 'Available in Arabic, French & English',
    }
};

const I18n = {
    locale: 'ar',

    /**
     * Initialize i18n
     */
    init() {
        // Get stored locale or default to 'ar'
        this.locale = Storage.get('khaznati_lang', 'ar');
        this.applyLocale(this.locale);

        // Setup global translation function
        window.t = (key) => this.translate(key);

        // Translate page content
        this.translatePage();
    },

    /**
     * Translate a key
     * @param {string} key - Translation key
     * @returns {string} Translated text
     */
    translate(key) {
        const keys = key.split('.');
        let value = translations[this.locale];

        if (!value) return key; // Fallback

        // Simple lookup (no nested support needed for now based on flat structure above)
        // If we switch to nested structure, we'd need traversal here
        return translations[this.locale][key] || key;
    },

    /**
     * Switch language
     * @param {string} lang - Language code (ar, fr, en)
     */
    setLocale(lang) {
        if (!translations[lang]) return;

        this.locale = lang;
        Storage.set('khaznati_lang', lang);
        this.applyLocale(lang);
        this.translatePage();

        // Update URL param if needed, but for now just reload optional
        // location.reload(); 
    },

    /**
     * Apply locale settings (dir, fonts, classes)
     * @param {string} lang - Language code
     */
    applyLocale(lang) {
        const doc = document.documentElement;

        // Set direction
        const dir = lang === 'ar' ? 'rtl' : 'ltr';
        doc.setAttribute('dir', dir);
        doc.setAttribute('lang', lang);

        // Update active class in dropdowns
        document.querySelectorAll('.lang-option').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });

        // Update lang toggle text
        const labels = { ar: 'عربي', fr: 'Français', en: 'English' };
        const labelEl = document.querySelector('.current-lang');
        if (labelEl) labelEl.textContent = labels[lang];
    },

    /**
     * Translate all elements with data-i18n attribute
     */
    translatePage() {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.dataset.i18n;
            if (el.tagName === 'INPUT' && el.getAttribute('placeholder')) {
                el.placeholder = this.translate(key);
            } else {
                el.innerHTML = this.translate(key);
            }
        });
    }
};

// Export for usage
window.I18n = I18n;
