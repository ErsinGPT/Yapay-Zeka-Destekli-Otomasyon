/**
 * Otomasyon CRM - Login Page Module
 */

import { API } from '../api.js';

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');
    const btnLogin = document.getElementById('btn-login');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    // Redirect if already logged in
    if (API.getToken()) {
        window.location.href = '../index.html';
        return;
    }

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!email || !password) {
            showError('E-posta ve şifre gereklidir');
            return;
        }

        // Show loading state
        btnLogin.classList.add('loading');
        btnLogin.disabled = true;
        hideError();

        try {
            await API.auth.login(email, password);
            window.location.href = '../index.html';
        } catch (error) {
            console.error('Login error:', error);
            showError(error.message || 'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.');
        } finally {
            btnLogin.classList.remove('loading');
            btnLogin.disabled = false;
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.add('show');
    }

    function hideError() {
        errorMessage.classList.remove('show');
    }

    emailInput.addEventListener('input', hideError);
    passwordInput.addEventListener('input', hideError);

    // Forgot Password Modal
    const forgotLink = document.querySelector('.forgot-password');
    const forgotModal = document.getElementById('forgot-modal');
    const modalClose = document.getElementById('modal-close');
    const modalOk = document.getElementById('modal-ok');

    function openModal() {
        forgotModal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        forgotModal.classList.remove('show');
        document.body.style.overflow = '';
    }

    forgotLink.addEventListener('click', function (e) {
        e.preventDefault();
        openModal();
    });

    modalClose.addEventListener('click', closeModal);
    modalOk.addEventListener('click', closeModal);

    forgotModal.addEventListener('click', function (e) {
        if (e.target === forgotModal) {
            closeModal();
        }
    });
});
