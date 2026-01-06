/**
 * Otomasyon CRM - Settings Page Module
 */

import { API } from '../api.js';
import { Utils } from '../utils.js';
import '../components/sidebar.js';
import '../components/header.js';
import '../layout-loader.js';

let settings = {};

/**
 * Ayarları yükle
 */
async function loadSettings() {
    try {
        settings = await API.get('/settings');
        populateForms();
    } catch (error) {
        console.error('Ayarlar yüklenemedi:', error);
        Utils.toast.error('Ayarlar yüklenemedi: ' + error.message);
    }
}

/**
 * Formları doldur
 */
function populateForms() {
    // Company settings
    const company = settings.company || {};
    const companyForm = document.getElementById('company-form');
    if (companyForm) {
        setFormValue(companyForm, 'company_name', company.company_name);
        setFormValue(companyForm, 'company_name_en', company.company_name_en);
        setFormValue(companyForm, 'tax_office', company.tax_office);
        setFormValue(companyForm, 'tax_id', company.tax_id);
        setFormValue(companyForm, 'address', company.address);
        setFormValue(companyForm, 'phone', company.phone);
        setFormValue(companyForm, 'email', company.email);
    }

    // Invoice numbering
    const invoicing = settings.invoice_numbering || {};
    const invoiceForm = document.getElementById('invoice-form');
    if (invoiceForm) {
        setFormValue(invoiceForm, 'prefix', invoicing.prefix || 'FTR');
        setFormValue(invoiceForm, 'separator', invoicing.separator || '-');
        setFormValue(invoiceForm, 'year_format', invoicing.year_format || '%Y');
        setFormValue(invoiceForm, 'padding', invoicing.padding || 6);
        setFormValue(invoiceForm, 'next_number', invoicing.next_number || 1);
        updateInvoicePreview();
    }

    // General settings
    const generalForm = document.getElementById('general-form');
    if (generalForm) {
        setFormValue(generalForm, 'default_currency', settings.default_currency || 'TRY');
        setFormValue(generalForm, 'default_vat_rate', settings.default_vat_rate || 20);
    }
}

/**
 * Form alanına değer ata
 */
function setFormValue(form, name, value) {
    const element = form.querySelector(`[name="${name}"]`);
    if (element && value !== undefined && value !== null) {
        element.value = value;
    }
}

/**
 * Tab değiştir
 */
function switchTab(tabName) {
    // Tab butonlarını güncelle
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Tab içeriklerini güncelle
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = 'none';
    });
    document.getElementById(`${tabName}-tab`).style.display = 'block';
}

/**
 * Fatura numarası önizlemesini güncelle
 */
function updateInvoicePreview() {
    const form = document.getElementById('invoice-form');
    const prefix = form.querySelector('[name="prefix"]').value || 'FTR';
    const separator = form.querySelector('[name="separator"]').value || '-';
    const yearFormat = form.querySelector('[name="year_format"]').value || '%Y';
    const padding = parseInt(form.querySelector('[name="padding"]').value) || 6;
    const nextNumber = parseInt(form.querySelector('[name="next_number"]').value) || 1;

    const year = yearFormat === '%Y' ? new Date().getFullYear() : new Date().getFullYear().toString().slice(-2);
    const number = nextNumber.toString().padStart(padding, '0');

    const preview = `${prefix}${separator}${year}${separator}${number}`;
    document.getElementById('invoice-preview').textContent = preview;
}

/**
 * Şirket ayarlarını kaydet
 */
async function saveCompanySettings(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {};
    formData.forEach((value, key) => {
        if (value) data[key] = value;
    });

    try {
        await API.put('/settings/company', data);
        Utils.toast.success('Şirket bilgileri kaydedildi');
        loadSettings();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

/**
 * Fatura ayarlarını kaydet
 */
async function saveInvoiceSettings(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const data = {};
    formData.forEach((value, key) => {
        if (value) {
            if (['padding', 'next_number'].includes(key)) {
                data[key] = parseInt(value);
            } else {
                data[key] = value;
            }
        }
    });

    try {
        await API.put('/settings/invoice-numbering', data);
        Utils.toast.success('Fatura ayarları kaydedildi');
        loadSettings();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

/**
 * Genel ayarları kaydet
 */
async function saveGeneralSettings(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    // Current settings'i güncelle
    const data = { ...settings };
    formData.forEach((value, key) => {
        if (value) {
            if (key === 'default_vat_rate') {
                data[key] = parseFloat(value);
            } else {
                data[key] = value;
            }
        }
    });

    try {
        await API.put('/settings', data);
        Utils.toast.success('Genel ayarlar kaydedildi');
        loadSettings();
    } catch (error) {
        Utils.toast.error(error.message || 'Bir hata oluştu');
    }
}

// Global fonksiyonlar
window.switchTab = switchTab;

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', async function () {
    if (!API.getToken()) {
        window.location.href = 'login.html';
        return;
    }

    await loadSettings();

    // Form event listeners
    document.getElementById('company-form').addEventListener('submit', saveCompanySettings);
    document.getElementById('invoice-form').addEventListener('submit', saveInvoiceSettings);
    document.getElementById('general-form').addEventListener('submit', saveGeneralSettings);

    // Invoice preview update
    const invoiceForm = document.getElementById('invoice-form');
    invoiceForm.querySelectorAll('input, select').forEach(input => {
        input.addEventListener('input', updateInvoicePreview);
    });
});
