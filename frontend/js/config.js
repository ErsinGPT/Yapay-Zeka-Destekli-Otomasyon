/**
 * Otomasyon CRM - Configuration Module
 * Ortam bazlı konfigürasyon yönetimi
 */

const Config = {
    // Backend portu (development için)
    backendPort: 8000,

    // Production backend URL (deployment için bu değeri güncelleyin)
    productionApiUrl: null, // Örn: 'https://api.yoursite.com/api'

    /**
     * API Base URL
     * Development ortamında aynı host'ta farklı port kullanır
     * Production'da ya aynı origin ya da tanımlı URL kullanır
     */
    get apiUrl() {
        const hostname = window.location.hostname;

        // Eğer production URL tanımlıysa onu kullan
        if (this.productionApiUrl) {
            return this.productionApiUrl;
        }

        // Development: aynı host'ta backend portuna bağlan
        // Bu hem localhost hem de lokal ağ IP'leri için çalışır
        return `http://${hostname}:${this.backendPort}/api`;
    },

    /**
     * Ortam bilgisi
     */
    get environment() {
        // Production URL tanımlıysa production'dayız
        if (this.productionApiUrl) {
            return 'production';
        }
        return 'development';
    },

    /**
     * Debug modu
     */
    get isDebug() {
        return this.environment === 'development';
    }
};

export { Config };

