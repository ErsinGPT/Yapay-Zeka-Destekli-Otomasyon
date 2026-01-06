/**
 * Otomasyon CRM - Service Forms Page Module
 */

import { API } from '../api.js';
import { Utils } from '../utils.js';
import '../components/sidebar.js';
import '../components/header.js';
import '../layout-loader.js';

let serviceForms = [];
let projects = [];
let users = [];

/**
 * Başlangıç verileri yükle
 */
async function loadInitialData() {
    try {
        projects = await API.projects.getAll();
        users = await API.get('/users');
    } catch (error) {
        console.error('Başlangıç verileri yüklenemedi:', error);
    }
}

/**
 * Servis formlarını yükle
 */
async function loadServiceForms() {
    const container = document.getElementById('table-container');

    try {
        const search = document.getElementById('search-input').value;
        const status = document.getElementById('status-filter').value;

        let params = {};
        if (search) params.search = search;
        if (status) params.status = status;

        serviceForms = await API.serviceForms.getAll(params);
        renderTable(serviceForms);
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
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-icon' }, '🔧'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-title' }, 'Henüz servis formu yok'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-message' }, 'Yeni servis formu oluşturarak başlayın'));

        const addBtn = Utils.createElement('button', {
            class: 'btn btn-primary',
            style: 'margin-top: var(--spacing-md);'
        }, 'Yeni Servis Formu');
        addBtn.addEventListener('click', openCreateModal);
        emptyDiv.appendChild(addBtn);

        container.appendChild(emptyDiv);
        return;
    }

    const table = Utils.createElement('table', { class: 'data-table' });

    // Thead
    const thead = Utils.createElement('thead');
    const headerRow = Utils.createElement('tr');
    ['Form No', 'Proje', 'Teknisyen', 'Tarih', 'Çalışma Saati', 'Durum', 'İşlemler'].forEach(text => {
        headerRow.appendChild(Utils.createElement('th', {}, text));
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Tbody
    const tbody = Utils.createElement('tbody');

    data.forEach(form => {
        const tr = Utils.createElement('tr');

        // Form No
        tr.appendChild(Utils.createElement('td', {}, Utils.createElement('strong', {}, form.form_number || '-')));

        // Proje
        tr.appendChild(Utils.createElement('td', {}, form.project_code || '-'));

        // Teknisyen
        tr.appendChild(Utils.createElement('td', {}, form.technician_name || '-'));

        // Tarih
        const date = form.service_date ? new Date(form.service_date).toLocaleDateString('tr-TR') : '-';
        tr.appendChild(Utils.createElement('td', {}, date));

        // Çalışma Saati
        tr.appendChild(Utils.createElement('td', {}, form.work_hours ? `${form.work_hours} saat` : '-'));

        // Durum
        const statusTd = Utils.createElement('td');
        const statusMap = {
            'DRAFT': { label: 'Taslak', class: 'default' },
            'IN_PROGRESS': { label: 'Devam Ediyor', class: 'warning' },
            'COMPLETED': { label: 'Tamamlandı', class: 'success' }
        };
        const statusInfo = statusMap[form.status] || { label: form.status, class: 'default' };
        const statusBadge = Utils.createElement('span', {
            class: `status-badge ${statusInfo.class}`
        }, statusInfo.label);
        statusTd.appendChild(statusBadge);
        tr.appendChild(statusTd);

        // İşlemler
        const actionTd = Utils.createElement('td');
        const actionWrapper = Utils.createElement('div', { style: 'display: flex; gap: var(--spacing-xs);' });

        const viewBtn = Utils.createElement('button', { class: 'btn btn-ghost btn-sm' }, 'Detay');
        viewBtn.addEventListener('click', () => viewServiceForm(form.id));
        actionWrapper.appendChild(viewBtn);

        if (form.status !== 'COMPLETED') {
            const completeBtn = Utils.createElement('button', { class: 'btn btn-outline btn-sm' }, 'Tamamla');
            completeBtn.addEventListener('click', () => completeForm(form.id));
            actionWrapper.appendChild(completeBtn);
        }

        actionTd.appendChild(actionWrapper);
        tr.appendChild(actionTd);

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.appendChild(table);
}

/**
 * Yeni servis formu modal
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
    header.appendChild(Utils.createElement('h3', {}, 'Yeni Servis Formu'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    // Form
    const form = Utils.createElement('form');
    form.addEventListener('submit', createServiceForm);

    const body = Utils.createElement('div', { class: 'modal-body' });

    // Proje
    const projectGroup = Utils.createElement('div', { class: 'form-group' });
    projectGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Proje'));
    const projectSelect = Utils.createElement('select', { class: 'form-select', name: 'project_id', required: '' });
    projectSelect.appendChild(Utils.createElement('option', { value: '' }, 'Seçiniz'));
    projects.forEach(p => {
        projectSelect.appendChild(Utils.createElement('option', { value: p.id }, `${p.project_code} - ${p.name}`));
    });
    projectGroup.appendChild(projectSelect);
    body.appendChild(projectGroup);

    // Teknisyen
    const techGroup = Utils.createElement('div', { class: 'form-group' });
    techGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Teknisyen'));
    const techSelect = Utils.createElement('select', { class: 'form-select', name: 'technician_id', required: '' });
    techSelect.appendChild(Utils.createElement('option', { value: '' }, 'Seçiniz'));
    users.forEach(u => {
        techSelect.appendChild(Utils.createElement('option', { value: u.id }, u.full_name || u.email));
    });
    techGroup.appendChild(techSelect);
    body.appendChild(techGroup);

    // Tarih ve Saat
    const row1 = Utils.createElement('div', { class: 'form-row' });

    const dateGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    dateGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Servis Tarihi'));
    const dateInput = Utils.createElement('input', { type: 'date', class: 'form-input', name: 'service_date', required: '' });
    dateInput.value = new Date().toISOString().split('T')[0];
    dateGroup.appendChild(dateInput);
    row1.appendChild(dateGroup);

    const hoursGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    hoursGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Çalışma Saati'));
    hoursGroup.appendChild(Utils.createElement('input', { type: 'number', step: '0.5', class: 'form-input', name: 'work_hours', value: '0' }));
    row1.appendChild(hoursGroup);

    body.appendChild(row1);

    // Yapılan İşler
    const workGroup = Utils.createElement('div', { class: 'form-group' });
    workGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Yapılan İşler'));
    workGroup.appendChild(Utils.createElement('textarea', { class: 'form-input', name: 'work_description', rows: '3' }));
    body.appendChild(workGroup);

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
 * Servis formu oluştur
 */
async function createServiceForm(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {};
    formData.forEach((value, key) => {
        if (value) {
            if (['project_id', 'technician_id'].includes(key)) {
                data[key] = parseInt(value);
            } else if (key === 'work_hours') {
                data[key] = parseFloat(value);
            } else {
                data[key] = value;
            }
        }
    });

    try {
        await API.serviceForms.create(data);
        closeModal();
        alert('Servis formu oluşturuldu');
        loadServiceForms();
    } catch (error) {
        alert(error.message || 'Bir hata oluştu');
    }
}

/**
 * Servis formu görüntüle
 */
async function viewServiceForm(id) {
    try {
        const form = await API.serviceForms.get(id);

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
        header.appendChild(Utils.createElement('h3', {}, `Servis Formu: ${form.form_number}`));
        const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
        closeBtn.addEventListener('click', closeModal);
        header.appendChild(closeBtn);
        modal.appendChild(header);

        const body = Utils.createElement('div', { class: 'modal-body' });

        const details = [
            ['Proje', form.project_code],
            ['Teknisyen', form.technician_name],
            ['Tarih', new Date(form.service_date).toLocaleDateString('tr-TR')],
            ['Çalışma Saati', form.work_hours ? `${form.work_hours} saat` : '-'],
            ['Yapılan İşler', form.work_description || '-'],
            ['Notlar', form.notes || '-'],
            ['Durum', form.status]
        ];

        details.forEach(([label, value]) => {
            const row = Utils.createElement('div', { style: 'display: flex; padding: var(--spacing-xs) 0; border-bottom: 1px solid var(--border-color);' });
            row.appendChild(Utils.createElement('strong', { style: 'flex: 1;' }, label));
            row.appendChild(Utils.createElement('span', { style: 'flex: 2;' }, value || '-'));
            body.appendChild(row);
        });

        // Malzemeler
        if (form.materials && form.materials.length > 0) {
            body.appendChild(Utils.createElement('h4', { style: 'margin-top: var(--spacing-md);' }, 'Kullanılan Malzemeler'));
            const materialList = Utils.createElement('ul', { style: 'margin: var(--spacing-sm) 0;' });
            form.materials.forEach(m => {
                materialList.appendChild(Utils.createElement('li', {}, `${m.product_name} - ${m.quantity} ${m.unit || 'adet'}`));
            });
            body.appendChild(materialList);
        }

        modal.appendChild(body);

        const footer = Utils.createElement('div', { class: 'modal-footer' });
        const closeFooterBtn = Utils.createElement('button', { type: 'button', class: 'btn btn-ghost' }, 'Kapat');
        closeFooterBtn.addEventListener('click', closeModal);
        footer.appendChild(closeFooterBtn);
        modal.appendChild(footer);

        overlay.appendChild(modal);
        modalContainer.appendChild(overlay);
    } catch (error) {
        alert('Form yüklenemedi: ' + error.message);
    }
}

/**
 * Formu tamamla
 */
async function completeForm(id) {
    if (!confirm('Servis formu tamamlansın mı?')) return;
    try {
        await API.serviceForms.complete(id);
        alert('Form tamamlandı');
        loadServiceForms();
    } catch (error) {
        alert(error.message || 'Bir hata oluştu');
    }
}

// Global fonksiyonlar
window.openCreateModal = openCreateModal;
window.closeModal = closeModal;
window.loadServiceForms = loadServiceForms;

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', async function () {
    if (!API.getToken()) {
        window.location.href = 'login.html';
        return;
    }
    await loadInitialData();
    loadServiceForms();

    document.getElementById('search-input').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') loadServiceForms();
    });
});
