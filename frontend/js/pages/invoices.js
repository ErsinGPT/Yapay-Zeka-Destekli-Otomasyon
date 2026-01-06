/**
 * Otomasyon CRM - Invoices Page Module
 */

import { API } from '../api.js';
import { Utils } from '../utils.js';
import '../components/sidebar.js';
import '../components/header.js';
import '../layout-loader.js';

let invoices = [];
let customers = [];
let projects = [];

/**
 * Başlangıç verileri yükle
 */
async function loadInitialData() {
    try {
        customers = await API.get('/customers');
        projects = await API.projects.getAll();
    } catch (error) {
        console.error('Başlangıç verileri yüklenemedi:', error);
    }
}

/**
 * Faturaları yükle
 */
async function loadInvoices() {
    const container = document.getElementById('table-container');

    try {
        const search = document.getElementById('search-input').value;
        const invoiceType = document.getElementById('type-filter').value;
        const status = document.getElementById('status-filter').value;

        let params = {};
        if (search) params.search = search;
        if (invoiceType) params.invoice_type = invoiceType;
        if (status) params.status = status;

        invoices = await API.invoices.getAll(params);
        renderTable(invoices);
    } catch (error) {
        container.innerHTML = '';
        const errorDiv = Utils.createElement('div', { class: 'empty-state' });
        errorDiv.appendChild(Utils.createElement('div', { class: 'empty-state-icon' }, '⚠️'));
        errorDiv.appendChild(Utils.createElement('div', { class: 'empty-state-title' }, 'Yüklenemedi'));
        errorDiv.appendChild(Utils.createElement('div', { class: 'empty-state-message' }, error.message));
        container.appendChild(errorDiv);
    }
}

/**
 * Tabloyu render et
 */
