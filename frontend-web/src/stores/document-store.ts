import { create } from "zustand";
import type { Document, DocumentType, PaginatedResponse } from "@/types";
import api from "@/lib/api";

interface DocumentState {
  documents: Document[];
  documentTypes: DocumentType[];
  total: number;
  isLoading: boolean;
  expiringDocs: Document[];

  fetchDocuments: (params?: Record<string, string | number>) => Promise<void>;
  fetchDocumentTypes: () => Promise<void>;
  fetchExpiring: (days?: number) => Promise<void>;
  uploadDocument: (formData: FormData) => Promise<Document>;
  deleteDocument: (id: string) => Promise<void>;
}

export const useDocumentStore = create<DocumentState>((set) => ({
  documents: [],
  documentTypes: [],
  total: 0,
  isLoading: false,
  expiringDocs: [],

  fetchDocuments: async (params) => {
    set({ isLoading: true });
    try {
      const res = await api.get<PaginatedResponse<Document>>("/api/v1/documents/", { params });
      set({ documents: res.data.data, total: res.data.total });
    } finally {
      set({ isLoading: false });
    }
  },

  fetchDocumentTypes: async () => {
    const res = await api.get<DocumentType[]>("/api/v1/documents/types");
    set({ documentTypes: res.data });
  },

  fetchExpiring: async (days = 90) => {
    const res = await api.get<Document[]>("/api/v1/documents/expiring", { params: { days } });
    set({ expiringDocs: res.data });
  },

  uploadDocument: async (formData) => {
    const res = await api.post<Document>("/api/v1/documents/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  },

  deleteDocument: async (id) => {
    await api.delete(`/api/v1/documents/${id}`);
  },
}));
