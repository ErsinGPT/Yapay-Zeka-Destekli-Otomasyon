/**
 * Otomasyon CRM - Configuration Module
 * Ortam bazlı konfigürasyon yönetimi
 */

const Config = {
    /**
     * API Base URL
     * Development ortamında localhost, production'da origin kullanır
     */
    get apiUrl() {
        // Production ortamı tespiti
        const isProduction = window.location.hostname !== 'localhost' &&
            window.location.hostname !== '127.0.0.1';

        if (isProduction) {
            return `${window.location.origin}/api`;
        }

        // Development ortamı
        return 'http://localhost:8000/api';
    },

    /**
     * Ortam bilgisi
     */
    get environment() {
        const isProduction = window.location.hostname !== 'localhost' &&
            window.location.hostname !== '127.0.0.1';
        return isProduction ? 'production' : 'development';
    },

    /**
     * Debug modu
     */
    get isDebug() {
        return this.environment === 'development';
    }
};

export { Config };
