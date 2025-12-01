// src/services/api.js
// API service for communicating with the backend

const API_BASE_URL = 'http://localhost:5001/api';

class APIService {
  async fetchWithTimeout(url, options = {}, timeout = options.method === 'POST' ? 30000 : 3000) { // 30 seconds for POST requests
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        cache: 'no-cache', // Don't cache API responses
      });
      clearTimeout(id);
      return response;
    } catch (error) {
      clearTimeout(id);
      throw error;
    }
  }

  async request(endpoint, options = {}) {
    try {
      const response = await this.fetchWithTimeout(
        `${API_BASE_URL}${endpoint}`,
        options
      );

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          error: 'Unknown error',
        }));
        throw new Error(error.error || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Health check
  async checkHealth() {
    return this.request('/health');
  }

  // Settings
  async getSettings() {
    return this.request('/settings');
  }

  async updateSettings(settings) {
    return this.request('/settings', {
      method: 'POST',
      body: JSON.stringify(settings),
    });
  }

  // Watched Folders
  async getWatchedFolders() {
    const data = await this.request('/watched-folders');
    // Backend now returns array directly
    return Array.isArray(data) ? data : [];
  }

  async addWatchedFolder(folder) {
    const data = await this.request('/watched-folders', {
      method: 'POST',
      body: JSON.stringify(folder),
    });
    // Backend returns the folder directly
    return data;
  }

  async deleteWatchedFolder(folderId) {
    return this.request(`/watched-folders/${folderId}`, {
      method: 'DELETE',
    });
  }

  async toggleFolderStatus(folderId) {
    const data = await this.request(`/watched-folders/${folderId}/toggle`, {
      method: 'POST',
    });
    // Backend returns the folder directly
    return data;
  }

  async processFolderFiles(folderId) {
    return this.request(`/process-folder/${folderId}`, {
      method: 'POST',
    });
  }

  // Start processing folder in background (returns accepted) and poll progress separately
  async startProcessFolder(folderId) {
    return this.request(`/process-folder/${folderId}`, {
      method: 'POST'
    });
  }

  async getProcessProgress(folderId) {
    return this.request(`/process-folder/${folderId}/progress`);
  }

  // Categories
  async getCategories() {
    const data = await this.request('/categories');
    // Backend now returns array directly
    return Array.isArray(data) ? data : [];
  }

  async addCategory(category) {
    const data = await this.request('/categories', {
      method: 'POST',
      body: JSON.stringify(category),
    });
    // Backend returns the category directly
    return data;
  }

  async deleteCategory(categoryId) {
    return this.request(`/categories/${categoryId}`, {
      method: 'DELETE',
    });
  }

  async updateCategory(categoryId, updates) {
    const data = await this.request(`/categories/${categoryId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
    return data;
  }

  // Statistics
  async getStats() {
    return this.request('/stats');
  }

  // History
  async getHistory(limit = 100) {
    return this.request(`/history?limit=${limit}`);
  }

  async getHistoryStats() {
    return this.request('/history/stats');
  }

  async undoMovement(movementId) {
    return this.request(`/history/${movementId}/undo`, {
      method: 'POST',
    });
  }

  async openFileLocation(movementId) {
    return this.request(`/history/${movementId}/open`, {
      method: 'POST',
    });
  }
}

export default new APIService();