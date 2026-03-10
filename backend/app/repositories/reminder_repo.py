from supabase import Client


class ReminderRepository:
    def __init__(self, db: Client):
        self.db = db

    def create(self, data: dict) -> dict:
        result = self.db.table("reminders").insert(data).execute()
        return result.data[0]

    def get_by_id(self, reminder_id: str, user_id: str) -> dict | None:
        result = (
            self.db.table("reminders")
            .select("*")
            .eq("id", reminder_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        return result.data if result else None

    def list_for_user(self, user_id: str, status: str | None = None) -> list[dict]:
        query = self.db.table("reminders").select("*").eq("user_id", user_id)
        if status:
            query = query.eq("status", status)
        result = query.order("remind_at").execute()
        return result.data

    def update(self, reminder_id: str, user_id: str, data: dict) -> dict | None:
        result = (
            self.db.table("reminders")
            .update(data)
            .eq("id", reminder_id)
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def delete(self, reminder_id: str, user_id: str) -> bool:
        self.db.table("reminders").delete().eq("id", reminder_id).eq("user_id", user_id).execute()
        return True

    def get_pending_due(self, before: str) -> list[dict]:
        result = (
            self.db.table("reminders")
            .select("*, documents(title, expiry_date, user_id)")
            .eq("status", "pending")
            .lte("remind_at", before)
            .execute()
        )
        return result.data

    def create_bulk(self, items: list[dict]) -> list[dict]:
        if not items:
            return []
        result = self.db.table("reminders").insert(items).execute()
        return result.data
