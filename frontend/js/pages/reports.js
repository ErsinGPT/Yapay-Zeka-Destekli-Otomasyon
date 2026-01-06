/**
 * Otomasyon CRM - Reports Page Module
 */

import { API } from '../api.js';
import { Utils } from '../utils.js';
import '../components/sidebar.js';
import '../components/header.js';
import '../layout-loader.js';

/**
 * Dashboard istatistiklerini yükle
 */
async function loadDashboardStats() {
    const container = document.getElementById('summary-stats');

    try {
        const dashboard = await API.get('/reports/dashboard');
        container.innerHTML = '';

        const stats = [
            { label: 'Toplam Proje', value: dashboard.total_projects || 0, icon: '📁' },
            { label: 'Aktif Proje', value: dashboard.active_projects || 0, icon: '🚀' },
            { label: 'Toplam Fırsat', value: dashboard.total_opportunities || 0, icon: '⭐' },
            { label: 'Toplam Müşteri', value: dashboard.total_customers || 0, icon: '👥' },
            { label: 'Bekleyen Fatura', value: dashboard.pending_invoices || 0, icon: '📄' },
            { label: 'Bekleyen Masraf', value: dashboard.pending_expenses || 0, icon: '💳' }
        ];

        stats.forEach(stat => {
            const card = Utils.createElement('div', { class: 'stat-card' });
            const iconDiv = Utils.createElement('div', { class: 'stat-icon' }, stat.icon);
            const contentDiv = Utils.createElement('div', { class: 'stat-content' });
            contentDiv.appendChild(Utils.createElement('div', { class: 'stat-value' }, stat.value.toString()));
            contentDiv.appendChild(Utils.createElement('div', { class: 'stat-label' }, stat.label));
            card.appendChild(iconDiv);
            card.appendChild(contentDiv);
            container.appendChild(card);
        });
    } catch (error) {
        container.innerHTML = '<p style="color: var(--text-muted);">Dashboard verileri yüklenemedi</p>';
    }
}

/**
 * Stok raporu yükle
 */
async function loadStockReport() {
    const container = document.getElementById('stock-report');

    try {
        const report = await API.reports.stockStatus();
        container.innerHTML = '';

        if (!report || report.length === 0) {
            container.appendChild(Utils.createElement('p', { style: 'color: var(--text-muted);' }, 'Stok verisi bulunamadı'));
            return;
        }

        const list = Utils.createElement('div');

        // Summary
        const totalProducts = report.length;
        const lowStock = report.filter(r => (r.available_quantity || 0) < 10).length;

        const summaryDiv = Utils.createElement('div', { style: 'margin-bottom: var(--spacing-md);' });
        summaryDiv.appendChild(Utils.createElement('p', {}, `Toplam ${totalProducts} ürün, ${lowStock} düşük stokta`));
        list.appendChild(summaryDiv);

        // Low stock items
        if (lowStock > 0) {
            list.appendChild(Utils.createElement('h4', { style: 'margin: var(--spacing-sm) 0; color: var(--error);' }, 'Düşük Stoklu Ürünler'));
            const lowStockItems = report.filter(r => (r.available_quantity || 0) < 10).slice(0, 5);
            lowStockItems.forEach(item => {
                const itemDiv = Utils.createElement('div', {
                    style: 'display: flex; justify-content: space-between; padding: var(--spacing-xs) 0; border-bottom: 1px solid var(--border-color);'
                });
                itemDiv.appendChild(Utils.createElement('span', {}, item.product_name || item.sku || '-'));
                itemDiv.appendChild(Utils.createElement('span', {
                    style: 'color: var(--error); font-weight: 600;'
                }, (item.available_quantity || 0).toString()));
                list.appendChild(itemDiv);
            });
        }

        container.appendChild(list);
    } catch (error) {
        container.innerHTML = '<p style="color: var(--error);">Stok raporu yüklenemedi</p>';
    }
}

/**
 * Masraf raporu yükle
 */