function renderTable(data) {
    const container = document.getElementById('table-container');
    container.innerHTML = '';

    if (data.length === 0) {
        const emptyDiv = Utils.createElement('div', { class: 'empty-state' });
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-icon' }, '📄'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-title' }, 'Henüz fatura yok'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-message' }, 'Yeni fatura oluşturarak başlayın'));

        const addBtn = Utils.createElement('button', {
            class: 'btn btn-primary',
            style: 'margin-top: var(--spacing-md);'
        }, 'Yeni Fatura');
        addBtn.addEventListener('click', openCreateModal);
        emptyDiv.appendChild(addBtn);

        container.appendChild(emptyDiv);
        return;
    }

    const table = Utils.createElement('table', { class: 'data-table' });

    // Thead
    const thead = Utils.createElement('thead');
    const headerRow = Utils.createElement('tr');
    ['Fatura No', 'Müşteri', 'Tip', 'Tarih', 'Tutar', 'Durum', 'İşlemler'].forEach(text => {
        headerRow.appendChild(Utils.createElement('th', {}, text));
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Tbody
    const tbody = Utils.createElement('tbody');

    data.forEach(invoice => {
        const tr = Utils.createElement('tr');

        // Fatura No
        tr.appendChild(Utils.createElement('td', {}, Utils.createElement('strong', {}, invoice.invoice_number || '-')));

        // Müşteri
        tr.appendChild(Utils.createElement('td', {}, invoice.customer_name || '-'));

        // Tip
        const typeTd = Utils.createElement('td');
        const typeBadge = Utils.createElement('span', {
            class: `status-badge ${invoice.invoice_type === 'EXPORT' ? 'info' : 'default'}`
        }, invoice.invoice_type === 'EXPORT' ? 'İhracat' : 'Yurtiçi');
        typeTd.appendChild(typeBadge);
        tr.appendChild(typeTd);

        // Tarih
        const date = invoice.invoice_date ? new Date(invoice.invoice_date).toLocaleDateString('tr-TR') : '-';
        tr.appendChild(Utils.createElement('td', {}, date));

        // Tutar
        const amount = parseFloat(invoice.total_amount || 0).toLocaleString('tr-TR', { minimumFractionDigits: 2 });
        tr.appendChild(Utils.createElement('td', {}, `${amount} ${invoice.currency || 'TRY'}`));

        // Durum
        const statusTd = Utils.createElement('td');
        const statusMap = {
            'DRAFT': { label: 'Taslak', class: 'default' },
            'SENT': { label: 'Gönderildi', class: 'info' },
            'PAID': { label: 'Ödendi', class: 'success' },
            'CANCELLED': { label: 'İptal', class: 'danger' }
        };
        const statusInfo = statusMap[invoice.status] || { label: invoice.status, class: 'default' };
        const statusBadge = Utils.createElement('span', {
            class: `status-badge ${statusInfo.class}`
        }, statusInfo.label);
        statusTd.appendChild(statusBadge);
        tr.appendChild(statusTd);

        // İşlemler
        const actionTd = Utils.createElement('td');
        const actionWrapper = Utils.createElement('div', { style: 'display: flex; gap: var(--spacing-xs);' });

        const viewBtn = Utils.createElement('button', { class: 'btn btn-ghost btn-sm' }, 'Görüntüle');
        viewBtn.addEventListener('click', () => viewInvoice(invoice.id));
        actionWrapper.appendChild(viewBtn);

        if (invoice.status === 'DRAFT') {
            const sendBtn = Utils.createElement('button', { class: 'btn btn-outline btn-sm' }, 'Gönder');
            sendBtn.addEventListener('click', () => sendInvoice(invoice.id));
            actionWrapper.appendChild(sendBtn);
        }

        if (invoice.status === 'SENT') {
            const paidBtn = Utils.createElement('button', { class: 'btn btn-outline btn-sm' }, 'Ödendi');
            paidBtn.addEventListener('click', () => markPaid(invoice.id));
            actionWrapper.appendChild(paidBtn);
        }

        actionTd.appendChild(actionWrapper);
        tr.appendChild(actionTd);

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.appendChild(table);
}

/**
 * Yeni fatura modal
 */
function openCreateModal() {
    document.body.style.overflow = 'hidden';
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = '';

    const overlay = Utils.createElement('div', { class: 'modal-overlay show' });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
    });

    const modal = Utils.createElement('div', {
        class: 'modal-content',
        style: 'max-width: 600px;'
    });

    // Header
    const header = Utils.createElement('div', { class: 'modal-header' });
    header.appendChild(Utils.createElement('h3', {}, 'Yeni Fatura'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    // Form
    const form = Utils.createElement('form');
    form.addEventListener('submit', createInvoice);

    const body = Utils.createElement('div', { class: 'modal-body' });

    // Müşteri
    const customerGroup = Utils.createElement('div', { class: 'form-group' });
    customerGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Müşteri'));
    const customerSelect = Utils.createElement('select', { class: 'form-select', name: 'customer_id', required: '' });
    customerSelect.appendChild(Utils.createElement('option', { value: '' }, 'Seçiniz'));
    customers.forEach(c => {
        customerSelect.appendChild(Utils.createElement('option', { value: c.id }, c.name));
    });
    customerGroup.appendChild(customerSelect);
    body.appendChild(customerGroup);

    // Proje
    const projectGroup = Utils.createElement('div', { class: 'form-group' });
    projectGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Proje'));
    const projectSelect = Utils.createElement('select', { class: 'form-select', name: 'project_id' });
    projectSelect.appendChild(Utils.createElement('option', { value: '' }, 'Seçiniz (Opsiyonel)'));
    projects.forEach(p => {
        projectSelect.appendChild(Utils.createElement('option', { value: p.id }, `${p.project_code} - ${p.name}`));
    });
    projectGroup.appendChild(projectSelect);
    body.appendChild(projectGroup);

    // Tip ve Para Birimi
    const row1 = Utils.createElement('div', { class: 'form-row' });

    const typeGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    typeGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Fatura Tipi'));
    const typeSelect = Utils.createElement('select', { class: 'form-select', name: 'invoice_type', required: '' });
    typeSelect.appendChild(Utils.createElement('option', { value: 'DOMESTIC' }, 'Yurtiçi'));
    typeSelect.appendChild(Utils.createElement('option', { value: 'EXPORT' }, 'İhracat'));
    typeGroup.appendChild(typeSelect);
    row1.appendChild(typeGroup);

    const currencyGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    currencyGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Para Birimi'));
    const currencySelect = Utils.createElement('select', { class: 'form-select', name: 'currency', required: '' });
    ['TRY', 'USD', 'EUR'].forEach(c => {
        currencySelect.appendChild(Utils.createElement('option', { value: c }, c));
    });
    currencyGroup.appendChild(currencySelect);
    row1.appendChild(currencyGroup);

    body.appendChild(row1);

    // Tarih ve Vade
    const row2 = Utils.createElement('div', { class: 'form-row' });

    const dateGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    dateGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Fatura Tarihi'));
    const dateInput = Utils.createElement('input', { type: 'date', class: 'form-input', name: 'invoice_date', required: '' });
    dateInput.value = new Date().toISOString().split('T')[0];
    dateGroup.appendChild(dateInput);
    row2.appendChild(dateGroup);

    const dueGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    dueGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Vade Tarihi'));
    dueGroup.appendChild(Utils.createElement('input', { type: 'date', class: 'form-input', name: 'due_date' }));
    row2.appendChild(dueGroup);

    body.appendChild(row2);

    // Tutar ve KDV
    const row3 = Utils.createElement('div', { class: 'form-row' });

    const subtotalGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    subtotalGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Ara Toplam'));
    subtotalGroup.appendChild(Utils.createElement('input', { type: 'number', step: '0.01', class: 'form-input', name: 'subtotal', required: '' }));
    row3.appendChild(subtotalGroup);

    const vatGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    vatGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'KDV %'));
    const vatInput = Utils.createElement('input', { type: 'number', step: '0.01', class: 'form-input', name: 'vat_rate', value: '20' });
    vatGroup.appendChild(vatInput);
    row3.appendChild(vatGroup);

    body.appendChild(row3);

    // Notlar
    const notesGroup = Utils.createElement('div', { class: 'form-group' });
    notesGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Notlar'));
    notesGroup.appendChild(Utils.createElement('textarea', { class: 'form-input', name: 'notes', rows: '2' }));
    body.appendChild(notesGroup);

    form.appendChild(body);

    // Footer
    const footer = Utils.createElement('div', { class: 'modal-footer' });
    const cancelBtn = Utils.createElement('button', { type: 'button', class: 'btn btn-ghost' }, 'İptal');
    cancelBtn.addEventListener('click', closeModal);
    footer.appendChild(cancelBtn);
    footer.appendChild(Utils.createElement('button', { type: 'submit', class: 'btn btn-primary' }, 'Kaydet'));
    form.appendChild(footer);

    modal.appendChild(form);
    overlay.appendChild(modal);
    modalContainer.appendChild(overlay);
}

/**
 * Modal kapat
 */
function closeModal() {
    document.getElementById('modal-container').innerHTML = '';
    document.body.style.overflow = '';
}

/**
 * Fatura oluştur
 */
async function createInvoice(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {};
    formData.forEach((value, key) => {
        if (value) {
            if (['customer_id', 'project_id'].includes(key)) {
                data[key] = parseInt(value);
            } else if (['subtotal', 'vat_rate'].includes(key)) {
                data[key] = parseFloat(value);
            } else {
                data[key] = value;
            }
        }
    });

    try {
        await API.invoices.create(data);
        closeModal();
        Utils.toast.success('Fatura oluşturuldu');
        loadInvoices();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

/**
 * Fatura görüntüle
 */
async function viewInvoice(id) {
    try {
        const invoice = await API.invoices.get(id);

        document.body.style.overflow = 'hidden';
        const modalContainer = document.getElementById('modal-container');
        modalContainer.innerHTML = '';

        const overlay = Utils.createElement('div', { class: 'modal-overlay show' });
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closeModal();
        });

        const modal = Utils.createElement('div', {
            class: 'modal-content',
            style: 'max-width: 600px;'
        });

        const header = Utils.createElement('div', { class: 'modal-header' });
        header.appendChild(Utils.createElement('h3', {}, `Fatura: ${invoice.invoice_number}`));
        const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
        closeBtn.addEventListener('click', closeModal);
        header.appendChild(closeBtn);
        modal.appendChild(header);

        const body = Utils.createElement('div', { class: 'modal-body' });

        const details = [
            ['Müşteri', invoice.customer_name],
            ['Tip', invoice.invoice_type === 'EXPORT' ? 'İhracat' : 'Yurtiçi'],
            ['Tarih', new Date(invoice.invoice_date).toLocaleDateString('tr-TR')],
            ['Ara Toplam', `${parseFloat(invoice.subtotal).toLocaleString('tr-TR')} ${invoice.currency}`],
            ['KDV', `%${invoice.vat_rate} (${parseFloat(invoice.vat_amount).toLocaleString('tr-TR')} ${invoice.currency})`],
            ['Toplam', `${parseFloat(invoice.total_amount).toLocaleString('tr-TR')} ${invoice.currency}`],
            ['Durum', invoice.status]
        ];

        details.forEach(([label, value]) => {
            const row = Utils.createElement('div', { style: 'display: flex; padding: var(--spacing-xs) 0; border-bottom: 1px solid var(--border-color);' });
            row.appendChild(Utils.createElement('strong', { style: 'flex: 1;' }, label));
            row.appendChild(Utils.createElement('span', { style: 'flex: 2;' }, value || '-'));
            body.appendChild(row);
        });

        modal.appendChild(body);

        const footer = Utils.createElement('div', { class: 'modal-footer' });
        const closeFooterBtn = Utils.createElement('button', { type: 'button', class: 'btn btn-ghost' }, 'Kapat');
        closeFooterBtn.addEventListener('click', closeModal);
        footer.appendChild(closeFooterBtn);
        modal.appendChild(footer);

        overlay.appendChild(modal);
        modalContainer.appendChild(overlay);
    } catch (error) {
        Utils.toast.error('Fatura yüklenemedi: ' + error.message);
    }
}

/**
 * Faturayı gönder
 */
async function sendInvoice(id) {
    if (!confirm('Fatura gönderilsin mi?')) return;
    try {
        await API.invoices.send(id);
        Utils.toast.success('Fatura gönderildi');
        loadInvoices();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

/**
 * Ödendi işaretle
 */
async function markPaid(id) {
    if (!confirm('Fatura ödendi olarak işaretlensin mi?')) return;
    try {
        await API.post(`/invoices/${id}/mark-paid`);
        Utils.toast.success('Fatura ödendi olarak işaretlendi');
        loadInvoices();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

// Global fonksiyonlar
window.openCreateModal = openCreateModal;
window.closeModal = closeModal;
window.loadInvoices = loadInvoices;

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', async function () {
    if (!API.getToken()) {
        window.location.href = 'login.html';
        return;
    }
    await loadInitialData();
    loadInvoices();

    document.getElementById('search-input').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') loadInvoices();
    });
});
