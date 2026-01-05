/**
 * Betsan CRM - API Client
 */

const API = {
    baseUrl: 'http://localhost:8000/api',

    /**
     * Get auth token from storage
     */
    getToken() {
        return localStorage.getItem('access_token');
    },

    /**
     * Set auth token
     */
    setToken(token) {
        localStorage.setItem('access_token', token);
    },

    /**
     * Remove auth token
     */
    removeToken() {
        localStorage.removeItem('access_token');
    },

    /**
     * Get default headers
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    },

    /**
     * Make API request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;

        const config = {
            headers: this.getHeaders(),
            ...options
        };

        try {
            const response = await fetch(url, config);

            // Handle 401 Unauthorized
            if (response.status === 401) {
                this.removeToken();
                window.location.href = '/pages/login.html';
                return;
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'API Error');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        let url = endpoint;
        if (Object.keys(params).length > 0) {
            url += '?' + new URLSearchParams(params).toString();
        }
        return this.request(url, { method: 'GET' });
    },

    /**
     * POST request
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * PUT request
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    },

    /**
     * Upload file
     */
    async upload(endpoint, file, additionalData = {}) {
        const formData = new FormData();
        formData.append('file', file);

        Object.keys(additionalData).forEach(key => {
            formData.append(key, additionalData[key]);
        });

        const token = this.getToken();
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers,
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Upload Error');
        }

        return data;
    },

    // ===== AUTH ENDPOINTS =====
    auth: {
        async login(email, password) {
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            const response = await fetch(`${API.baseUrl}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Login failed');
            }

            API.setToken(data.access_token);
            return data;
        },

        async logout() {
            API.removeToken();
        },

        async getCurrentUser() {
            return API.get('/users/me');
        }
    },

    // ===== CRM ENDPOINTS =====
    opportunities: {
        getAll: (params) => API.get('/opportunities', params),
        get: (id) => API.get(`/opportunities/${id}`),
        create: (data) => API.post('/opportunities', data),
        update: (id, data) => API.put(`/opportunities/${id}`, data),
        markWon: (id) => API.post(`/opportunities/${id}/won`),
        getQuotes: (id) => API.get(`/opportunities/${id}/quotes`),
        createQuote: (id, data) => API.post(`/opportunities/${id}/quotes`, data)
    },

    projects: {
        getAll: (params) => API.get('/projects', params),
        get: (id) => API.get(`/projects/${id}`),
        update: (id, data) => API.put(`/projects/${id}`, data),
        updateStatus: (id, status) => API.put(`/projects/${id}/status`, { status }),
        getSummary: (id) => API.get(`/projects/${id}/summary`)
    },

    // ===== INVENTORY ENDPOINTS =====
    products: {
        getAll: (params) => API.get('/products', params),
        get: (id) => API.get(`/products/${id}`),
        create: (data) => API.post('/products', data),
        update: (id, data) => API.put(`/products/${id}`, data),
        getBom: (id) => API.get(`/products/${id}/bom`),
        updateBom: (id, data) => API.post(`/products/${id}/bom`, data),
        getBarcode: (id) => API.get(`/products/${id}/barcode`),
        checkStock: (id) => API.get(`/products/${id}/stock-check`)
    },

    warehouses: {
        getAll: (params) => API.get('/warehouses', params),
        get: (id) => API.get(`/warehouses/${id}`),
        create: (data) => API.post('/warehouses', data),
        update: (id, data) => API.put(`/warehouses/${id}`, data),
        getStock: (id) => API.get(`/warehouses/${id}/stock`)
    },

    stock: {
        getSummary: () => API.get('/stock'),
        transfer: (data) => API.post('/stock/transfer', data),
        reserve: (data) => API.post('/stock/reserve', data),
        cancelReservation: (id) => API.delete(`/stock/reserve/${id}`),
        getMovements: (params) => API.get('/stock/movements', params),
        checkAvailability: (params) => API.get('/stock/check-availability', params)
    },

    // ===== FINANCE ENDPOINTS =====
    invoices: {
        getAll: (params) => API.get('/invoices', params),
        get: (id) => API.get(`/invoices/${id}`),
        create: (data) => API.post('/invoices', data),
        update: (id, data) => API.put(`/invoices/${id}`, data),
        send: (id) => API.post(`/invoices/${id}/send`),
        getPdf: (id) => API.get(`/invoices/${id}/pdf`)
    },

    expenses: {
        getAll: (params) => API.get('/expenses', params),
        get: (id) => API.get(`/expenses/${id}`),
        create: (data) => API.post('/expenses', data),
        update: (id, data) => API.put(`/expenses/${id}`, data),
        approve: (id) => API.post(`/expenses/${id}/approve`),
        reject: (id) => API.post(`/expenses/${id}/reject`),
        getPersonnelAccount: (userId) => API.get(`/expenses/personnel/${userId}/account`)
    },

    // ===== OPERATIONS ENDPOINTS =====
    serviceForms: {
        getAll: (params) => API.get('/service-forms', params),
        get: (id) => API.get(`/service-forms/${id}`),
        create: (data) => API.post('/service-forms', data),
        update: (id, data) => API.put(`/service-forms/${id}`, data),
        addMaterial: (id, data) => API.post(`/service-forms/${id}/add-material`, data),
        complete: (id) => API.post(`/service-forms/${id}/complete`),
        getDeliveryNote: (id) => API.get(`/service-forms/${id}/delivery-note`)
    },

    // ===== REPORTS ENDPOINTS =====
    reports: {
        projectProfitability: (projectId) => API.get(`/reports/project-profitability/${projectId}`),
        stockStatus: () => API.get('/reports/stock-status'),
        expenseSummary: () => API.get('/reports/expense-summary'),
        revenueSummary: () => API.get('/reports/revenue-summary'),
        currencyRates: () => API.get('/reports/currency-rates')
    }
};

// Export for use
window.API = API;
