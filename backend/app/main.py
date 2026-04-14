from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import ai, assistant, health, students
from app.core.config import get_settings

settings = get_settings()

print(f"Backend CORS origins: {settings.backend_cors_origin_list}")
print(f"Backend CORS origin regex: {settings.backend_cors_origin_regex_value}")
print(f"API prefix: {settings.api_v1_prefix}")

app = FastAPI(title=settings.project_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origin_list,
    allow_origin_regex=settings.backend_cors_origin_regex_value,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "service": "ai-academic-assistant-backend"}

app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(assistant.router, prefix=settings.api_v1_prefix)
app.include_router(students.router, prefix=settings.api_v1_prefix)
app.include_router(ai.router, prefix=settings.api_v1_prefix)
