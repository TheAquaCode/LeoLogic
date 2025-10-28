// src/services/api.js
// API service for communicating with the backend

const API_BASE_URL = 'http://localhost:5001/api';

class APIService {
  async fetchWithTimeout(url, options = {}, timeout = 10000) {
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

  // Watched Folders
  async getWatchedFolders() {
    const data = await this.request('/watched-folders');
    // Accept both array or { folders: [...] }
    return Array.isArray(data) ? data : data.folders || [];
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

  // Categories
  async getCategories() {
    const data = await this.request('/categories');
    // Accept both array or { categories: [...] }
    return Array.isArray(data) ? data : data.categories || [];
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
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }

  // Statistics
  async getStats() {
    return this.request('/stats');
  }
}

export default new APIService();
