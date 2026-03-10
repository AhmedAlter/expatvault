from supabase import Client


class DocumentRepository:
    def __init__(self, db: Client):
        self.db = db

    def create(self, data: dict) -> dict:
        result = self.db.table("documents").insert(data).execute()
        return result.data[0]

    def get_by_id(self, doc_id: str, user_id: str) -> dict | None:
        result = (
            self.db.table("documents")
            .select("*")
            .eq("id", doc_id)
            .eq("user_id", user_id)
            .eq("is_archived", False)
            .maybe_single()
            .execute()
        )
        return result.data if result else None

    def list_for_user(
        self,
        user_id: str,
        status: str | None = None,
        document_type_id: int | None = None,
        family_member_id: str | None = None,
        search: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[dict], int]:
        query = (
            self.db.table("documents")
            .select("*", count="exact")
            .eq("user_id", user_id)
            .eq("is_archived", False)
        )
        if status:
            query = query.eq("status", status)
        if document_type_id:
            query = query.eq("document_type_id", document_type_id)
        if family_member_id:
            query = query.eq("family_member_id", family_member_id)
        if search:
            query = query.ilike("title", f"%{search}%")

        offset = (page - 1) * per_page
        query = query.order("created_at", desc=True).range(offset, offset + per_page - 1)
        result = query.execute()
        return result.data, result.count or 0

    def update(self, doc_id: str, user_id: str, data: dict) -> dict | None:
        result = (
            self.db.table("documents")
            .update(data)
            .eq("id", doc_id)
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def archive(self, doc_id: str, user_id: str) -> bool:
        result = (
            self.db.table("documents")
            .update({"is_archived": True})
            .eq("id", doc_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(result.data)

    def get_expiring(self, user_id: str, within_days: int) -> list[dict]:
        from datetime import datetime, timedelta, timezone

        cutoff = (datetime.now(timezone.utc) + timedelta(days=within_days)).isoformat()
        result = (
            self.db.table("documents")
            .select("*")
            .eq("user_id", user_id)
            .eq("is_archived", False)
            .not_.is_("expiry_date", "null")
            .lte("expiry_date", cutoff)
            .gte("expiry_date", datetime.now(timezone.utc).isoformat())
            .order("expiry_date")
            .execute()
        )
        return result.data

    def get_user_docs_by_type(self, user_id: str) -> list[dict]:
        result = (
            self.db.table("documents")
            .select("*, document_types(name, dependency_chain)")
            .eq("user_id", user_id)
            .eq("is_archived", False)
            .execute()
        )
        return result.data

    def count_for_user(self, user_id: str) -> int:
        result = (
            self.db.table("documents")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("is_archived", False)
            .execute()
        )
        return result.count or 0
