from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import auth, users, documents, reminders, notifications, family

settings = get_settings()

app = FastAPI(
    title="ExpatVault API",
    description="Smart Document Lifecycle Manager for UAE Expats",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(reminders.router)
app.include_router(notifications.router)
app.include_router(family.router)


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "env": settings.APP_ENV}
