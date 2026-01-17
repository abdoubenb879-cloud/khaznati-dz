/**
 * Khaznati DZ - API Service
 * Backend communication layer
 */

const API_BASE = '/api';

class ApiService {
    constructor() {
        this.currentUser = null;
        this.csrfToken = null;
    }

    /**
     * Generic fetch wrapper with CSRF and error handling
     */
    async request(path, options = {}) {
        const url = `${API_BASE}${path}`;

        // Setup headers
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };

        // Add CSRF to headers if we have it
        if (this.csrfToken) {
            headers['X-CSRF-Token'] = this.csrfToken;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'API request failed');
            }

            return data;
        } catch (error) {
            console.error(`API Error [${path}]:`, error);
            throw error;
        }
    }

    /**
     * File upload specific request (Multipart)
     */
    async upload(path, formData, onProgress) {
        const url = `${API_BASE}${path}`;

        // Note: Don't set Content-Type for FormData, browser does it with boundary
        const headers = {};
        if (this.csrfToken) {
            headers['X-CSRF-Token'] = this.csrfToken;
        }

        // Using XHR for progress tracking if needed, otherwise simplified fetch
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', url);

            if (this.csrfToken) {
                xhr.setRequestHeader('X-CSRF-Token', this.csrfToken);
            }

            xhr.upload.onprogress = (e) => {
                if (e.lengthComputable && onProgress) {
                    const percent = Math.round((e.loaded / e.total) * 100);
                    onProgress(percent);
                }
            };

            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    resolve(JSON.parse(xhr.responseText));
                } else {
                    const error = JSON.parse(xhr.responseText || '{}');
                    reject(new Error(error.detail || 'Upload failed'));
                }
            };

            xhr.onerror = () => reject(new Error('Network error'));
            xhr.send(formData);
        });
    }

    // ========== AUTH ==========

    async login(email, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        this.currentUser = data.user;
        await this.fetchCsrf();
        return data;
    }

    async register(userData) {
        const data = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        this.currentUser = data.user;
        await this.fetchCsrf();
        return data;
    }

    async logout() {
        await this.request('/auth/logout', { method: 'POST' });
        this.currentUser = null;
        this.csrfToken = null;
    }

    async getMe() {
        try {
            const data = await this.request('/auth/me');
            this.currentUser = data;
            await this.fetchCsrf();
            return data;
        } catch (e) {
            this.currentUser = null;
            return null;
        }
    }

    async fetchCsrf() {
        const data = await this.request('/auth/csrf-token');
        this.csrfToken = data.csrf_token;
        return this.csrfToken;
    }

    // ========== FILES & FOLDERS ==========

    async listFiles(parentId = null) {
        const query = parentId ? `?parent_id=${parentId}` : '';
        const data = await this.request(`/files${query}`);
        return data.items || [];
    }

    async createFolder(name, parentId = null) {
        return await this.request('/folders', {
            method: 'POST',
            body: JSON.stringify({ name, parent_id: parentId })
        });
    }

    async uploadFile(file, parentId = null, onProgress) {
        const formData = new FormData();
        formData.append('file', file);
        if (parentId) {
            formData.append('parent_id', parentId);
        }
        return await this.upload('/files/upload', formData, onProgress);
    }

    async deleteFile(fileId) {
        return await this.request(`/files/${fileId}`, { method: 'DELETE' });
    }

    async renameFile(fileId, newName) {
        return await this.request(`/files/${fileId}/rename`, {
            method: 'POST',
            body: JSON.stringify({ name: newName })
        });
    }

    async getDownloadUrl(fileId) {
        // In the new architecture, we get the file data directly or a redirect
        return `/api/files/${fileId}/download`;
    }

    // ========== TRASH ==========

    async listTrash() {
        const data = await this.request('/trash');
        return data.items || [];
    }

    async restoreFromTrash(fileId) {
        return await this.request(`/trash/files/${fileId}/restore`, { method: 'POST' });
    }

    async emptyTrash() {
        return await this.request('/trash/empty', { method: 'POST' });
    }
}

export const api = new ApiService();
