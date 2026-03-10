from supabase import Client


class SessionRepository:
    def __init__(self, db: Client):
        self.db = db

    def create(self, data: dict) -> dict:
        result = self.db.table("sessions").insert(data).execute()
        return result.data[0]

    def get_by_refresh_token(self, token: str) -> dict | None:
        result = (
            self.db.table("sessions")
            .select("*")
            .eq("refresh_token", token)
            .maybe_single()
            .execute()
        )
        return result.data if result else None

    def delete_by_refresh_token(self, token: str) -> bool:
        self.db.table("sessions").delete().eq("refresh_token", token).execute()
        return True

    def delete_all_for_user(self, user_id: str) -> bool:
        self.db.table("sessions").delete().eq("user_id", user_id).execute()
        return True
