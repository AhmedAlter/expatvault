from supabase import Client


class NotificationRepository:
    def __init__(self, db: Client):
        self.db = db

    def create(self, data: dict) -> dict:
        result = self.db.table("notifications").insert(data).execute()
        return result.data[0]

    def list_for_user(self, user_id: str, page: int = 1, per_page: int = 20) -> tuple[list[dict], int]:
        offset = (page - 1) * per_page
        result = (
            self.db.table("notifications")
            .select("*", count="exact")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .range(offset, offset + per_page - 1)
            .execute()
        )
        return result.data, result.count or 0

    def unread_count(self, user_id: str) -> int:
        result = (
            self.db.table("notifications")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("is_read", False)
            .execute()
        )
        return result.count or 0

    def mark_read(self, notif_id: str, user_id: str) -> dict | None:
        from datetime import datetime, timezone

        result = (
            self.db.table("notifications")
            .update({"is_read": True, "read_at": datetime.now(timezone.utc).isoformat()})
            .eq("id", notif_id)
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def mark_all_read(self, user_id: str) -> int:
        from datetime import datetime, timezone

        result = (
            self.db.table("notifications")
            .update({"is_read": True, "read_at": datetime.now(timezone.utc).isoformat()})
            .eq("user_id", user_id)
            .eq("is_read", False)
            .execute()
        )
        return len(result.data) if result.data else 0
