const STORAGE_KEYS = {
  WATCHED_FOLDERS: 'filephile_watched_folders',
  CATEGORIES: 'filephile_categories',
  QUICK_SORT_EXPANDED: 'filephile_quick_sort_expanded'
};

export const loadFromStorage = (key, defaultValue = null) => {
  try {
    // Handle both direct keys and STORAGE_KEYS references
    const storageKey = STORAGE_KEYS[key] || key;
    const data = localStorage.getItem(storageKey);
    return data ? JSON.parse(data) : defaultValue;
  } catch (error) {
    console.error(`Error loading ${key} from storage:`, error);
    return defaultValue;
  }
};

export const saveToStorage = (key, data) => {
  try {
    // Handle both direct keys and STORAGE_KEYS references
    const storageKey = STORAGE_KEYS[key] || key;
    localStorage.setItem(storageKey, JSON.stringify(data));
  } catch (error) {
    console.error(`Error saving ${key} to storage:`, error);
  }
};

export default {
  STORAGE_KEYS,
  loadFromStorage,
  saveToStorage
};