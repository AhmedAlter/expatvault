import { create } from "zustand";
import type { Notification } from "@/types";
import api from "@/lib/api";

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;

  fetchNotifications: (page?: number) => Promise<void>;
  fetchUnreadCount: () => Promise<void>;
  markRead: (id: string) => Promise<void>;
  markAllRead: () => Promise<void>;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  unreadCount: 0,
  isLoading: false,

  fetchNotifications: async (page = 1) => {
    set({ isLoading: true });
    try {
      const res = await api.get("/api/v1/notifications/", { params: { page } });
      set({ notifications: res.data.data });
    } finally {
      set({ isLoading: false });
    }
  },

  fetchUnreadCount: async () => {
    const res = await api.get("/api/v1/notifications/unread-count");
    set({ unreadCount: res.data.count });
  },

  markRead: async (id) => {
    await api.patch(`/api/v1/notifications/${id}/read`);
    set((s) => ({
      notifications: s.notifications.map((n) => (n.id === id ? { ...n, is_read: true } : n)),
      unreadCount: Math.max(0, s.unreadCount - 1),
    }));
  },

  markAllRead: async () => {
    await api.post("/api/v1/notifications/read-all");
    set((s) => ({
      notifications: s.notifications.map((n) => ({ ...n, is_read: true })),
      unreadCount: 0,
    }));
  },
}));
