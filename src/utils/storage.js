const STORAGE_KEYS = {
  WATCHED_FOLDERS: 'filephile_watched_folders',
  CATEGORIES: 'filephile_categories'
};

export const loadFromStorage = (key) => {
  try {
    const data = localStorage.getItem(STORAGE_KEYS[key]);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error(`Error loading ${key} from storage:`, error);
    return null;
  }
};

export const saveToStorage = (key, data) => {
  try {
    localStorage.setItem(STORAGE_KEYS[key], JSON.stringify(data));
  } catch (error) {
    console.error(`Error saving ${key} to storage:`, error);
  }
};

export default {
  STORAGE_KEYS,
  loadFromStorage,
  saveToStorage
};