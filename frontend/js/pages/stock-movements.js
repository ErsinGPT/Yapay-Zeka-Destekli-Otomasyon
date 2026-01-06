/**
 * Otomasyon CRM - Stock Movements Page Module
 */

import { API } from '../api.js';
import { Utils } from '../utils.js';
import '../components/sidebar.js';
import '../components/header.js';
import '../layout-loader.js';

let movements = [];
let warehouses = [];
let products = [];
let projects = [];

/**
 * Başlangıç verileri yükle
 */
async function loadInitialData() {
    try {
        warehouses = await API.warehouses.getAll();
        const warehouseSelect = document.getElementById('warehouse-filter');
        warehouses.forEach(w => {
            warehouseSelect.appendChild(Utils.createElement('option', { value: w.id }, w.name));
        });

        products = await API.products.getAll();
        projects = await API.projects.getAll();
    } catch (error) {
        console.error('Başlangıç verileri yüklenemedi:', error);
    }
}

/**
 * Özet kartları yükle
 */
async function loadSummary() {
    const container = document.getElementById('summary-cards');
    try {
        const summary = await API.stock.getSummary();
        container.innerHTML = '';

        const stats = [
            { label: 'Toplam Ürün', value: summary.total_products || 0, icon: '📦' },
            { label: 'Toplam Stok', value: summary.total_stock || 0, icon: '📊' },
            { label: 'Rezerve', value: summary.reserved_stock || 0, icon: '🔒' }
        ];

        stats.forEach(stat => {
            const card = Utils.createElement('div', { class: 'stat-card' });
            const iconDiv = Utils.createElement('div', { class: 'stat-icon' }, stat.icon);
            const contentDiv = Utils.createElement('div', { class: 'stat-content' });
            contentDiv.appendChild(Utils.createElement('div', {
                class: 'stat-value',
                style: stat.danger && stat.value > 0 ? 'color: var(--error);' : ''
            }, stat.value.toString()));
            contentDiv.appendChild(Utils.createElement('div', { class: 'stat-label' }, stat.label));
            card.appendChild(iconDiv);
            card.appendChild(contentDiv);
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Özet yüklenemedi:', error);
    }
}

/**
 * Hareketleri yükle
 */
async function loadMovements() {
    const container = document.getElementById('table-container');

    try {
        const movementType = document.getElementById('movement-type-filter').value;
        const warehouseId = document.getElementById('warehouse-filter').value;
        const dateFrom = document.getElementById('date-from').value;
        const dateTo = document.getElementById('date-to').value;

        let params = {};
        if (movementType) params.movement_type = movementType;
        if (warehouseId) params.warehouse_id = warehouseId;
        if (dateFrom) params.date_from = dateFrom;
        if (dateTo) params.date_to = dateTo;

        movements = await API.stock.getMovements(params);
        renderTable(movements);
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
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-icon' }, '📋'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-title' }, 'Henüz hareket yok'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-message' }, 'Stok hareketi ekleyerek başlayın'));
        container.appendChild(emptyDiv);
        return;
    }

    const table = Utils.createElement('table', { class: 'data-table' });

    // Thead
    const thead = Utils.createElement('thead');
    const headerRow = Utils.createElement('tr');
    ['Tarih', 'Tip', 'Ürün', 'Depo', 'Miktar', 'Açıklama'].forEach(text => {
        headerRow.appendChild(Utils.createElement('th', {}, text));
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Tbody
    const tbody = Utils.createElement('tbody');

    data.forEach(movement => {
        const tr = Utils.createElement('tr');

        // Tarih
        const date = new Date(movement.created_at);
        tr.appendChild(Utils.createElement('td', {}, date.toLocaleDateString('tr-TR')));

        // Tip
        const typeTd = Utils.createElement('td');
        const typeMap = { 'IN': 'Giriş', 'OUT': 'Çıkış', 'TRANSFER': 'Transfer' };
        const typeColorMap = { 'IN': 'success', 'OUT': 'danger', 'TRANSFER': 'info' };
        const typeBadge = Utils.createElement('span', {
            class: `status-badge ${typeColorMap[movement.movement_type] || 'default'}`
        }, typeMap[movement.movement_type] || movement.movement_type);
        typeTd.appendChild(typeBadge);
        tr.appendChild(typeTd);

        // Ürün
        tr.appendChild(Utils.createElement('td', {}, movement.product_name || '-'));

        // Depo (Girişte to_warehouse, Çıkışta from_warehouse)
        const warehouseName = movement.movement_type === 'IN'
            ? movement.to_warehouse_name
            : movement.from_warehouse_name;
        tr.appendChild(Utils.createElement('td', {}, warehouseName || '-'));

        // Miktar
        tr.appendChild(Utils.createElement('td', {}, movement.quantity?.toString() || '0'));

        // Açıklama
        tr.appendChild(Utils.createElement('td', {}, movement.notes || '-'));

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.appendChild(table);
}

/**
 * Hareket ekleme modal
 */
function openMovementModal() {
    document.body.style.overflow = 'hidden';
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = '';

    const overlay = Utils.createElement('div', { class: 'modal-overlay show' });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
    });

    const modal = Utils.createElement('div', {
        class: 'modal-content',
        style: 'max-width: 500px;'
    });

    // Header
    const header = Utils.createElement('div', { class: 'modal-header' });
    header.appendChild(Utils.createElement('h3', {}, 'Stok Hareketi Ekle'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    // Form
    const form = Utils.createElement('form');
    form.addEventListener('submit', createMovement);

    const body = Utils.createElement('div', { class: 'modal-body' });

    // Hareket Tipi
    const typeGroup = Utils.createElement('div', { class: 'form-group' });
    typeGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Hareket Tipi'));
    const typeSelect = Utils.createElement('select', { class: 'form-select', name: 'movement_type', required: '' });
    typeSelect.appendChild(Utils.createElement('option', { value: 'IN' }, 'Giriş'));
    typeSelect.appendChild(Utils.createElement('option', { value: 'OUT' }, 'Çıkış'));
    typeGroup.appendChild(typeSelect);
    body.appendChild(typeGroup);

    // Proje
    const projectGroup = Utils.createElement('div', { class: 'form-group' });
    projectGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Proje'));
    const projectSelect = Utils.createElement('select', { class: 'form-select', name: 'project_id', required: '' });
    projectSelect.appendChild(Utils.createElement('option', { value: '' }, 'Seçiniz'));
    projects.forEach(p => {
        projectSelect.appendChild(Utils.createElement('option', { value: p.id }, `${p.project_code} - ${p.title}`));
    });
    projectGroup.appendChild(projectSelect);
    body.appendChild(projectGroup);

    // Ürün
    const productGroup = Utils.createElement('div', { class: 'form-group' });
    productGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Ürün'));
    const productSelect = Utils.createElement('select', { class: 'form-select', name: 'product_id', required: '' });
    productSelect.appendChild(Utils.createElement('option', { value: '' }, 'Seçiniz'));
    products.forEach(p => {
        productSelect.appendChild(Utils.createElement('option', { value: p.id }, `${p.sku} - ${p.name}`));
    });
    productGroup.appendChild(productSelect);
    body.appendChild(productGroup);

    // Depo
    const warehouseGroup = Utils.createElement('div', { class: 'form-group' });
    warehouseGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Depo'));
    const warehouseSelect = Utils.createElement('select', { class: 'form-select', name: 'warehouse_id', required: '' });
    warehouseSelect.appendChild(Utils.createElement('option', { value: '' }, 'Seçiniz'));
    warehouses.forEach(w => {
        warehouseSelect.appendChild(Utils.createElement('option', { value: w.id }, w.name));
    });
    warehouseGroup.appendChild(warehouseSelect);
    body.appendChild(warehouseGroup);

    // Miktar
    const qtyGroup = Utils.createElement('div', { class: 'form-group' });
    qtyGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Miktar'));
    qtyGroup.appendChild(Utils.createElement('input', { type: 'number', class: 'form-input', name: 'quantity', required: '', min: '1' }));
    body.appendChild(qtyGroup);

    // Açıklama
    const descGroup = Utils.createElement('div', { class: 'form-group' });
    descGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Açıklama'));
    descGroup.appendChild(Utils.createElement('textarea', { class: 'form-input', name: 'notes', rows: '2' }));
    body.appendChild(descGroup);

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
 * Transfer modal
 */
function openTransferModal() {
    document.body.style.overflow = 'hidden';
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = '';

    const overlay = Utils.createElement('div', { class: 'modal-overlay show' });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
    });

    const modal = Utils.createElement('div', {
        class: 'modal-content',
        style: 'max-width: 500px;'
    });

    // Header
    const header = Utils.createElement('div', { class: 'modal-header' });
    header.appendChild(Utils.createElement('h3', {}, 'Stok Transferi'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    // Form
    const form = Utils.createElement('form');
    form.addEventListener('submit', createTransfer);

    const body = Utils.createElement('div', { class: 'modal-body' });

    // Ürün
    const productGroup = Utils.createElement('div', { class: 'form-group' });
    productGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Ürün'));
    const productSelect = Utils.createElement('select', { class: 'form-select', name: 'product_id', required: '' });
    productSelect.appendChild(Utils.createElement('option', { value: '' }, 'Seçiniz'));
    products.forEach(p => {
        productSelect.appendChild(Utils.createElement('option', { value: p.id }, `${p.sku} - ${p.name}`));
    });
    productGroup.appendChild(productSelect);
    body.appendChild(productGroup);

    // Çıkış Depo
    const fromGroup = Utils.createElement('div', { class: 'form-group' });
    fromGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Çıkış Deposu'));
    const fromSelect = Utils.createElement('select', { class: 'form-select', name: 'from_warehouse_id', required: '' });
    fromSelect.appendChild(Utils.createElement('option', { value: '' }, 'Seçiniz'));
    warehouses.forEach(w => {
        fromSelect.appendChild(Utils.createElement('option', { value: w.id }, w.name));
    });
    fromGroup.appendChild(fromSelect);
    body.appendChild(fromGroup);

    // Giriş Depo
    const toGroup = Utils.createElement('div', { class: 'form-group' });
    toGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Giriş Deposu'));
    const toSelect = Utils.createElement('select', { class: 'form-select', name: 'to_warehouse_id', required: '' });
    toSelect.appendChild(Utils.createElement('option', { value: '' }, 'Seçiniz'));
    warehouses.forEach(w => {
        toSelect.appendChild(Utils.createElement('option', { value: w.id }, w.name));
    });
    toGroup.appendChild(toSelect);
    body.appendChild(toGroup);

    // Miktar
    const qtyGroup = Utils.createElement('div', { class: 'form-group' });
    qtyGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Miktar'));
    qtyGroup.appendChild(Utils.createElement('input', { type: 'number', class: 'form-input', name: 'quantity', required: '', min: '1' }));
    body.appendChild(qtyGroup);

    form.appendChild(body);

    // Footer
    const footer = Utils.createElement('div', { class: 'modal-footer' });
    const cancelBtn = Utils.createElement('button', { type: 'button', class: 'btn btn-ghost' }, 'İptal');
    cancelBtn.addEventListener('click', closeModal);
    footer.appendChild(cancelBtn);
    footer.appendChild(Utils.createElement('button', { type: 'submit', class: 'btn btn-primary' }, 'Transfer Et'));
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
 * Hareket oluştur
 */
async function createMovement(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {};
    formData.forEach((value, key) => {
        if (value) {
            if (['product_id', 'warehouse_id', 'quantity', 'project_id'].includes(key)) {
                data[key] = parseInt(value);
            } else {
                data[key] = value;
            }
        }
    });

    // Set warehouse based on movement type
    if (data.movement_type === 'IN') {
        data.to_warehouse_id = data.warehouse_id;
    } else {
        data.from_warehouse_id = data.warehouse_id;
    }
    delete data.warehouse_id;

    try {
        await API.post('/stock/movements', data);
        closeModal();
        Utils.toast.success('Hareket kaydedildi');
        loadMovements();
        loadSummary();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

/**
 * Transfer oluştur
 */
async function createTransfer(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {};
    formData.forEach((value, key) => {
        if (value) {
            if (['product_id', 'from_warehouse_id', 'to_warehouse_id', 'quantity'].includes(key)) {
                data[key] = parseInt(value);
            } else {
                data[key] = value;
            }
        }
    });

    if (data.from_warehouse_id === data.to_warehouse_id) {
        Utils.toast.warning('Çıkış ve giriş deposu aynı olamaz');
        return;
    }

    try {
        await API.stock.transfer(data);
        closeModal();
        Utils.toast.success('Transfer başarılı');
        loadMovements();
        loadSummary();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

// Global fonksiyonlar
window.openMovementModal = openMovementModal;
window.openTransferModal = openTransferModal;
window.closeModal = closeModal;
window.loadMovements = loadMovements;

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', async function () {
    if (!API.getToken()) {
        window.location.href = 'login.html';
        return;
    }
    await loadInitialData();
    loadSummary();
    loadMovements();
});
