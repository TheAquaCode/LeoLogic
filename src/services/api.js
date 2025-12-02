// src/services/api.js
const API_BASE_URL = 'http://localhost:5001/api';

class APIService {
  async fetchWithTimeout(url, options = {}, timeout = options.method === 'POST' ? 30000 : 3000) { 
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
        cache: 'no-cache', 
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

  async clearCache() {
    return this.request('/settings/clear-cache', {
      method: 'POST'
    });
  }

  // Watched Folders
  async getWatchedFolders() {
    const data = await this.request('/watched-folders');
    return Array.isArray(data) ? data : [];
  }

  async addWatchedFolder(folder) {
    return this.request('/watched-folders', {
      method: 'POST',
      body: JSON.stringify(folder),
    });
  }

  async deleteWatchedFolder(folderId) {
    return this.request(`/watched-folders/${folderId}`, {
      method: 'DELETE',
    });
  }

  async toggleFolderStatus(folderId) {
    return this.request(`/watched-folders/${folderId}/toggle`, {
      method: 'POST',
    });
  }

  async processFolderFiles(folderId) {
    return this.request(`/process-folder/${folderId}`, {
      method: 'POST',
    });
  }

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
    return Array.isArray(data) ? data : [];
  }

  async addCategory(category) {
    return this.request('/categories', {
      method: 'POST',
      body: JSON.stringify(category),
    });
  }

  async deleteCategory(categoryId) {
    return this.request(`/categories/${categoryId}`, {
      method: 'DELETE',
    });
  }

  async updateCategory(categoryId, updates) {
    return this.request(`/categories/${categoryId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
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