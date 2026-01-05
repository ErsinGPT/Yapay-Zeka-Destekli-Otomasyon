/**
 * Betsan CRM - DataTable Component
 */

const DataTable = {
    create(container, options) {
        const { columns, data, actions } = options;

        let html = `
            <div class="data-table-wrapper">
                <table class="data-table">
                    <thead><tr>
                        ${columns.map(col => `<th>${col.label}</th>`).join('')}
                        ${actions ? '<th>İşlemler</th>' : ''}
                    </tr></thead>
                    <tbody>
        `;

        if (data.length === 0) {
            html += `<tr><td colspan="${columns.length + (actions ? 1 : 0)}" class="text-center text-muted p-lg">Veri bulunamadı</td></tr>`;
        } else {
            data.forEach(row => {
                html += '<tr>';
                columns.forEach(col => {
                    const value = row[col.field];
                    html += `<td>${col.render ? col.render(value, row) : value}</td>`;
                });
                if (actions) {
                    html += `<td class="table-actions">${actions(row)}</td>`;
                }
                html += '</tr>';
            });
        }

        html += '</tbody></table></div>';

        if (typeof container === 'string') {
            document.querySelector(container).innerHTML = html;
        } else {
            container.innerHTML = html;
        }
    }
};

window.DataTable = DataTable;
