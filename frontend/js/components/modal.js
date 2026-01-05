/**
 * Betsan CRM - Modal Component
 */

const Modal = {
    show(options) {
        const container = document.getElementById('modal-container');
        if (!container) return;

        const { title, content, footer, size = 'md' } = options;

        container.innerHTML = `
            <div class="modal-backdrop" onclick="Modal.close()"></div>
            <div class="modal-dialog modal-${size}">
                <div class="modal-header">
                    <h3 class="modal-title">${title || ''}</h3>
                    <button class="modal-close" onclick="Modal.close()">×</button>
                </div>
                <div class="modal-body">${content || ''}</div>
                ${footer ? `<div class="modal-footer">${footer}</div>` : ''}
            </div>
        `;

        container.classList.add('show');
        document.body.style.overflow = 'hidden';
    },

    close() {
        const container = document.getElementById('modal-container');
        if (!container) return;

        container.classList.remove('show');
        container.innerHTML = '';
        document.body.style.overflow = '';
    }
};

window.Modal = Modal;
