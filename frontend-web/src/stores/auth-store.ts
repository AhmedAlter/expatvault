import { create } from "zustand";
import type { User } from "@/types";
import api from "@/lib/api";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  login: (identifier: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; full_name: string; phone?: string; nationality?: string }) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  sendOtp: (channel?: string) => Promise<void>;
  verifyOtp: (code: string) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isLoading: false,
  isAuthenticated: !!localStorage.getItem("access_token"),

  login: async (identifier, password) => {
    set({ isLoading: true });
    try {
      const isEmail = identifier.includes("@");
      const payload = isEmail
        ? { email: identifier, password }
        : { email: identifier, password, phone: identifier };

      const res = await api.post("/api/v1/auth/login", {
        email: isEmail ? identifier : `${identifier}@phone.expatvault.local`,
        password,
      });
      localStorage.setItem("access_token", res.data.access_token);
      localStorage.setItem("refresh_token", res.data.refresh_token);
      set({ isAuthenticated: true });
      await get().fetchUser();
    } finally {
      set({ isLoading: false });
    }
  },

  register: async (data) => {
    set({ isLoading: true });
    try {
      await api.post("/api/v1/auth/register", data);
    } finally {
      set({ isLoading: false });
    }
  },

  logout: async () => {
    const refreshToken = localStorage.getItem("refresh_token");
    try {
      if (refreshToken) {
        await api.post("/api/v1/auth/logout", { refresh_token: refreshToken });
      }
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      set({ user: null, isAuthenticated: false });
    }
  },

  fetchUser: async () => {
    try {
      const res = await api.get("/api/v1/users/me");
      set({ user: res.data, isAuthenticated: true });
    } catch {
      set({ user: null, isAuthenticated: false });
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  },

  sendOtp: async (channel = "email") => {
    await api.post("/api/v1/auth/otp/send", { channel });
  },

  verifyOtp: async (code) => {
    await api.post("/api/v1/auth/otp/verify", { code });
    await get().fetchUser();
  },
}));
