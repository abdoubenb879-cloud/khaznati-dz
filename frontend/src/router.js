export class Router {
    constructor(routes) {
        this.routes = routes;
        this.currentPath = null;

        window.addEventListener('hashchange', () => this.handleRoute());
        window.addEventListener('load', () => this.handleRoute());
    }

    handleRoute() {
        const hash = window.location.hash.slice(1) || '/';

        // Handle parameterized routes like /auth/:mode
        let routeKey = hash;
        let params = {};

        if (hash.startsWith('/auth/')) {
            routeKey = '/auth/:mode';
            params.mode = hash.split('/')[2];
        }

        const route = this.routes[routeKey] || this.routes['/'];

        this.currentPath = hash;
        if (route) {
            route(params);
        }
    }

    navigate(path) {
        window.location.hash = path;
    }
}
