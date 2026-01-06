/**
 * Otomasyon CRM - Authentication Module
 */

import { API } from './api.js';

const Auth = {
    currentUser: null,

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!API.getToken();
    },

    /**
     * Login user
     */
    async login(email, password) {
        try {
            await API.auth.login(email, password);
            await this.loadCurrentUser();
            return true;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },

    /**
     * Logout user
     */
    async logout() {
        await API.auth.logout();
        this.currentUser = null;
        window.location.href = '/pages/login.html';
    },

    /**
     * Load current user data
     */
    async loadCurrentUser() {
        try {
            this.currentUser = await API.auth.getCurrentUser();
            return this.currentUser;
        } catch (error) {
            console.error('Failed to load user:', error);
            this.logout();
        }
    },

    /**
     * Get current user
     */
    getUser() {
        return this.currentUser;
    },

    /**
     * Check if user has role
     */
    hasRole(role) {
        if (!this.currentUser) return false;
        return this.currentUser.role === role;
    },

    /**
     * Check if user has permission
     */
    hasPermission(permission) {
        if (!this.currentUser) return false;
        // TODO: Implement permission checking
        return true;
    },

    /**
     * Require authentication (redirect if not authenticated)
     */
    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/pages/login.html';
            return false;
        }
        return true;
    },

    /**
     * Initialize auth on page load
     */
    async init() {
        if (this.isAuthenticated()) {
            await this.loadCurrentUser();
        }
    }
};

export { Auth };
