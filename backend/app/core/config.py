import json
import re
from functools import lru_cache
from typing import List
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "AI Academic Assistant API"
    api_v1_prefix: str = "/api/v1"
    backend_cors_origins: str = "http://localhost:5173"
    backend_cors_origin_regex: str = ""

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_interactions_table: str = "interactions"
    supabase_students_table: str = "students"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def backend_cors_origin_list(self) -> List[str]:
        def clean_origin(origin: str) -> str:
            origin_value = origin.strip().strip('"').strip("'")
            if origin_value.endswith("/") and origin_value != "*":
                origin_value = origin_value[:-1]
            return origin_value

        value = self.backend_cors_origins
        if isinstance(value, list):
            return [clean_origin(str(origin)) for origin in value if str(origin).strip()]
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
                return [clean_origin(str(origin)) for origin in parsed if str(origin).strip()]

        return [clean_origin(origin) for origin in normalized.split(",") if origin.strip()]

    @property
    def backend_cors_origin_regex_value(self) -> str | None:
        normalized = self.backend_cors_origin_regex.strip()
        if normalized:
            return normalized
        return self._derive_vercel_origin_regex(self.backend_cors_origin_list)

    @staticmethod
    def _derive_vercel_origin_regex(origins: List[str]) -> str | None:
        for origin in origins:
            parsed = urlparse(origin)
            hostname = (parsed.hostname or "").lower()
            if not hostname.endswith(".vercel.app"):
                continue

            subdomain = hostname[: -len(".vercel.app")]
            match = re.match(r"^(?P<base>.+)-(?P<suffix>[a-z0-9]{6,})$", subdomain)
            if match and any(char.isdigit() for char in match.group("suffix")):
                base = match.group("base")
            else:
                base = subdomain

            escaped = re.escape(base)
            return rf"^https://{escaped}(?:-[a-zA-Z0-9-]+)?\.vercel\.app$"

        return None


@lru_cache
def get_settings() -> Settings:
    return Settings()
