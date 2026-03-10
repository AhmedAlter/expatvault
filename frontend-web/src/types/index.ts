export interface User {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  nationality: string | null;
  emirates_id_number: string | null;
  subscription_tier: "free" | "individual_pro" | "family";
  is_active: boolean;
  is_verified: boolean;
  avatar_url: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface DocumentType {
  id: number;
  name: string;
  display_name: string;
  category: string | null;
  typical_validity_days: number | null;
  renewal_url: string | null;
  renewal_lead_days: number | null;
  dependency_chain: string[] | null;
}

export interface Document {
  id: string;
  user_id: string;
  family_member_id: string | null;
  document_type_id: number;
  title: string;
  file_path: string | null;
  file_size_bytes: number | null;
  mime_type: string | null;
  issue_date: string | null;
  expiry_date: string | null;
  status: "active" | "expiring_soon" | "expired" | "renewed";
  ocr_text: string | null;
  ai_classification: string | null;
  ai_confidence: number | null;
  metadata: Record<string, unknown> | null;
  is_archived: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface Reminder {
  id: string;
  document_id: string;
  user_id: string;
  remind_at: string;
  days_before: number | null;
  channel: "in_app" | "email" | "sms";
  status: "pending" | "sent" | "acknowledged" | "snoozed";
  sent_at: string | null;
  snoozed_until: string | null;
  created_at: string;
}

export interface Notification {
  id: string;
  user_id: string;
  reminder_id: string | null;
  title: string;
  body: string;
  channel: string;
  is_read: boolean;
  read_at: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface FamilyMember {
  id: string;
  user_id: string;
  full_name: string;
  relationship: "spouse" | "child" | "parent" | "sibling" | "other";
  date_of_birth: string | null;
  nationality: string | null;
  emirates_id_number: string | null;
  avatar_url: string | null;
  created_at: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
}
