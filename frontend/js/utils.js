/**
 * Otomasyon CRM - Utility Functions
 */

const Utils = {
    /**
     * XSS Korumalı HTML Sanitization
     * Sadece güvenli etiketlere ve attribute'lara izin verir
     */
    sanitizeHTML(str) {
        if (!str) return '';

        // Temel XSS karakterlerini escape et
        const escapeMap = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;'
        };

        return String(str).replace(/[&<>"'/]/g, char => escapeMap[char]);
    },

    /**
     * Güvenli text content oluşturma
     */
    createTextNode(text) {
        return document.createTextNode(text || '');
    },

    /**
     * Güvenli element oluşturma
     */
    createElement(tag, attributes = {}, textContent = '') {
        const element = document.createElement(tag);

        // Güvenli attribute'ları ekle
        const safeAttributes = ['class', 'id', 'style', 'type', 'name', 'value', 'placeholder',
            'disabled', 'readonly', 'required', 'href', 'src', 'alt', 'title',
            'colspan', 'rowspan', 'data-id', 'data-status', 'data-value'];

        Object.keys(attributes).forEach(key => {
            if (safeAttributes.includes(key) || key.startsWith('data-')) {
                // href ve src için XSS koruması
                if (key === 'href' || key === 'src') {
                    const value = attributes[key];
                    // javascript: protokolünü engelle
                    if (value && !value.toLowerCase().startsWith('javascript:')) {
                        element.setAttribute(key, value);
                    }
                } else {
                    element.setAttribute(key, attributes[key]);
                }
            }
        });

        if (textContent) {
            element.textContent = textContent;
        }

        return element;
    },

    /**
     * Format number as currency
     */
    formatCurrency(amount, currency = 'TRY') {
        if (amount === null || amount === undefined || isNaN(amount)) {
            amount = 0;
        }
        const formatter = new Intl.NumberFormat('tr-TR', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2
        });
        return formatter.format(amount);
    },

    /**
     * Format date
     */
    formatDate(date, format = 'short') {
        const d = new Date(date);
        if (format === 'short') {
            return d.toLocaleDateString('tr-TR');
        } else if (format === 'long') {
            return d.toLocaleDateString('tr-TR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } else if (format === 'datetime') {
            return d.toLocaleString('tr-TR');
        }
        return d.toLocaleDateString('tr-TR');
    },

    /**
     * Format number with thousand separators
     */
    formatNumber(num) {
        return new Intl.NumberFormat('tr-TR').format(num);
    },

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Generate unique ID
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },

    /**
     * Get initials from name
     */
    getInitials(name) {
        if (!name) return '';
        return name
            .split(' ')
            .map(word => word[0])
            .join('')
            .toUpperCase()
            .slice(0, 2);
    },

    /**
     * Capitalize first letter
     */
    capitalize(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    },

    /**
     * Truncate text
     */
    truncate(str, length = 50) {
        if (!str || str.length <= length) return str;
        return str.slice(0, length) + '...';
    },

    /**
     * Parse query string
     */
    parseQueryString(queryString) {
        const params = new URLSearchParams(queryString);
        const result = {};
        for (const [key, value] of params) {
            result[key] = value;
        }
        return result;
    },

    /**
     * Build query string
     */
    buildQueryString(params) {
        return new URLSearchParams(params).toString();
    },

    /**
     * Deep clone object
     */
    deepClone(obj) {
        return JSON.parse(JSON.stringify(obj));
    },

    /**
     * Check if object is empty
     */
    isEmpty(obj) {
        if (obj === null || obj === undefined) return true;
        if (Array.isArray(obj)) return obj.length === 0;
        if (typeof obj === 'object') return Object.keys(obj).length === 0;
        return false;
    },

    /**
     * Sleep/delay function
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    /**
     * Get status badge class
     */
    getStatusClass(status) {
        const statusMap = {
            // Project statuses
            'OPPORTUNITY': 'info',
            'WON': 'success',
            'ENGINEERING': 'info',
            'PROCUREMENT': 'warning',
            'ASSEMBLY': 'warning',
            'TESTING': 'info',
            'SHIPPING': 'warning',
            'COMMISSIONING': 'info',
            'COMPLETED': 'success',
            'INVOICED': 'success',
            // General statuses
            'ACTIVE': 'success',
            'INACTIVE': 'gray',
            'PENDING': 'warning',
            'APPROVED': 'success',
            'REJECTED': 'danger',
            'OPEN': 'info',
            'IN_PROGRESS': 'warning',
            'CLOSED': 'gray'
        };
        return statusMap[status] || 'gray';
    },

    /**
     * Translate status to Turkish
     */
    translateStatus(status) {
        const translations = {
            'OPPORTUNITY': 'Fırsat',
            'WON': 'Kazanıldı',
            'ENGINEERING': 'Mühendislik',
            'PROCUREMENT': 'Tedarik',
            'ASSEMBLY': 'Montaj',
            'TESTING': 'Test',
            'SHIPPING': 'Sevkiyat',
            'COMMISSIONING': 'Devreye Alma',
            'COMPLETED': 'Tamamlandı',
            'INVOICED': 'Faturalandı',
            'ACTIVE': 'Aktif',
            'INACTIVE': 'Pasif',
            'PENDING': 'Beklemede',
            'APPROVED': 'Onaylandı',
            'REJECTED': 'Reddedildi',
            'PHYSICAL': 'Fiziksel',
            'VIRTUAL': 'Sanal/Araç',
            'DOMESTIC': 'Yurtiçi',
            'EXPORT': 'İhracat'
        };
        return translations[status] || status;
    }
};

export { Utils };