async function loadExpenseReport() {
    const container = document.getElementById('expense-report');

    try {
        const report = await API.reports.expenseSummary();
        container.innerHTML = '';

        const list = Utils.createElement('div');

        const items = [
            ['Toplam Masraf', formatCurrency(report.total_amount || 0)],
            ['Onaylanan', formatCurrency(report.approved_amount || 0)],
            ['Bekleyen', formatCurrency(report.pending_amount || 0)],
            ['Bu Ay', formatCurrency(report.this_month || 0)]
        ];

        items.forEach(([label, value]) => {
            const itemDiv = Utils.createElement('div', {
                style: 'display: flex; justify-content: space-between; padding: var(--spacing-xs) 0; border-bottom: 1px solid var(--border-color);'
            });
            itemDiv.appendChild(Utils.createElement('span', {}, label));
            itemDiv.appendChild(Utils.createElement('span', { style: 'font-weight: 600;' }, value));
            list.appendChild(itemDiv);
        });

        container.appendChild(list);
    } catch (error) {
        container.innerHTML = '<p style="color: var(--error);">Masraf raporu yüklenemedi</p>';
    }
}

/**
 * Gelir raporu yükle
 */
async function loadRevenueReport() {
    const container = document.getElementById('revenue-report');

    try {
        const report = await API.reports.revenueSummary();
        container.innerHTML = '';

        const list = Utils.createElement('div');

        const items = [
            ['Toplam Gelir', formatCurrency(report.total_revenue || 0)],
            ['Ödenen', formatCurrency(report.paid_amount || 0)],
            ['Bekleyen', formatCurrency(report.pending_amount || 0)],
            ['Bu Ay', formatCurrency(report.this_month || 0)]
        ];

        items.forEach(([label, value]) => {
            const itemDiv = Utils.createElement('div', {
                style: 'display: flex; justify-content: space-between; padding: var(--spacing-xs) 0; border-bottom: 1px solid var(--border-color);'
            });
            itemDiv.appendChild(Utils.createElement('span', {}, label));
            itemDiv.appendChild(Utils.createElement('span', { style: 'font-weight: 600;' }, value));
            list.appendChild(itemDiv);
        });

        container.appendChild(list);
    } catch (error) {
        container.innerHTML = '<p style="color: var(--error);">Gelir raporu yüklenemedi</p>';
    }
}

/**
 * Döviz kurları yükle
 */
async function loadCurrencyRates() {
    const container = document.getElementById('currency-report');

    try {
        const rates = await API.reports.currencyRates();
        container.innerHTML = '';

        const list = Utils.createElement('div');

        const currencies = [
            { code: 'USD', symbol: '$' },
            { code: 'EUR', symbol: '€' },
            { code: 'GBP', symbol: '£' }
        ];

        currencies.forEach(currency => {
            const rate = rates[currency.code] || rates[currency.code.toLowerCase()];
            if (rate) {
                const itemDiv = Utils.createElement('div', {
                    style: 'display: flex; justify-content: space-between; align-items: center; padding: var(--spacing-sm) 0; border-bottom: 1px solid var(--border-color);'
                });

                const leftDiv = Utils.createElement('div');
                leftDiv.appendChild(Utils.createElement('span', { style: 'font-size: 1.5rem; margin-right: var(--spacing-sm);' }, currency.symbol));
                leftDiv.appendChild(Utils.createElement('span', {}, currency.code));
                itemDiv.appendChild(leftDiv);

                itemDiv.appendChild(Utils.createElement('span', {
                    style: 'font-weight: 600; font-size: 1.1rem;'
                }, `${parseFloat(rate).toFixed(4)} ₺`));

                list.appendChild(itemDiv);
            }
        });

        if (list.children.length === 0) {
            list.appendChild(Utils.createElement('p', { style: 'color: var(--text-muted);' }, 'Kur bilgisi bulunamadı'));
        }

        // Last update
        if (rates.last_update) {
            list.appendChild(Utils.createElement('p', {
                style: 'color: var(--text-muted); font-size: var(--font-size-xs); margin-top: var(--spacing-sm);'
            }, `Son güncelleme: ${new Date(rates.last_update).toLocaleString('tr-TR')}`));
        }

        container.appendChild(list);
    } catch (error) {
        container.innerHTML = '<p style="color: var(--error);">Döviz kurları yüklenemedi</p>';
    }
}

/**
 * Para formatla
 */
function formatCurrency(value, currency = 'TRY') {
    return parseFloat(value).toLocaleString('tr-TR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }) + ' ' + (currency === 'TRY' ? '₺' : currency);
}

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', async function () {
    if (!API.getToken()) {
        window.location.href = 'login.html';
        return;
    }

    // Paralel yükleme
    loadDashboardStats();
    loadStockReport();
    loadExpenseReport();
    loadRevenueReport();
    loadCurrencyRates();
});
