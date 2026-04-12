import json
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "AI Academic Assistant API"
    api_v1_prefix: str = "/api/v1"
    backend_cors_origins: str = "http://localhost:5173"

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_interactions_table: str = "interactions"
    supabase_students_table: str = "students"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def backend_cors_origin_list(self) -> List[str]:
        value = self.backend_cors_origins
        if isinstance(value, list):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        if not isinstance(value, str):
            return []

        normalized = value.strip()
        if not normalized:
            return []

        if normalized.startswith("["):
            try:
                parsed = json.loads(normalized)
            except json.JSONDecodeError:
                parsed = None

            if isinstance(parsed, list):
                return [str(origin).strip() for origin in parsed if str(origin).strip()]

        return [origin.strip() for origin in normalized.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
