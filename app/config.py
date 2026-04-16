from __future__ import annotations

import os
from dataclasses import dataclass


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _get_int(name: str, default: int | None = None) -> int | None:
    value = os.getenv(name, "").strip()
    if not value:
        return default
    return int(value)


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name, "").strip()
    if not value:
        return default
    return float(value)


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    keycrm_api_token: str
    keycrm_base_url: str
    keycrm_status_id: int
    keycrm_page_size: int
    keycrm_sort: str
    keycrm_include: str
    keycrm_max_pages: int
    keycrm_request_timeout_seconds: float
    telegram_target_chat_id: int | None
    log_level: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            telegram_bot_token=_require_env("TELEGRAM_BOT_TOKEN"),
            keycrm_api_token=_require_env("KEYCRM_API_TOKEN"),
            keycrm_base_url=os.getenv("KEYCRM_BASE_URL", "https://openapi.keycrm.app/v1").rstrip("/"),
            keycrm_status_id=_get_int("KEYCRM_STATUS_ID", 2) or 2,
            keycrm_page_size=_get_int("KEYCRM_PAGE_SIZE", 50) or 50,
            keycrm_sort=os.getenv("KEYCRM_SORT", "id").strip() or "id",
            keycrm_include=os.getenv("KEYCRM_INCLUDE", "products.offer").strip() or "products.offer",
            keycrm_max_pages=_get_int("KEYCRM_MAX_PAGES", 100) or 100,
            keycrm_request_timeout_seconds=_get_float("KEYCRM_REQUEST_TIMEOUT_SECONDS", 30.0),
            telegram_target_chat_id=_get_int("TELEGRAM_TARGET_CHAT_ID"),
            log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper() or "INFO",
        )
