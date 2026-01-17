const translations = {
    ar: {
        brand: 'خزنتي',
        nav_home: 'الرئيسية',
        nav_files: 'ملفاتي',
        nav_trash: 'المهملات',
        nav_settings: 'الإعدادات',
        search_placeholder: 'بحث عن ملفات...',
        upload_cta: 'رفع ملف',
        welcome: 'مرحباً بعودتك',
        auth_login: 'تسجيل الدخول',
        auth_signup: 'إنشاء حساب',
        new_folder: 'مجلد جديد',
        empty_files: 'لا توجد ملفات هنا',
        delete: 'حذف',
        rename: 'تغيير الاسم',
        download: 'تحميل',
        restore: 'استعادة',
        items: 'عناصر'
    },
    fr: {
        brand: 'Khaznati',
        nav_home: 'Accueil',
        nav_files: 'Mes Fichiers',
        nav_trash: 'Corbeille',
        nav_settings: 'Paramètres',
        search_placeholder: 'Rechercher des fichiers...',
        upload_cta: 'Téléverser',
        welcome: 'Bon retour',
        auth_login: 'Connexion',
        auth_signup: 'Inscription',
        new_folder: 'Nouveau dossier',
        empty_files: 'Aucun fichier trouvé',
        delete: 'Supprimer',
        rename: 'Renommer',
        download: 'Télécharger',
        restore: 'Restaurer',
        items: 'éléments'
    }
};

class I18n {
    constructor() {
        this.lang = localStorage.getItem('khaznati_lang') || 'fr';
        this.applyDirection();
    }

    setLanguage(lang) {
        if (translations[lang]) {
            this.lang = lang;
            localStorage.setItem('khaznati_lang', lang);
            this.applyDirection();
            window.location.reload(); // Simple way to re-render everything
        }
    }

    t(key) {
        return translations[this.lang][key] || key;
    }

    applyDirection() {
        const isRtl = this.lang === 'ar';
        document.documentElement.setAttribute('dir', isRtl ? 'rtl' : 'ltr');
        document.documentElement.setAttribute('lang', this.lang);
    }
}

export const i18n = new I18n();
