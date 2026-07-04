from __future__ import annotations

import asyncio
from typing import Any

import httpx

from app.config import Settings
from app.keycrm import KeyCRMClient, KeyCRMError


def make_settings(**overrides: Any) -> Settings:
    values = {
        "telegram_bot_token": "telegram-token",
        "keycrm_api_token": "keycrm-token",
        "keycrm_base_url": "https://openapi.keycrm.test/v1",
        "keycrm_status_id": 2,
        "keycrm_page_size": 2,
        "keycrm_sort": "id",
        "keycrm_include": "products.offer",
        "keycrm_max_pages": 5,
        "keycrm_request_timeout_seconds": 5.0,
        "telegram_target_chat_id": None,
        "log_level": "INFO",
    }
    values.update(overrides)
    return Settings(**values)


def test_fetch_orders_follows_keycrm_pagination() -> None:
    seen_pages: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        page = request.url.params["page"]
        seen_pages.append(page)
        assert request.headers["authorization"] == "Bearer keycrm-token"
        assert request.url.params["filter[status_id]"] == "2"
        assert request.url.params["include"] == "products.offer"

        if page == "1":
            return httpx.Response(
                200,
                json={
                    "data": [{"id": 1}, {"id": 2}],
                    "current_page": 1,
                    "last_page": 2,
                    "next_page_url": "https://openapi.keycrm.test/v1/order?page=2",
                },
            )

        return httpx.Response(
            200,
            json={
                "data": [{"id": 3}],
                "current_page": 2,
                "last_page": 2,
                "next_page_url": None,
            },
        )

    client = KeyCRMClient(make_settings(), transport=httpx.MockTransport(handler))

    orders = asyncio.run(client.fetch_orders())

    assert orders == [{"id": 1}, {"id": 2}, {"id": 3}]
    assert seen_pages == ["1", "2"]


def test_fetch_orders_wraps_http_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"message": "server error"})

    client = KeyCRMClient(make_settings(), transport=httpx.MockTransport(handler))

    try:
        asyncio.run(client.fetch_orders())
    except KeyCRMError as error:
        assert "KeyCRM request failed" in str(error)
    else:  # pragma: no cover
        raise AssertionError("Expected KeyCRMError")
