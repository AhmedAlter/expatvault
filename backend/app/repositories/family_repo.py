from supabase import Client


class FamilyRepository:
    def __init__(self, db: Client):
        self.db = db

    def create(self, data: dict) -> dict:
        result = self.db.table("family_members").insert(data).execute()
        return result.data[0]

    def get_by_id(self, member_id: str, user_id: str) -> dict | None:
        result = (
            self.db.table("family_members")
            .select("*")
            .eq("id", member_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        return result.data if result else None

    def list_for_user(self, user_id: str) -> list[dict]:
        result = (
            self.db.table("family_members")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at")
            .execute()
        )
        return result.data

    def update(self, member_id: str, user_id: str, data: dict) -> dict | None:
        result = (
            self.db.table("family_members")
            .update(data)
            .eq("id", member_id)
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def delete(self, member_id: str, user_id: str) -> bool:
        self.db.table("family_members").delete().eq("id", member_id).eq("user_id", user_id).execute()
        return True

    def count_for_user(self, user_id: str) -> int:
        result = (
            self.db.table("family_members")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .execute()
        )
        return result.count or 0
