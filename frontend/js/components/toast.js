/**
 * Otomasyon CRM - Toast Notifications
 * XSS Korumalı, Güvenli DOM Manipülasyonu
 */

import { Utils } from '../utils.js';

const Toast = {
    /**
     * Güvenli toast gösterme
     * @param {string} message - Toast mesajı (textContent olarak eklenir, XSS güvenli)
     * @param {string} type - Toast tipi (info, success, warning, error)
     * @param {number} duration - Gösterim süresi (ms)
     */
    show(message, type = 'info', duration = 3000) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        // Toast element oluştur
        const toast = Utils.createElement('div', { class: `toast toast-${type}` });

        // Message span (XSS güvenli - textContent kullanılıyor)
        const messageSpan = Utils.createElement('span', { class: 'toast-message' }, message);

        // Close button
        const closeBtn = Utils.createElement('button', { class: 'toast-close' }, '×');
        closeBtn.addEventListener('click', () => toast.remove());

        toast.appendChild(messageSpan);
        toast.appendChild(closeBtn);
        container.appendChild(toast);

        // Animasyon için küçük gecikme
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        // Otomatik kaldırma
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    success(message) { this.show(message, 'success'); },
    error(message) { this.show(message, 'error'); },
    warning(message) { this.show(message, 'warning'); },
    info(message) { this.show(message, 'info'); }
};

export { Toast };

// Global erişim için
window.Toast = Toast;
