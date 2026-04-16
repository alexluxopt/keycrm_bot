from __future__ import annotations

from typing import Any

import httpx

from app.config import Settings


class KeyCRMError(RuntimeError):
    pass


class KeyCRMClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def fetch_orders(self) -> list[dict[str, Any]]:
        orders: list[dict[str, Any]] = []
        url = f"{self._settings.keycrm_base_url}/order"
        params = {
            "limit": str(self._settings.keycrm_page_size),
            "sort": self._settings.keycrm_sort,
            "filter[status_id]": str(self._settings.keycrm_status_id),
            "include": self._settings.keycrm_include,
        }
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self._settings.keycrm_api_token}",
        }

        try:
            async with httpx.AsyncClient(
                headers=headers,
                timeout=self._settings.keycrm_request_timeout_seconds,
            ) as client:
                for page in range(1, self._settings.keycrm_max_pages + 1):
                    response = await client.get(url, params={**params, "page": str(page)})
                    response.raise_for_status()
                    payload = response.json()
                    root = self._normalize_root(payload)
                    data = root.get("data", [])

                    if not isinstance(data, list):
                        raise KeyCRMError("KeyCRM response does not contain a valid data array.")

                    if not data:
                        break

                    orders.extend(item for item in data if isinstance(item, dict))

                    current_page = int(root.get("current_page", page))
                    last_page = root.get("last_page")
                    next_page_url = root.get("next_page_url")

                    if last_page is not None and current_page >= int(last_page):
                        break

                    if next_page_url in (None, "") and len(data) < self._settings.keycrm_page_size:
                        break
                else:
                    raise KeyCRMError(
                        f"Pagination limit exceeded ({self._settings.keycrm_max_pages} pages)."
                    )
        except httpx.HTTPError as error:
            raise KeyCRMError(f"KeyCRM request failed: {error}") from error

        return orders

    @staticmethod
    def _normalize_root(payload: Any) -> dict[str, Any]:
        if isinstance(payload, list):
            if not payload or not isinstance(payload[0], dict):
                raise KeyCRMError("Unexpected list payload returned by KeyCRM.")
            return payload[0]

        if not isinstance(payload, dict):
            raise KeyCRMError("Unexpected payload returned by KeyCRM.")

        return payload
