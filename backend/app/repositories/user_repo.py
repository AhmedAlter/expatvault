from supabase import Client


class UserRepository:
    def __init__(self, db: Client):
        self.db = db

    def create(self, data: dict) -> dict:
        result = self.db.table("users").insert(data).execute()
        return result.data[0]

    def get_by_id(self, user_id: str) -> dict | None:
        result = self.db.table("users").select("*").eq("id", user_id).maybe_single().execute()
        return result.data if result else None

    def get_by_email(self, email: str) -> dict | None:
        result = self.db.table("users").select("*").eq("email", email).maybe_single().execute()
        return result.data if result else None

    def get_by_phone(self, phone: str) -> dict | None:
        result = self.db.table("users").select("*").eq("phone", phone).maybe_single().execute()
        return result.data if result else None

    def update(self, user_id: str, data: dict) -> dict | None:
        result = self.db.table("users").update(data).eq("id", user_id).execute()
        return result.data[0] if result.data else None

    def delete(self, user_id: str) -> bool:
        self.db.table("users").delete().eq("id", user_id).execute()
        return True
