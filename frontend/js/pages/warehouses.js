/**
 * Otomasyon CRM - Warehouses Page Module
 */

import { API } from '../api.js';
import { Utils } from '../utils.js';
import '../components/sidebar.js';
import '../components/header.js';
import '../layout-loader.js';

let warehouses = [];

/**
 * Depoları yükle
 */
async function loadWarehouses() {
    const container = document.getElementById('warehouses-container');

    try {
        const search = document.getElementById('search-input').value;
        const warehouseType = document.getElementById('type-filter').value;

        let params = {};
        if (search) params.search = search;
        if (warehouseType) params.warehouse_type = warehouseType;

        warehouses = await API.warehouses.getAll(params);
        renderCards(warehouses);
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
 * Kart görünümünü render et
 */
function renderCards(data) {
    const container = document.getElementById('warehouses-container');
    container.innerHTML = '';

    if (data.length === 0) {
        const emptyDiv = Utils.createElement('div', { class: 'empty-state', style: 'grid-column: 1 / -1;' });
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-icon' }, '🏭'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-title' }, 'Henüz depo yok'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-message' }, 'Yeni depo ekleyerek başlayın'));

        const addBtn = Utils.createElement('button', {
            class: 'btn btn-primary',
            style: 'margin-top: var(--spacing-md);'
        }, 'Yeni Depo Ekle');
        addBtn.addEventListener('click', openCreateModal);
        emptyDiv.appendChild(addBtn);

        container.appendChild(emptyDiv);
        return;
    }

    data.forEach(warehouse => {
        const card = Utils.createElement('div', { class: 'content-card' });

        // Card Header
        const header = Utils.createElement('div', {
            class: 'content-card-header',
            style: 'display: flex; justify-content: space-between; align-items: center;'
        });

        const titleWrapper = Utils.createElement('div');
        const icon = warehouse.warehouse_type === 'PHYSICAL' ? '🏭' : '🚛';
        titleWrapper.appendChild(Utils.createElement('h3', {}, `${icon} ${warehouse.name}`));
        titleWrapper.appendChild(Utils.createElement('div', {
            style: 'font-size: var(--font-size-sm); color: var(--text-muted);'
        }, `Kod: ${warehouse.code}`));
        header.appendChild(titleWrapper);

        const typeBadge = Utils.createElement('span', {
            class: `status-badge ${warehouse.warehouse_type === 'PHYSICAL' ? 'info' : 'warning'}`
        }, warehouse.warehouse_type === 'PHYSICAL' ? 'Fiziksel' : 'Sanal');
        header.appendChild(typeBadge);

        card.appendChild(header);

        // Card Body
        const body = Utils.createElement('div', { class: 'content-card-body' });

        if (warehouse.warehouse_type === 'VIRTUAL' && warehouse.vehicle_plate) {
            const plateDiv = Utils.createElement('div', { style: 'margin-bottom: var(--spacing-sm);' });
            plateDiv.appendChild(Utils.createElement('strong', {}, 'Plaka: '));
            plateDiv.appendChild(document.createTextNode(warehouse.vehicle_plate));
            body.appendChild(plateDiv);
        }

        if (warehouse.address) {
            const addressDiv = Utils.createElement('div', { style: 'margin-bottom: var(--spacing-sm);' });
            addressDiv.appendChild(Utils.createElement('strong', {}, 'Adres: '));
            addressDiv.appendChild(document.createTextNode(warehouse.address));
            body.appendChild(addressDiv);
        }

        // Stock summary placeholder
        const stockDiv = Utils.createElement('div', {
            style: 'padding: var(--spacing-sm); background: var(--bg-tertiary); border-radius: var(--radius-sm); margin-top: var(--spacing-sm);'
        });
        stockDiv.appendChild(Utils.createElement('div', {
            style: 'font-size: var(--font-size-sm); color: var(--text-muted);'
        }, 'Stok özeti için depoya tıklayın'));
        body.appendChild(stockDiv);

        card.appendChild(body);

        // Card Footer
        const footer = Utils.createElement('div', {
            class: 'content-card-footer',
            style: 'display: flex; gap: var(--spacing-sm);'
        });

        const viewBtn = Utils.createElement('button', { class: 'btn btn-outline btn-sm' }, 'Stok Görüntüle');
        viewBtn.addEventListener('click', () => viewWarehouseStock(warehouse.id));
        footer.appendChild(viewBtn);

        const editBtn = Utils.createElement('button', { class: 'btn btn-ghost btn-sm' }, 'Düzenle');
        editBtn.addEventListener('click', () => editWarehouse(warehouse.id));
        footer.appendChild(editBtn);

        const deleteBtn = Utils.createElement('button', { class: 'btn btn-ghost btn-sm', style: 'color: var(--danger);' }, 'Sil');
        deleteBtn.addEventListener('click', () => deleteWarehouse(warehouse.id, warehouse.name));
        footer.appendChild(deleteBtn);

        card.appendChild(footer);
        container.appendChild(card);
    });
}

/**
 * Yeni depo modal
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
        style: 'max-width: 500px;'
    });

    // Header
    const header = Utils.createElement('div', { class: 'modal-header' });
    header.appendChild(Utils.createElement('h3', {}, 'Yeni Depo'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    // Form
    const form = Utils.createElement('form');
    form.addEventListener('submit', createWarehouse);

    const body = Utils.createElement('div', { class: 'modal-body' });

    // Depo Adı
    const nameGroup = Utils.createElement('div', { class: 'form-group' });
    nameGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Depo Adı'));
    nameGroup.appendChild(Utils.createElement('input', { type: 'text', class: 'form-input', name: 'name', required: '' }));
    body.appendChild(nameGroup);

    // Kod
    const codeGroup = Utils.createElement('div', { class: 'form-group' });
    codeGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Depo Kodu'));
    codeGroup.appendChild(Utils.createElement('input', { type: 'text', class: 'form-input', name: 'code', required: '', placeholder: 'ör: DEPO-001' }));
    body.appendChild(codeGroup);

    // Tip
    const typeGroup = Utils.createElement('div', { class: 'form-group' });
    typeGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Depo Tipi'));
    const typeSelect = Utils.createElement('select', { class: 'form-select', name: 'warehouse_type', required: '' });
    typeSelect.appendChild(Utils.createElement('option', { value: 'PHYSICAL' }, 'Fiziksel Depo'));
    typeSelect.appendChild(Utils.createElement('option', { value: 'VIRTUAL' }, 'Sanal Depo (Araç)'));
    typeSelect.addEventListener('change', (e) => {
        const plateGroup = document.getElementById('plate-group');
        plateGroup.style.display = e.target.value === 'VIRTUAL' ? 'block' : 'none';
    });
    typeGroup.appendChild(typeSelect);
    body.appendChild(typeGroup);

    // Araç Plakası (koşullu)
    const plateGroup = Utils.createElement('div', { class: 'form-group', id: 'plate-group', style: 'display: none;' });
    plateGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Araç Plakası'));
    plateGroup.appendChild(Utils.createElement('input', { type: 'text', class: 'form-input', name: 'vehicle_plate', placeholder: 'ör: 34 ABC 123' }));
    body.appendChild(plateGroup);

    // Adres
    const addressGroup = Utils.createElement('div', { class: 'form-group' });
    addressGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Adres'));
    addressGroup.appendChild(Utils.createElement('textarea', { class: 'form-input', name: 'address', rows: '2' }));
    body.appendChild(addressGroup);

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
 * Yeni depo oluştur
 */
async function createWarehouse(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {};
    formData.forEach((value, key) => {
        if (value) data[key] = value;
    });

    try {
        await API.warehouses.create(data);
        closeModal();
        Utils.toast.success('Depo başarıyla oluşturuldu');
        loadWarehouses();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

/**
 * Depo düzenle
 */
function editWarehouse(id) {
    const warehouse = warehouses.find(w => w.id === id);
    if (!warehouse) return;

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
    header.appendChild(Utils.createElement('h3', {}, 'Depo Düzenle'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    // Form
    const form = Utils.createElement('form');
    form.addEventListener('submit', (e) => updateWarehouse(e, id));

    const body = Utils.createElement('div', { class: 'modal-body' });

    // Form alanları
    const fields = [
        { name: 'name', label: 'Depo Adı', value: warehouse.name, required: true },
        { name: 'address', label: 'Adres', value: warehouse.address || '', type: 'textarea' }
    ];

    if (warehouse.warehouse_type === 'VIRTUAL') {
        fields.push({ name: 'vehicle_plate', label: 'Araç Plakası', value: warehouse.vehicle_plate || '' });
    }

    fields.forEach(field => {
        const group = Utils.createElement('div', { class: 'form-group' });
        group.appendChild(Utils.createElement('label', {
            class: field.required ? 'form-label required' : 'form-label'
        }, field.label));

        const input = field.type === 'textarea'
            ? Utils.createElement('textarea', { class: 'form-input', name: field.name, rows: '2' })
            : Utils.createElement('input', { type: 'text', class: 'form-input', name: field.name, value: field.value });

        if (field.type === 'textarea') input.textContent = field.value;
        if (field.required) input.setAttribute('required', '');

        group.appendChild(input);
        body.appendChild(group);
    });

    form.appendChild(body);

    // Footer
    const footer = Utils.createElement('div', { class: 'modal-footer' });
    const cancelBtn = Utils.createElement('button', { type: 'button', class: 'btn btn-ghost' }, 'İptal');
    cancelBtn.addEventListener('click', closeModal);
    footer.appendChild(cancelBtn);
    footer.appendChild(Utils.createElement('button', { type: 'submit', class: 'btn btn-primary' }, 'Güncelle'));
    form.appendChild(footer);

    modal.appendChild(form);
    overlay.appendChild(modal);
    modalContainer.appendChild(overlay);
}

/**
 * Depo güncelle
 */
async function updateWarehouse(event, id) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {};
    formData.forEach((value, key) => {
        if (value) data[key] = value;
    });

    try {
        await API.warehouses.update(id, data);
        closeModal();
        Utils.toast.success('Depo güncellendi');
        loadWarehouses();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

/**
 * Depo stoğunu görüntüle
 */
async function viewWarehouseStock(warehouseId) {
    try {
        const stock = await API.warehouses.getStock(warehouseId);
        const warehouse = warehouses.find(w => w.id === warehouseId);

        document.body.style.overflow = 'hidden';
        const modalContainer = document.getElementById('modal-container');
        modalContainer.innerHTML = '';

        const overlay = Utils.createElement('div', { class: 'modal-overlay show' });
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closeModal();
        });

        const modal = Utils.createElement('div', {
            class: 'modal-content',
            style: 'max-width: 700px;'
        });

        const header = Utils.createElement('div', { class: 'modal-header' });
        header.appendChild(Utils.createElement('h3', {}, `Stok - ${warehouse?.name || 'Depo'}`));
        const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
        closeBtn.addEventListener('click', closeModal);
        header.appendChild(closeBtn);
        modal.appendChild(header);

        const body = Utils.createElement('div', { class: 'modal-body' });

        if (stock.length === 0) {
            body.appendChild(Utils.createElement('p', { style: 'text-align: center; color: var(--text-muted);' }, 'Bu depoda stok bulunmuyor'));
        } else {
            const table = Utils.createElement('table', { class: 'data-table' });
            const thead = Utils.createElement('thead');
            const headerRow = Utils.createElement('tr');
            ['SKU', 'Ürün', 'Miktar', 'Rezerve', 'Kullanılabilir'].forEach(text => {
                headerRow.appendChild(Utils.createElement('th', {}, text));
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);

            const tbody = Utils.createElement('tbody');
            stock.forEach(item => {
                const tr = Utils.createElement('tr');

                // SKU with code element
                const skuTd = Utils.createElement('td');
                const skuCode = Utils.createElement('code', {}, item.product_sku || '-');
                skuTd.appendChild(skuCode);
                tr.appendChild(skuTd);

                tr.appendChild(Utils.createElement('td', {}, item.product_name || 'İsimsiz'));
                tr.appendChild(Utils.createElement('td', {}, item.quantity?.toString() || '0'));
                tr.appendChild(Utils.createElement('td', {}, item.reserved_quantity?.toString() || '0'));

                const available = (item.quantity || 0) - (item.reserved_quantity || 0);
                const availableTd = Utils.createElement('td');
                const badge = Utils.createElement('span', {
                    class: `status-badge ${available > 0 ? 'success' : 'danger'}`
                }, available.toString());
                availableTd.appendChild(badge);
                tr.appendChild(availableTd);

                tbody.appendChild(tr);
            });
            table.appendChild(tbody);
            body.appendChild(table);
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
        Utils.toast.error('Stok yüklenemedi: ' + error.message);
    }
}

/**
 * Depo sil - Modal göster
 */
function deleteWarehouse(id, name) {
    document.body.style.overflow = 'hidden';
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = '';

    const overlay = Utils.createElement('div', { class: 'modal-overlay show' });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
    });

    const modal = Utils.createElement('div', { class: 'modal-content', style: 'max-width: 400px;' });
    modal.addEventListener('click', (e) => e.stopPropagation());

    const header = Utils.createElement('div', { class: 'modal-header' });
    header.appendChild(Utils.createElement('h3', { style: 'color: var(--danger);' }, '⚠️ Depo Sil'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    const body = Utils.createElement('div', { class: 'modal-body' });
    body.appendChild(Utils.createElement('p', {}, `"${name}" deposunu silmek istediğinize emin misiniz?`));
    body.appendChild(Utils.createElement('p', { style: 'font-size: var(--font-size-sm); color: var(--text-muted); margin-top: var(--spacing-sm);' }, 'Stoğu olan depolar normalde silinemez.'));

    // Force delete checkbox
    const forceGroup = Utils.createElement('div', { style: 'margin-top: var(--spacing-md); padding: var(--spacing-sm); background: var(--warning-bg); border-radius: var(--radius-md);' });
    const forceLabel = Utils.createElement('label', { style: 'display: flex; align-items: center; gap: var(--spacing-xs); cursor: pointer;' });
    const forceCheckbox = Utils.createElement('input', { type: 'checkbox', id: 'force-delete-warehouse' });
    forceLabel.appendChild(forceCheckbox);
    forceLabel.appendChild(Utils.createElement('span', { style: 'font-size: var(--font-size-sm);' }, 'Stok kaydını da sil (zorla sil)'));
    forceGroup.appendChild(forceLabel);
    body.appendChild(forceGroup);

    modal.appendChild(body);

    const footer = Utils.createElement('div', { class: 'modal-footer' });
    const cancelBtn = Utils.createElement('button', { type: 'button', class: 'btn btn-ghost' }, 'İptal');
    cancelBtn.addEventListener('click', closeModal);
    footer.appendChild(cancelBtn);

    const confirmBtn = Utils.createElement('button', { type: 'button', class: 'btn btn-danger' }, 'Sil');
    confirmBtn.addEventListener('click', async () => {
        try {
            confirmBtn.disabled = true;
            confirmBtn.textContent = 'Siliniyor...';
            const forceDelete = document.getElementById('force-delete-warehouse').checked;
            await API.delete(`/warehouses/${id}${forceDelete ? '?force=true' : ''}`);
            closeModal();
            Utils.toast.success('Depo silindi');
            loadWarehouses();
        } catch (error) {
            Utils.toast.error(error.message || 'Depoda stok bulunuyor olabilir.');
            confirmBtn.disabled = false;
            confirmBtn.textContent = 'Sil';
        }
    });
    footer.appendChild(confirmBtn);
    modal.appendChild(footer);

    overlay.appendChild(modal);
    modalContainer.appendChild(overlay);
}

// Global fonksiyonlar
window.openCreateModal = openCreateModal;
window.closeModal = closeModal;
window.loadWarehouses = loadWarehouses;

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function () {
    if (!API.getToken()) {
        window.location.href = 'login.html';
        return;
    }
    loadWarehouses();

    document.getElementById('search-input').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') loadWarehouses();
    });
});
