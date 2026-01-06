/**
 * Otomasyon CRM - Customers Page Module
 */

import { API } from '../api.js';
import { Utils } from '../utils.js';
import '../components/sidebar.js';
import '../components/header.js';
import '../layout-loader.js';

let customers = [];

/**
 * Müşterileri yükle
 */
async function loadCustomers() {
    const container = document.getElementById('table-container');

    try {
        const search = document.getElementById('search-input').value;
        const statusFilter = document.getElementById('status-filter').value;

        let params = {};
        if (search) params.search = search;
        if (statusFilter) params.is_active = statusFilter;

        customers = await API.get('/customers', params);
        renderTable(customers);
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
 * Tabloyu güvenli şekilde render et
 */
function renderTable(data) {
    const container = document.getElementById('table-container');
    container.innerHTML = '';

    if (data.length === 0) {
        const emptyDiv = Utils.createElement('div', { class: 'empty-state' });
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-icon' }, '👥'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-title' }, 'Henüz müşteri yok'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-message' }, 'Yeni müşteri ekleyerek başlayın'));

        const addBtn = Utils.createElement('button', {
            class: 'btn btn-primary',
            style: 'margin-top: var(--spacing-md);'
        }, 'Yeni Müşteri Ekle');
        addBtn.addEventListener('click', openCreateModal);
        emptyDiv.appendChild(addBtn);

        container.appendChild(emptyDiv);
        return;
    }

    // Tablo oluştur
    const table = Utils.createElement('table', { class: 'data-table' });

    // Thead
    const thead = Utils.createElement('thead');
    const headerRow = Utils.createElement('tr');
    ['Müşteri Adı', 'E-posta', 'Telefon', 'Şehir', 'Durum'].forEach(text => {
        headerRow.appendChild(Utils.createElement('th', {}, text));
    });
    const actionTh = Utils.createElement('th', { style: 'text-align: right;' }, 'İşlemler');
    headerRow.appendChild(actionTh);
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Tbody
    const tbody = Utils.createElement('tbody');

    data.forEach(customer => {
        const tr = Utils.createElement('tr');

        // Müşteri adı + avatar
        const nameTd = Utils.createElement('td');
        const nameWrapper = Utils.createElement('div', {
            style: 'display: flex; align-items: center; gap: var(--spacing-sm);'
        });

        const avatar = Utils.createElement('div', { class: 'avatar avatar-sm' }, customer.name.charAt(0));
        nameWrapper.appendChild(avatar);

        const nameContent = Utils.createElement('div');
        nameContent.appendChild(Utils.createElement('strong', {}, customer.name));
        if (customer.contact_person) {
            nameContent.appendChild(Utils.createElement('div', {
                style: 'font-size: var(--font-size-xs); color: var(--text-muted);'
            }, customer.contact_person));
        }
        nameWrapper.appendChild(nameContent);
        nameTd.appendChild(nameWrapper);
        tr.appendChild(nameTd);

        // Diğer alanlar
        tr.appendChild(Utils.createElement('td', {}, customer.email || '-'));
        tr.appendChild(Utils.createElement('td', {}, customer.phone || '-'));
        tr.appendChild(Utils.createElement('td', {}, customer.city || '-'));

        // Durum badge
        const statusTd = Utils.createElement('td');
        const badge = Utils.createElement('span', {
            class: `status-badge ${customer.is_active ? 'success' : 'danger'}`
        }, customer.is_active ? 'Aktif' : 'Pasif');
        statusTd.appendChild(badge);
        tr.appendChild(statusTd);

        // İşlemler
        const actionTd = Utils.createElement('td', { style: 'text-align: right;' });
        const actionWrapper = Utils.createElement('div', { style: 'display: flex; gap: var(--spacing-xs); justify-content: flex-end;' });

        const editBtn = Utils.createElement('button', { class: 'btn btn-ghost btn-sm' }, 'Düzenle');
        editBtn.addEventListener('click', () => editCustomer(customer.id));
        actionWrapper.appendChild(editBtn);

        const deleteBtn = Utils.createElement('button', { class: 'btn btn-ghost btn-sm', style: 'color: var(--danger);' }, 'Sil');
        deleteBtn.addEventListener('click', () => deleteCustomer(customer.id, customer.name));
        actionWrapper.appendChild(deleteBtn);

        actionTd.appendChild(actionWrapper);
        tr.appendChild(actionTd);

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.appendChild(table);
}

/**
 * Yeni müşteri modal'ı aç
 */
function openCreateModal() {
    document.body.style.overflow = 'hidden';
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = '';

    // Overlay
    const overlay = Utils.createElement('div', { class: 'modal-overlay show' });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
    });

    // Modal content
    const modal = Utils.createElement('div', {
        class: 'modal-content',
        style: 'max-width: 500px;'
    });
    modal.addEventListener('click', (e) => e.stopPropagation());

    // Header
    const header = Utils.createElement('div', { class: 'modal-header' });
    header.appendChild(Utils.createElement('h3', {}, 'Yeni Müşteri'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    // Form
    const form = Utils.createElement('form');
    form.addEventListener('submit', createCustomer);

    const body = Utils.createElement('div', { class: 'modal-body' });

    // Form alanları
    const fields = [
        { name: 'name', label: 'Müşteri Adı', type: 'text', required: true },
        { name: 'email', label: 'E-posta', type: 'email' },
        { name: 'phone', label: 'Telefon', type: 'text' },
        { name: 'contact_person', label: 'Yetkili Kişi', type: 'text' },
        { name: 'city', label: 'Şehir', type: 'text' },
        { name: 'tax_id', label: 'Vergi No', type: 'text' }
    ];

    fields.forEach(field => {
        const group = Utils.createElement('div', { class: 'form-group' });
        const label = Utils.createElement('label', {
            class: field.required ? 'form-label required' : 'form-label'
        }, field.label);
        const input = Utils.createElement('input', {
            type: field.type,
            class: 'form-input',
            name: field.name
        });
        if (field.required) input.setAttribute('required', '');
        group.appendChild(label);
        group.appendChild(input);
        body.appendChild(group);
    });

    form.appendChild(body);

    // Footer
    const footer = Utils.createElement('div', { class: 'modal-footer' });
    const cancelBtn = Utils.createElement('button', {
        type: 'button',
        class: 'btn btn-ghost'
    }, 'İptal');
    cancelBtn.addEventListener('click', closeModal);
    const submitBtn = Utils.createElement('button', {
        type: 'submit',
        class: 'btn btn-primary'
    }, 'Kaydet');
    footer.appendChild(cancelBtn);
    footer.appendChild(submitBtn);
    form.appendChild(footer);

    modal.appendChild(form);
    overlay.appendChild(modal);
    modalContainer.appendChild(overlay);
}

/**
 * Modal'ı kapat
 */
function closeModal() {
    document.getElementById('modal-container').innerHTML = '';
    document.body.style.overflow = '';
}

/**
 * Yeni müşteri oluştur
 */
async function createCustomer(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {};
    formData.forEach((value, key) => {
        if (value) data[key] = value;
    });

    try {
        await API.post('/customers', data);
        closeModal();
        alert('Müşteri başarıyla oluşturuldu');
        loadCustomers();
    } catch (error) {
        alert(error.message || 'Bir hata oluştu');
    }
}

/**
 * Müşteri düzenle modal'ı
 */
function editCustomer(id) {
    const customer = customers.find(c => c.id === id);
    if (!customer) return;

    document.body.style.overflow = 'hidden';
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = '';

    // Overlay
    const overlay = Utils.createElement('div', { class: 'modal-overlay show' });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
    });

    // Modal content
    const modal = Utils.createElement('div', {
        class: 'modal-content',
        style: 'max-width: 500px;'
    });
    modal.addEventListener('click', (e) => e.stopPropagation());

    // Header
    const header = Utils.createElement('div', { class: 'modal-header' });
    header.appendChild(Utils.createElement('h3', {}, 'Müşteri Düzenle'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    // Form
    const form = Utils.createElement('form');
    form.addEventListener('submit', (e) => updateCustomer(e, id));

    const body = Utils.createElement('div', { class: 'modal-body' });

    // Form alanları
    const fields = [
        { name: 'name', label: 'Müşteri Adı', type: 'text', value: customer.name, required: true },
        { name: 'email', label: 'E-posta', type: 'email', value: customer.email || '' },
        { name: 'phone', label: 'Telefon', type: 'text', value: customer.phone || '' },
        { name: 'city', label: 'Şehir', type: 'text', value: customer.city || '' }
    ];

    fields.forEach(field => {
        const group = Utils.createElement('div', { class: 'form-group' });
        const label = Utils.createElement('label', {
            class: field.required ? 'form-label required' : 'form-label'
        }, field.label);
        const input = Utils.createElement('input', {
            type: field.type,
            class: 'form-input',
            name: field.name,
            value: field.value
        });
        if (field.required) input.setAttribute('required', '');
        group.appendChild(label);
        group.appendChild(input);
        body.appendChild(group);
    });

    // Durum select
    const statusGroup = Utils.createElement('div', { class: 'form-group' });
    statusGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Durum'));
    const statusSelect = Utils.createElement('select', { class: 'form-select', name: 'is_active' });

    const activeOption = Utils.createElement('option', { value: 'true' }, 'Aktif');
    if (customer.is_active) activeOption.setAttribute('selected', '');
    const inactiveOption = Utils.createElement('option', { value: 'false' }, 'Pasif');
    if (!customer.is_active) inactiveOption.setAttribute('selected', '');

    statusSelect.appendChild(activeOption);
    statusSelect.appendChild(inactiveOption);
    statusGroup.appendChild(statusSelect);
    body.appendChild(statusGroup);

    form.appendChild(body);

    // Footer
    const footer = Utils.createElement('div', { class: 'modal-footer' });
    const cancelBtn = Utils.createElement('button', {
        type: 'button',
        class: 'btn btn-ghost'
    }, 'İptal');
    cancelBtn.addEventListener('click', closeModal);
    const submitBtn = Utils.createElement('button', {
        type: 'submit',
        class: 'btn btn-primary'
    }, 'Güncelle');
    footer.appendChild(cancelBtn);
    footer.appendChild(submitBtn);
    form.appendChild(footer);

    modal.appendChild(form);
    overlay.appendChild(modal);
    modalContainer.appendChild(overlay);
}

/**
 * Müşteri güncelle
 */
async function updateCustomer(event, id) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {};
    formData.forEach((value, key) => {
        if (key === 'is_active') {
            data[key] = value === 'true';
        } else if (value) {
            data[key] = value;
        }
    });

    try {
        await API.put(`/customers/${id}`, data);
        closeModal();
        alert('Müşteri güncellendi');
        loadCustomers();
    } catch (error) {
        alert(error.message || 'Bir hata oluştu');
    }
}

/**
 * Müşteri sil
 */
async function deleteCustomer(id, name) {
    if (!confirm(`"${name}" müşterisini silmek istediğinize emin misiniz?`)) return;

    try {
        await API.delete(`/customers/${id}`);
        alert('Müşteri silindi');
        loadCustomers();
    } catch (error) {
        alert(error.message || 'Bir hata oluştu');
    }
}

// Global fonksiyonlar (onclick handler'lar için)
window.openCreateModal = openCreateModal;
window.closeModal = closeModal;
window.loadCustomers = loadCustomers;

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function () {
    if (!API.getToken()) {
        window.location.href = 'login.html';
        return;
    }
    loadCustomers();

    // Enter key search
    document.getElementById('search-input').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') loadCustomers();
    });
});
