import httpx
from app.tasks.celery_app import celery_app
from app.database import get_supabase
from app.repositories.document_repo import DocumentRepository
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_document_ocr(self, document_id: str, user_id: str):
    try:
        db = get_supabase()
        doc_repo = DocumentRepository(db)
        doc = doc_repo.get_by_id(document_id, user_id)
        if not doc or not doc.get("file_path"):
            logger.warning(f"Document {document_id} not found or has no file")
            return

        # Get signed URL for the file
        signed = db.storage.from_("documents").create_signed_url(doc["file_path"], 3600)
        file_url = signed.get("signedURL") or signed.get("signedUrl")
        if not file_url:
            logger.error(f"Failed to get signed URL for {doc['file_path']}")
            return

        settings = get_settings()
        response = httpx.post(
            f"{settings.AI_SERVICE_URL}/api/process",
            json={"file_url": file_url, "document_id": document_id},
            timeout=120.0,
        )
        response.raise_for_status()
        result = response.json()

        update_data = {}
        if result.get("ocr_text"):
            update_data["ocr_text"] = result["ocr_text"]
        if result.get("classification"):
            update_data["ai_classification"] = result["classification"]
        if result.get("confidence"):
            update_data["ai_confidence"] = result["confidence"]
        if result.get("expiry_date") and not doc.get("expiry_date"):
            update_data["expiry_date"] = result["expiry_date"]
        if result.get("issue_date") and not doc.get("issue_date"):
            update_data["issue_date"] = result["issue_date"]

        if update_data:
            doc_repo.update(document_id, user_id, update_data)
            logger.info(f"OCR completed for document {document_id}")

    except Exception as exc:
        logger.error(f"OCR task failed for {document_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)
