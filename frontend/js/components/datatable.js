/**
 * Otomasyon CRM - DataTable Component
 * XSS Korumalı, Güvenli DOM Manipülasyonu
 */

import { Utils } from '../utils.js';

const DataTable = {
    /**
     * Güvenli tablo oluşturma
     */
    create(container, options) {
        const { columns, data, actions } = options;
        const targetEl = typeof container === 'string'
            ? document.querySelector(container)
            : container;

        if (!targetEl) return;

        // Container'ı temizle
        targetEl.innerHTML = '';

        // Wrapper oluştur
        const wrapper = Utils.createElement('div', { class: 'data-table-wrapper' });
        const table = Utils.createElement('table', { class: 'data-table' });

        // Thead oluştur
        const thead = Utils.createElement('thead');
        const headerRow = Utils.createElement('tr');

        columns.forEach(col => {
            const th = Utils.createElement('th', {}, col.label);
            headerRow.appendChild(th);
        });

        if (actions) {
            const actionTh = Utils.createElement('th', {}, 'İşlemler');
            headerRow.appendChild(actionTh);
        }

        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Tbody oluştur
        const tbody = Utils.createElement('tbody');

        if (data.length === 0) {
            const emptyRow = Utils.createElement('tr');
            const emptyCell = Utils.createElement('td', {
                colspan: columns.length + (actions ? 1 : 0),
                class: 'text-center text-muted p-lg'
            }, 'Veri bulunamadı');
            emptyRow.appendChild(emptyCell);
            tbody.appendChild(emptyRow);
        } else {
            data.forEach(row => {
                const tr = Utils.createElement('tr');

                columns.forEach(col => {
                    const td = Utils.createElement('td');
                    const value = row[col.field];

                    if (col.render) {
                        // Render fonksiyonu varsa, güvenli HTML oluşturması beklenir
                        // veya string döndürür
                        const rendered = col.render(value, row);
                        if (typeof rendered === 'string') {
                            // String ise güvenli şekilde ekle
                            td.innerHTML = rendered;
                        } else if (rendered instanceof HTMLElement) {
                            td.appendChild(rendered);
                        } else {
                            td.textContent = String(rendered || '');
                        }
                    } else {
                        // Düz metin olarak ekle (XSS güvenli)
                        td.textContent = value !== null && value !== undefined ? String(value) : '';
                    }

                    tr.appendChild(td);
                });

                if (actions) {
                    const actionTd = Utils.createElement('td', { class: 'table-actions' });
                    const actionContent = actions(row);

                    if (typeof actionContent === 'string') {
                        actionTd.innerHTML = actionContent;
                    } else if (actionContent instanceof HTMLElement) {
                        actionTd.appendChild(actionContent);
                    }

                    tr.appendChild(actionTd);
                }

                tbody.appendChild(tr);
            });
        }

        table.appendChild(tbody);
        wrapper.appendChild(table);
        targetEl.appendChild(wrapper);
    }
};

export { DataTable };
