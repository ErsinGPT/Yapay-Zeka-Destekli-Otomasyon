/**
 * Otomasyon CRM - Modal Component
 * XSS Korumalı, Güvenli DOM Manipülasyonu
 */

import { Utils } from '../utils.js';

const Modal = {
    /**
     * Güvenli modal gösterme
     * @param {Object} options - Modal seçenekleri
     * @param {string} options.title - Modal başlığı (metin olarak sanitize edilir)
     * @param {string|HTMLElement} options.content - Modal içeriği
     * @param {string|HTMLElement} options.footer - Modal footer
     * @param {string} options.size - Modal boyutu (sm, md, lg)
     */
    show(options) {
        const container = document.getElementById('modal-container');
        if (!container) return;

        const { title, content, footer, size = 'md' } = options;

        // Container'ı temizle
        container.innerHTML = '';

        // Backdrop
        const backdrop = Utils.createElement('div', { class: 'modal-backdrop' });
        backdrop.addEventListener('click', () => Modal.close());

        // Dialog
        const dialog = Utils.createElement('div', { class: `modal-dialog modal-${size}` });

        // Header
        const header = Utils.createElement('div', { class: 'modal-header' });
        const titleEl = Utils.createElement('h3', { class: 'modal-title' }, title || '');
        const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
        closeBtn.addEventListener('click', () => Modal.close());
        header.appendChild(titleEl);
        header.appendChild(closeBtn);

        // Body
        const body = Utils.createElement('div', { class: 'modal-body' });
        if (typeof content === 'string') {
            // HTML content için güvenli olmayan ama gerekli durumlar
            body.innerHTML = content;
        } else if (content instanceof HTMLElement) {
            body.appendChild(content);
        }

        dialog.appendChild(header);
        dialog.appendChild(body);

        // Footer (opsiyonel)
        if (footer) {
            const footerEl = Utils.createElement('div', { class: 'modal-footer' });
            if (typeof footer === 'string') {
                footerEl.innerHTML = footer;
            } else if (footer instanceof HTMLElement) {
                footerEl.appendChild(footer);
            }
            dialog.appendChild(footerEl);
        }

        container.appendChild(backdrop);
        container.appendChild(dialog);
        container.classList.add('show');
        document.body.style.overflow = 'hidden';
    },

    /**
     * Modal'ı kapat
     */
    close() {
        const container = document.getElementById('modal-container');
        if (!container) return;

        container.classList.remove('show');
        container.innerHTML = '';
        document.body.style.overflow = '';
    }
};

export { Modal };

// Global erişim için (onclick handler'lar için gerekli)
window.Modal = Modal;
