import { defineStore } from "pinia";
import { ref, computed } from "vue";

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: "info" | "success" | "warning" | "error";
  read: boolean;
  createdAt: Date;
  actionUrl?: string;
}

/**
 * Notification store
 * Manages in-app notifications
 */
export const useNotificationStore = defineStore("notification", () => {
  const notifications = ref<Notification[]>([]);
  const maxNotifications = 50;

  const unreadCount = computed(() => {
    return notifications.value.filter((n) => !n.read).length;
  });

  const unreadNotifications = computed(() => {
    return notifications.value.filter((n) => !n.read);
  });

  function addNotification(notification: Omit<Notification, "id" | "createdAt" | "read">) {
    const newNotification: Notification = {
      id: crypto.randomUUID(),
      ...notification,
      read: false,
      createdAt: new Date(),
    };

    notifications.value.unshift(newNotification);

    // Keep only the most recent notifications
    if (notifications.value.length > maxNotifications) {
      notifications.value = notifications.value.slice(0, maxNotifications);
    }

    return newNotification;
  }

  function markAsRead(notificationId: string) {
    const notification = notifications.value.find((n) => n.id === notificationId);
    if (notification) {
      notification.read = true;
    }
  }

  function markAllAsRead() {
    notifications.value.forEach((n) => {
      n.read = true;
    });
  }

  function removeNotification(notificationId: string) {
    const index = notifications.value.findIndex((n) => n.id === notificationId);
    if (index !== -1) {
      notifications.value.splice(index, 1);
    }
  }

  function clearAll() {
    notifications.value = [];
  }

  function clearRead() {
    notifications.value = notifications.value.filter((n) => !n.read);
  }

  // Toast-like helpers
  function success(title: string, message: string) {
    return addNotification({ title, message, type: "success" });
  }

  function error(title: string, message: string) {
    return addNotification({ title, message, type: "error" });
  }

  function warning(title: string, message: string) {
    return addNotification({ title, message, type: "warning" });
  }

  function info(title: string, message: string) {
    return addNotification({ title, message, type: "info" });
  }

  return {
    notifications,
    unreadCount,
    unreadNotifications,
    addNotification,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll,
    clearRead,
    success,
    error,
    warning,
    info,
  };
});
