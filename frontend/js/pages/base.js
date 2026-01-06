/**
 * Otomasyon CRM - Base Page Module
 * Ortak sayfa işlevlerini içerir
 */

import { API } from '../api.js';
import { Utils } from '../utils.js';
import '../layout-loader.js';

/**
 * Sayfa için temel fonksiyonlar
 */
export function initPage() {
    // Auth check
    if (!API.getToken()) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

/**
 * Modal kapat
 */
export function closeModal(event) {
    if (event && event.target !== event.currentTarget) return;
    document.getElementById('modal-container').innerHTML = '';
    document.body.style.overflow = '';
}

// Global erişim için
window.closeModal = closeModal;

// Reexport for convenience
export { API, Utils };
