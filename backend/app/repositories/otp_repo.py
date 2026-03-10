from supabase import Client


class OTPRepository:
    def __init__(self, db: Client):
        self.db = db

    def create(self, data: dict) -> dict:
        result = self.db.table("otp_codes").insert(data).execute()
        return result.data[0]

    def get_latest_for_user(self, user_id: str, channel: str) -> dict | None:
        result = (
            self.db.table("otp_codes")
            .select("*")
            .eq("user_id", user_id)
            .eq("channel", channel)
            .eq("verified", False)
            .order("created_at", desc=True)
            .limit(1)
            .maybe_single()
            .execute()
        )
        return result.data if result else None

    def increment_attempts(self, otp_id: str, current_attempts: int) -> None:
        self.db.table("otp_codes").update({"attempts": current_attempts + 1}).eq("id", otp_id).execute()

    def mark_verified(self, otp_id: str) -> None:
        self.db.table("otp_codes").update({"verified": True}).eq("id", otp_id).execute()

    def count_recent(self, user_id: str, channel: str, since: str) -> int:
        result = (
            self.db.table("otp_codes")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("channel", channel)
            .gte("created_at", since)
            .execute()
        )
        return result.count or 0
