/**
 * Safe localStorage wrapper with JSON serialization
 */
export const storage = {
  get<T>(key: string, defaultValue?: T): T | null {
    if (typeof window === "undefined") return defaultValue || null;

    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue || null;
    } catch (error) {
      console.error(`Error reading from localStorage key "${key}":`, error);
      return defaultValue || null;
    }
  },

  set(key: string, value: any): void {
    if (typeof window === "undefined") return;

    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Error writing to localStorage key "${key}":`, error);
    }
  },

  remove(key: string): void {
    if (typeof window === "undefined") return;

    try {
      window.localStorage.removeItem(key);
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error);
    }
  },

  clear(): void {
    if (typeof window === "undefined") return;

    try {
      window.localStorage.clear();
    } catch (error) {
      console.error("Error clearing localStorage:", error);
    }
  },
};

/**
 * Session storage wrapper
 */
export const sessionStorage = {
  get<T>(key: string, defaultValue?: T): T | null {
    if (typeof window === "undefined") return defaultValue || null;

    try {
      const item = window.sessionStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue || null;
    } catch (error) {
      console.error(`Error reading from sessionStorage key "${key}":`, error);
      return defaultValue || null;
    }
  },

  set(key: string, value: any): void {
    if (typeof window === "undefined") return;

    try {
      window.sessionStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Error writing to sessionStorage key "${key}":`, error);
    }
  },

  remove(key: string): void {
    if (typeof window === "undefined") return;

    try {
      window.sessionStorage.removeItem(key);
    } catch (error) {
      console.error(`Error removing sessionStorage key "${key}":`, error);
    }
  },

  clear(): void {
    if (typeof window === "undefined") return;

    try {
      window.sessionStorage.clear();
    } catch (error) {
      console.error("Error clearing sessionStorage:", error);
    }
  },
};
