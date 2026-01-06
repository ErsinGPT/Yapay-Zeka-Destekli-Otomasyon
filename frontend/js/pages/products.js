/**
 * Otomasyon CRM - Products Page Module
 */

import { API } from '../api.js';
import { Utils } from '../utils.js';
import '../components/sidebar.js';
import '../components/header.js';
import '../layout-loader.js';

let products = [];
let categories = [];

/**
 * Kategorileri yükle
 */
async function loadCategories() {
    try {
        categories = await API.get('/products/categories');
        const select = document.getElementById('category-filter');
        categories.forEach(cat => {
            const option = Utils.createElement('option', { value: cat.id }, cat.name);
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Kategoriler yüklenemedi:', error);
    }
}

/**
 * Ürünleri yükle
 */
async function loadProducts() {
    const container = document.getElementById('table-container');

    try {
        const search = document.getElementById('search-input').value;
        const categoryId = document.getElementById('category-filter').value;
        const isActive = document.getElementById('status-filter').value;

        let params = {};
        if (search) params.search = search;
        if (categoryId) params.category_id = categoryId;
        if (isActive) params.is_active = isActive;

        products = await API.products.getAll(params);
        renderTable(products);
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
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-icon' }, '📦'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-title' }, 'Henüz ürün yok'));
        emptyDiv.appendChild(Utils.createElement('div', { class: 'empty-state-message' }, 'Yeni ürün ekleyerek başlayın'));

        const addBtn = Utils.createElement('button', {
            class: 'btn btn-primary',
            style: 'margin-top: var(--spacing-md);'
        }, 'Yeni Ürün Ekle');
        addBtn.addEventListener('click', openCreateModal);
        emptyDiv.appendChild(addBtn);

        container.appendChild(emptyDiv);
        return;
    }

    const table = Utils.createElement('table', { class: 'data-table' });

    // Thead
    const thead = Utils.createElement('thead');
    const headerRow = Utils.createElement('tr');
    ['SKU', 'Ürün Adı', 'Kategori', 'Birim', 'Liste Fiyatı', 'Stok', 'Durum'].forEach(text => {
        headerRow.appendChild(Utils.createElement('th', {}, text));
    });
    headerRow.appendChild(Utils.createElement('th', { style: 'text-align: right;' }, 'İşlemler'));
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Tbody
    const tbody = Utils.createElement('tbody');

    data.forEach(product => {
        const tr = Utils.createElement('tr');

        // SKU
        const skuTd = Utils.createElement('td');
        const skuCode = Utils.createElement('code', {}, product.sku);
        skuTd.appendChild(skuCode);
        tr.appendChild(skuTd);

        // Ürün Adı
        const nameTd = Utils.createElement('td');
        const nameWrapper = Utils.createElement('div');
        nameWrapper.appendChild(Utils.createElement('strong', {}, product.name));
        if (product.barcode) {
            nameWrapper.appendChild(Utils.createElement('div', {
                style: 'font-size: var(--font-size-xs); color: var(--text-muted);'
            }, `Barkod: ${product.barcode}`));
        }
        nameTd.appendChild(nameWrapper);
        tr.appendChild(nameTd);

        // Kategori
        tr.appendChild(Utils.createElement('td', {}, product.category_name || '-'));

        // Birim
        tr.appendChild(Utils.createElement('td', {}, product.unit || 'Adet'));

        // Liste Fiyatı
        const priceTd = Utils.createElement('td');
        const price = parseFloat(product.list_price || 0).toLocaleString('tr-TR', { minimumFractionDigits: 2 });
        priceTd.textContent = `${price} ${product.currency || 'TRY'}`;
        tr.appendChild(priceTd);

        // Stok
        const stockTd = Utils.createElement('td');
        const totalStock = product.total_stock || 0;
        const availableStock = product.available_stock || 0;
        const stockBadge = Utils.createElement('span', {
            class: `status-badge ${availableStock > 0 ? 'success' : 'danger'}`
        }, `${availableStock} / ${totalStock}`);
        stockTd.appendChild(stockBadge);
        tr.appendChild(stockTd);

        // Durum
        const statusTd = Utils.createElement('td');
        const badge = Utils.createElement('span', {
            class: `status-badge ${product.is_active ? 'success' : 'danger'}`
        }, product.is_active ? 'Aktif' : 'Pasif');
        statusTd.appendChild(badge);
        tr.appendChild(statusTd);

        // İşlemler
        const actionTd = Utils.createElement('td', { style: 'text-align: right;' });

        const editBtn = Utils.createElement('button', { class: 'btn btn-ghost btn-sm' }, 'Düzenle');
        editBtn.addEventListener('click', () => editProduct(product.id));
        actionTd.appendChild(editBtn);

        if (product.is_bom) {
            const bomBtn = Utils.createElement('button', { class: 'btn btn-ghost btn-sm' }, 'BOM');
            bomBtn.addEventListener('click', () => showBom(product.id));
            actionTd.appendChild(bomBtn);
        }

        const deleteBtn = Utils.createElement('button', { class: 'btn btn-ghost btn-sm', style: 'color: var(--danger);' }, 'Sil');
        deleteBtn.addEventListener('click', () => deleteProduct(product.id, product.name));
        actionTd.appendChild(deleteBtn);

        tr.appendChild(actionTd);
        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.appendChild(table);
}

/**
 * Yeni ürün modal
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
    modal.addEventListener('click', (e) => e.stopPropagation());

    // Header
    const header = Utils.createElement('div', { class: 'modal-header' });
    header.appendChild(Utils.createElement('h3', {}, 'Yeni Ürün'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    // Form
    const form = Utils.createElement('form');
    form.addEventListener('submit', createProduct);

    const body = Utils.createElement('div', { class: 'modal-body' });

    // İki kolonlu form
    const row1 = Utils.createElement('div', { class: 'form-row' });

    // SKU
    const skuGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    skuGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'SKU'));
    skuGroup.appendChild(Utils.createElement('input', { type: 'text', class: 'form-input', name: 'sku', required: '' }));
    row1.appendChild(skuGroup);

    // Barkod
    const barcodeGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    barcodeGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Barkod'));
    barcodeGroup.appendChild(Utils.createElement('input', { type: 'text', class: 'form-input', name: 'barcode' }));
    row1.appendChild(barcodeGroup);
    body.appendChild(row1);

    // Ürün Adı
    const nameGroup = Utils.createElement('div', { class: 'form-group' });
    nameGroup.appendChild(Utils.createElement('label', { class: 'form-label required' }, 'Ürün Adı'));
    nameGroup.appendChild(Utils.createElement('input', { type: 'text', class: 'form-input', name: 'name', required: '' }));
    body.appendChild(nameGroup);

    // Kategori
    const categoryGroup = Utils.createElement('div', { class: 'form-group' });
    categoryGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Kategori'));
    const categorySelect = Utils.createElement('select', { class: 'form-select', name: 'category_id' });
    categorySelect.appendChild(Utils.createElement('option', { value: '' }, 'Seçiniz'));
    categories.forEach(cat => {
        categorySelect.appendChild(Utils.createElement('option', { value: cat.id }, cat.name));
    });
    categoryGroup.appendChild(categorySelect);
    body.appendChild(categoryGroup);

    // Birim ve Fiyat
    const row2 = Utils.createElement('div', { class: 'form-row' });

    const unitGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    unitGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Birim'));
    const unitSelect = Utils.createElement('select', { class: 'form-select', name: 'unit' });
    ['Adet', 'Metre', 'Kg', 'Lt', 'Paket', 'Kutu'].forEach(u => {
        unitSelect.appendChild(Utils.createElement('option', { value: u }, u));
    });
    unitGroup.appendChild(unitSelect);
    row2.appendChild(unitGroup);

    const priceGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    priceGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Liste Fiyatı'));
    priceGroup.appendChild(Utils.createElement('input', { type: 'number', step: '0.01', class: 'form-input', name: 'list_price' }));
    row2.appendChild(priceGroup);

    body.appendChild(row2);

    // Maliyet ve Para Birimi
    const row3 = Utils.createElement('div', { class: 'form-row' });

    const costGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    costGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Maliyet'));
    costGroup.appendChild(Utils.createElement('input', { type: 'number', step: '0.01', class: 'form-input', name: 'cost' }));
    row3.appendChild(costGroup);

    const currencyGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    currencyGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Para Birimi'));
    const currencySelect = Utils.createElement('select', { class: 'form-select', name: 'currency' });
    ['TRY', 'USD', 'EUR'].forEach(c => {
        currencySelect.appendChild(Utils.createElement('option', { value: c }, c));
    });
    currencyGroup.appendChild(currencySelect);
    row3.appendChild(currencyGroup);

    body.appendChild(row3);

    // BOM Section
    const bomSection = Utils.createElement('div', {
        style: 'margin-top: var(--spacing-md); padding-top: var(--spacing-md); border-top: 1px solid var(--border-color);'
    });
    bomSection.appendChild(Utils.createElement('h4', { style: 'margin-bottom: var(--spacing-sm);' }, 'Ürün Ağacı (BOM)'));

    // BOM gerekmiyor checkbox
    const noBomGroup = Utils.createElement('div', { class: 'form-group' });
    const noBomLabel = Utils.createElement('label', { style: 'display: flex; align-items: center; gap: var(--spacing-sm); cursor: pointer;' });
    const noBomCheckbox = Utils.createElement('input', { type: 'checkbox', name: 'no_bom', id: 'no-bom-checkbox' });
    noBomCheckbox.addEventListener('change', (e) => {
        const bomControls = document.getElementById('bom-controls');
        bomControls.style.display = e.target.checked ? 'none' : 'block';
    });
    noBomLabel.appendChild(noBomCheckbox);
    noBomLabel.appendChild(document.createTextNode('BOM Gerekmiyor (Basit Ürün)'));
    noBomGroup.appendChild(noBomLabel);
    bomSection.appendChild(noBomGroup);

    // BOM kontrolleri
    const bomControls = Utils.createElement('div', { id: 'bom-controls' });

    const bomList = Utils.createElement('div', { id: 'bom-items', style: 'margin-bottom: var(--spacing-sm);' });
    bomControls.appendChild(bomList);

    // BOM ekleme
    const bomAddRow = Utils.createElement('div', { class: 'form-row' });

    const bomProductGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 2;' });
    const bomProductSelect = Utils.createElement('select', { class: 'form-select', id: 'bom-product-select' });
    bomProductSelect.appendChild(Utils.createElement('option', { value: '' }, 'Malzeme seçin...'));
    products.forEach(p => {
        bomProductSelect.appendChild(Utils.createElement('option', { value: p.id }, `${p.sku} - ${p.name}`));
    });
    bomProductGroup.appendChild(bomProductSelect);
    bomAddRow.appendChild(bomProductGroup);

    const bomQtyGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    bomQtyGroup.appendChild(Utils.createElement('input', { type: 'number', class: 'form-input', id: 'bom-qty-input', placeholder: 'Miktar', min: '1', value: '1' }));
    bomAddRow.appendChild(bomQtyGroup);

    const addBomBtn = Utils.createElement('button', { type: 'button', class: 'btn btn-outline btn-sm' }, '+ Ekle');
    addBomBtn.addEventListener('click', addBomItem);
    bomAddRow.appendChild(addBomBtn);

    bomControls.appendChild(bomAddRow);
    bomSection.appendChild(bomControls);
    body.appendChild(bomSection);

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
 * Yeni ürün oluştur
 */
async function createProduct(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {};
    formData.forEach((value, key) => {
        if (value && key !== 'no_bom') {
            if (['list_price', 'cost', 'category_id'].includes(key)) {
                data[key] = parseFloat(value) || parseInt(value);
            } else {
                data[key] = value;
            }
        }
    });

    try {
        const product = await API.products.create(data);

        // BOM varsa ekle
        if (bomItems.length > 0 && !form.querySelector('#no-bom-checkbox').checked) {
            const bomData = bomItems.map(item => ({
                child_product_id: item.child_product_id,
                quantity: item.quantity
            }));
            await API.products.updateBom(product.id, bomData);
        }

        bomItems = []; // Reset BOM items
        closeModal();
        Utils.toast.success('Ürün başarıyla oluşturuldu');
        loadProducts();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

/**
 * Ürün düzenle
 */
function editProduct(id) {
    const product = products.find(p => p.id === id);
    if (!product) return;

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
    modal.addEventListener('click', (e) => e.stopPropagation());

    // Header
    const header = Utils.createElement('div', { class: 'modal-header' });
    header.appendChild(Utils.createElement('h3', {}, 'Ürün Düzenle'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    // Form
    const form = Utils.createElement('form');
    form.addEventListener('submit', (e) => updateProduct(e, id));

    const body = Utils.createElement('div', { class: 'modal-body' });

    // Form alanları
    const fields = [
        { name: 'sku', label: 'SKU', type: 'text', value: product.sku, required: true },
        { name: 'name', label: 'Ürün Adı', type: 'text', value: product.name, required: true },
        { name: 'barcode', label: 'Barkod', type: 'text', value: product.barcode || '' },
        { name: 'list_price', label: 'Liste Fiyatı', type: 'number', value: product.list_price || '' },
        { name: 'cost', label: 'Maliyet', type: 'number', value: product.cost || '' }
    ];

    fields.forEach(field => {
        const group = Utils.createElement('div', { class: 'form-group' });
        group.appendChild(Utils.createElement('label', {
            class: field.required ? 'form-label required' : 'form-label'
        }, field.label));
        const input = Utils.createElement('input', {
            type: field.type,
            class: 'form-input',
            name: field.name,
            value: field.value
        });
        if (field.required) input.setAttribute('required', '');
        if (field.type === 'number') input.setAttribute('step', '0.01');
        group.appendChild(input);
        body.appendChild(group);
    });

    // Durum
    const statusGroup = Utils.createElement('div', { class: 'form-group' });
    statusGroup.appendChild(Utils.createElement('label', { class: 'form-label' }, 'Durum'));
    const statusSelect = Utils.createElement('select', { class: 'form-select', name: 'is_active' });
    const activeOpt = Utils.createElement('option', { value: 'true' }, 'Aktif');
    const inactiveOpt = Utils.createElement('option', { value: 'false' }, 'Pasif');
    if (product.is_active) activeOpt.setAttribute('selected', '');
    else inactiveOpt.setAttribute('selected', '');
    statusSelect.appendChild(activeOpt);
    statusSelect.appendChild(inactiveOpt);
    statusGroup.appendChild(statusSelect);
    body.appendChild(statusGroup);

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
 * Ürün güncelle
 */
async function updateProduct(event, id) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {};
    formData.forEach((value, key) => {
        if (key === 'is_active') {
            data[key] = value === 'true';
        } else if (['list_price', 'cost'].includes(key) && value) {
            data[key] = parseFloat(value);
        } else if (value) {
            data[key] = value;
        }
    });

    try {
        await API.products.update(id, data);
        closeModal();
        Utils.toast.success('Ürün güncellendi');
        loadProducts();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

/**
 * BOM göster
 */
async function showBom(productId) {
    try {
        const bom = await API.products.getBom(productId);
        const product = products.find(p => p.id === productId);

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
        header.appendChild(Utils.createElement('h3', {}, `BOM - ${product?.name || 'Ürün'}`));
        const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
        closeBtn.addEventListener('click', closeModal);
        header.appendChild(closeBtn);
        modal.appendChild(header);

        const body = Utils.createElement('div', { class: 'modal-body' });

        if (bom.length === 0) {
            body.appendChild(Utils.createElement('p', { style: 'text-align: center; color: var(--text-muted);' }, 'Bu ürün için BOM tanımlanmamış'));
        } else {
            const table = Utils.createElement('table', { class: 'data-table' });
            const thead = Utils.createElement('thead');
            const headerRow = Utils.createElement('tr');
            ['Malzeme', 'SKU', 'Miktar'].forEach(text => {
                headerRow.appendChild(Utils.createElement('th', {}, text));
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);

            const tbody = Utils.createElement('tbody');
            bom.forEach(item => {
                const tr = Utils.createElement('tr');
                tr.appendChild(Utils.createElement('td', {}, item.child_product_name || 'İsimsiz'));
                tr.appendChild(Utils.createElement('td', {}, Utils.createElement('code', {}, item.child_product_sku || '-')));
                tr.appendChild(Utils.createElement('td', {}, item.quantity.toString()));
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
        Utils.toast.error('BOM yüklenemedi: ' + error.message);
    }
}

/**
 * Kategori modal
 */
function openCategoryModal() {
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

    const header = Utils.createElement('div', { class: 'modal-header' });
    header.appendChild(Utils.createElement('h3', {}, 'Kategoriler'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    const body = Utils.createElement('div', { class: 'modal-body' });

    // Yeni kategori formu
    const form = Utils.createElement('form', { style: 'margin-bottom: var(--spacing-md);' });
    form.addEventListener('submit', createCategory);

    const formRow = Utils.createElement('div', { class: 'form-row' });
    const inputGroup = Utils.createElement('div', { class: 'form-group', style: 'flex: 1;' });
    inputGroup.appendChild(Utils.createElement('input', {
        type: 'text',
        class: 'form-input',
        name: 'name',
        placeholder: 'Yeni kategori adı',
        required: ''
    }));
    formRow.appendChild(inputGroup);
    formRow.appendChild(Utils.createElement('button', { type: 'submit', class: 'btn btn-primary' }, 'Ekle'));
    form.appendChild(formRow);
    body.appendChild(form);

    // Kategori listesi
    const list = Utils.createElement('div', { id: 'category-list' });
    if (categories.length === 0) {
        list.appendChild(Utils.createElement('p', { style: 'color: var(--text-muted);' }, 'Henüz kategori yok'));
    } else {
        categories.forEach(cat => {
            const item = Utils.createElement('div', {
                style: 'padding: var(--spacing-sm); border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;'
            });
            item.appendChild(Utils.createElement('span', {}, cat.name));

            const deleteBtn = Utils.createElement('button', {
                class: 'btn btn-ghost btn-sm',
                style: 'color: var(--danger);'
            }, '×');
            deleteBtn.addEventListener('click', () => deleteCategory(cat.id, cat.name));
            item.appendChild(deleteBtn);

            list.appendChild(item);
        });
    }
    body.appendChild(list);

    modal.appendChild(body);

    const footer = Utils.createElement('div', { class: 'modal-footer' });
    const closeFooterBtn = Utils.createElement('button', { type: 'button', class: 'btn btn-ghost' }, 'Kapat');
    closeFooterBtn.addEventListener('click', closeModal);
    footer.appendChild(closeFooterBtn);
    modal.appendChild(footer);

    overlay.appendChild(modal);
    modalContainer.appendChild(overlay);
}

/**
 * Kategori oluştur
 */
async function createCategory(event) {
    event.preventDefault();
    const form = event.target;
    const name = form.querySelector('input[name="name"]').value;

    try {
        await API.post('/products/categories', { name });
        closeModal();
        await loadCategories();
        openCategoryModal();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

/**
 * Kategori sil - Modal göster
 */
function deleteCategory(id, name) {
    // Kategori modalını kapat
    closeModal();

    setTimeout(() => {
        document.body.style.overflow = 'hidden';
        const modalContainer = document.getElementById('modal-container');
        modalContainer.innerHTML = '';

        const overlay = Utils.createElement('div', { class: 'modal-overlay show' });
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) { closeModal(); openCategoryModal(); }
        });

        const modal = Utils.createElement('div', { class: 'modal-content', style: 'max-width: 400px;' });
        modal.addEventListener('click', (e) => e.stopPropagation());

        const header = Utils.createElement('div', { class: 'modal-header' });
        header.appendChild(Utils.createElement('h3', { style: 'color: var(--danger);' }, '⚠️ Kategori Sil'));
        const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
        closeBtn.addEventListener('click', () => { closeModal(); openCategoryModal(); });
        header.appendChild(closeBtn);
        modal.appendChild(header);

        const body = Utils.createElement('div', { class: 'modal-body' });
        body.appendChild(Utils.createElement('p', {}, `"${name}" kategorisini silmek istediğinize emin misiniz?`));
        body.appendChild(Utils.createElement('p', { style: 'font-size: var(--font-size-sm); color: var(--text-muted); margin-top: var(--spacing-sm);' }, 'Bu kategoride ürün varsa silme işlemi başarısız olacaktır.'));
        modal.appendChild(body);

        const footer = Utils.createElement('div', { class: 'modal-footer' });
        const cancelBtn = Utils.createElement('button', { type: 'button', class: 'btn btn-ghost' }, 'İptal');
        cancelBtn.addEventListener('click', () => { closeModal(); openCategoryModal(); });
        footer.appendChild(cancelBtn);

        const confirmBtn = Utils.createElement('button', { type: 'button', class: 'btn btn-danger' }, 'Sil');
        confirmBtn.addEventListener('click', async () => {
            try {
                confirmBtn.disabled = true;
                confirmBtn.textContent = 'Siliniyor...';
                await API.delete(`/products/categories/${id}`);
                closeModal();
                await loadCategories();
                Utils.toast.success('Kategori silindi');
                openCategoryModal();
            } catch (error) {
                Utils.toast.error(error.message || 'Bu kategoride ürün bulunuyor olabilir.');
                confirmBtn.disabled = false;
                confirmBtn.textContent = 'Sil';
            }
        });
        footer.appendChild(confirmBtn);
        modal.appendChild(footer);

        overlay.appendChild(modal);
        modalContainer.appendChild(overlay);
    }, 100);
}

/**
 * Ürün sil - Modal göster
 */
function deleteProduct(id, name) {
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
    header.appendChild(Utils.createElement('h3', { style: 'color: var(--danger);' }, '⚠️ Ürün Sil'));
    const closeBtn = Utils.createElement('button', { class: 'modal-close' }, '×');
    closeBtn.addEventListener('click', closeModal);
    header.appendChild(closeBtn);
    modal.appendChild(header);

    const body = Utils.createElement('div', { class: 'modal-body' });
    body.appendChild(Utils.createElement('p', {}, `"${name}" ürününü silmek istediğinize emin misiniz?`));
    body.appendChild(Utils.createElement('p', { style: 'font-size: var(--font-size-sm); color: var(--text-muted); margin-top: var(--spacing-sm);' }, 'Stoku olan ürünler normalde silinemez.'));

    // Force delete checkbox
    const forceGroup = Utils.createElement('div', { style: 'margin-top: var(--spacing-md); padding: var(--spacing-sm); background: var(--warning-bg); border-radius: var(--radius-md);' });
    const forceLabel = Utils.createElement('label', { style: 'display: flex; align-items: center; gap: var(--spacing-xs); cursor: pointer;' });
    const forceCheckbox = Utils.createElement('input', { type: 'checkbox', id: 'force-delete-checkbox' });
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
            const forceDelete = document.getElementById('force-delete-checkbox').checked;
            await API.delete(`/products/${id}${forceDelete ? '?force=true' : ''}`);
            closeModal();
            Utils.toast.success('Ürün silindi');
            loadProducts();
        } catch (error) {
            Utils.toast.error(error.message || 'Stoku olan ürün silinemez.');
            confirmBtn.disabled = false;
            confirmBtn.textContent = 'Sil';
        }
    });
    footer.appendChild(confirmBtn);
    modal.appendChild(footer);

    overlay.appendChild(modal);
    modalContainer.appendChild(overlay);
}

// BOM ekleme
let bomItems = [];

function addBomItem() {
    const productSelect = document.getElementById('bom-product-select');
    const qtyInput = document.getElementById('bom-qty-input');

    const productId = parseInt(productSelect.value);
    const qty = parseInt(qtyInput.value) || 1;

    if (!productId) {
        Utils.toast.warning('Lütfen bir malzeme seçin');
        return;
    }

    const product = products.find(p => p.id === productId);
    if (!product) return;

    // Zaten ekliyse miktarı güncelle
    const existing = bomItems.find(b => b.child_product_id === productId);
    if (existing) {
        existing.quantity += qty;
    } else {
        bomItems.push({
            child_product_id: productId,
            child_product_name: product.name,
            child_product_sku: product.sku,
            quantity: qty
        });
    }

    renderBomItems();
    productSelect.value = '';
    qtyInput.value = '1';
}

function removeBomItem(productId) {
    bomItems = bomItems.filter(b => b.child_product_id !== productId);
    renderBomItems();
}

function renderBomItems() {
    const container = document.getElementById('bom-items');
    if (!container) return;

    container.innerHTML = '';

    if (bomItems.length === 0) {
        container.appendChild(Utils.createElement('p', { style: 'color: var(--text-muted); font-size: var(--font-size-sm);' }, 'Henüz malzeme eklenmedi'));
        return;
    }

    bomItems.forEach(item => {
        const row = Utils.createElement('div', {
            style: 'display: flex; justify-content: space-between; align-items: center; padding: var(--spacing-xs); background: var(--bg-tertiary); border-radius: var(--radius-sm); margin-bottom: var(--spacing-xs);'
        });

        row.appendChild(Utils.createElement('span', {}, `${item.child_product_sku} - ${item.child_product_name} (x${item.quantity})`));

        const removeBtn = Utils.createElement('button', { type: 'button', class: 'btn btn-ghost btn-sm', style: 'color: var(--danger);' }, '×');
        removeBtn.addEventListener('click', () => removeBomItem(item.child_product_id));
        row.appendChild(removeBtn);

        container.appendChild(row);
    });
}

// Global fonksiyonlar
window.openCreateModal = openCreateModal;
window.openCategoryModal = openCategoryModal;
window.closeModal = closeModal;
window.loadProducts = loadProducts;

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function () {
    if (!API.getToken()) {
        window.location.href = 'login.html';
        return;
    }
    loadCategories();
    loadProducts();

    document.getElementById('search-input').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') loadProducts();
    });
});
