"""A thin, typed wrapper over the Beaconless REST API.

See https://beaconless-api.pages.dev/api-reference for the full reference:
authentication, GET /events, POST /ingest, error codes.
"""
from __future__ import annotations

import os
import time
from typing import Any, Dict, Iterator, List, Optional

import requests

DEFAULT_BASE_URL = "https://api.beaconless.dev/v2"


class BeaconlessError(Exception):
    """Raised when the API returns a non-2xx status."""

    def __init__(self, status: int, body: Any) -> None:
        super().__init__(f"Beaconless API error {status}: {body}")
        self.status = status
        self.body = body


class Client:
    """Client for the Beaconless telemetry API.

    Args:
        api_key: project API key. Falls back to ``$BEACONLESS_API_KEY``.
        base_url: override the API base (e.g. for a self-hosted deployment).
        max_retries: retries on 429 / 5xx with exponential backoff.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        max_retries: int = 3,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.environ.get("BEACONLESS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No API key. Pass api_key= or set BEACONLESS_API_KEY."
            )
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "beaconless-python/0.1.0",
                "Accept": "application/json",
            }
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{path}"
        for attempt in range(self.max_retries + 1):
            resp = self._session.request(
                method, url, timeout=self.timeout, **kwargs
            )
            if resp.status_code == 429 or resp.status_code >= 500:
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
            if not resp.ok:
                try:
                    body = resp.json()
                except ValueError:
                    body = resp.text
                raise BeaconlessError(resp.status_code, body)
            return resp.json() if resp.content else None
        raise BeaconlessError(resp.status_code, "retries exhausted")

    def events(
        self, limit: int = 50, cursor: Optional[str] = None
    ) -> Iterator[Dict[str, Any]]:
        """Yield recent telemetry events, following cursor pagination."""
        while True:
            params: Dict[str, Any] = {"limit": limit}
            if cursor:
                params["cursor"] = cursor
            page = self._request("GET", "/events", params=params)
            for event in page.get("data", []):
                yield event
            cursor = page.get("next_cursor")
            if not cursor:
                return

    def ingest(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Push a batch of event objects. Returns the ingest receipt."""
        return self._request("POST", "/ingest", json={"events": events})
