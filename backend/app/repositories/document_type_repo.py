from supabase import Client


class DocumentTypeRepository:
    def __init__(self, db: Client):
        self.db = db

    def get_all(self) -> list[dict]:
        result = self.db.table("document_types").select("*").order("name").execute()
        return result.data

    def get_by_id(self, type_id: int) -> dict | None:
        result = self.db.table("document_types").select("*").eq("id", type_id).maybe_single().execute()
        return result.data if result else None

    def get_by_name(self, name: str) -> dict | None:
        result = self.db.table("document_types").select("*").eq("name", name).maybe_single().execute()
        return result.data if result else None
