from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import ai, assistant, health, students
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.project_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(assistant.router, prefix=settings.api_v1_prefix)
app.include_router(students.router)
app.include_router(ai.router)
