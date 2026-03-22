"""
LMS API client for fetching data from the backend.

All HTTP requests to the LMS backend go through this client.
Handlers call these functions — they don't make HTTP requests directly.

This client supports both sync (for --test mode) and async (for Telegram) usage.
"""

import httpx
import logging
from typing import Any

logger = logging.getLogger(__name__)


class LMSAPIClient:
    """Client for interacting with the LMS backend API."""

    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the API client.

        Args:
            base_url: Base URL of the LMS backend (e.g., http://localhost:42002)
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        # Use async client but we'll wrap sync calls appropriately
        self._async_client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0,
        )
        # Sync client for --test mode
        self._sync_client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0,
        )

    def get_items_sync(self) -> list[dict[str, Any]]:
        """
        Fetch all items (labs and tasks) from the backend (sync version).

        Returns:
            List of items (labs and tasks)

        Raises:
            httpx.RequestError: If the request fails
        """
        response = self._sync_client.get("/items/")
        response.raise_for_status()
        return response.json()

    def get_learners_sync(self) -> list[dict[str, Any]]:
        """
        Fetch all enrolled learners (sync version).

        Returns:
            List of learner records
        """
        response = self._sync_client.get("/learners/")
        response.raise_for_status()
        return response.json()

    def get_scores_sync(self, lab: str) -> list[dict[str, Any]]:
        """
        Fetch score distribution for a specific lab (sync version).

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            Score distribution data
        """
        response = self._sync_client.get("/analytics/scores", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_pass_rates_sync(self, lab: str) -> list[dict[str, Any]]:
        """
        Fetch per-task pass rates for a specific lab (sync version).

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            List of pass rate records per task
        """
        response = self._sync_client.get("/analytics/pass-rates", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_timeline_sync(self, lab: str) -> list[dict[str, Any]]:
        """
        Fetch submission timeline for a specific lab (sync version).

        Args:
            lab: Lab identifier

        Returns:
            Timeline data showing submissions per day
        """
        response = self._sync_client.get("/analytics/timeline", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_groups_sync(self, lab: str) -> list[dict[str, Any]]:
        """
        Fetch per-group performance for a specific lab (sync version).

        Args:
            lab: Lab identifier

        Returns:
            Group performance data
        """
        response = self._sync_client.get("/analytics/groups", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_top_learners_sync(
        self, lab: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """
        Fetch top learners for a specific lab (sync version).

        Args:
            lab: Lab identifier
            limit: Maximum number of learners to return

        Returns:
            List of top learner records
        """
        response = self._sync_client.get(
            "/analytics/top-learners", params={"lab": lab, "limit": limit}
        )
        response.raise_for_status()
        return response.json()

    def get_completion_rate_sync(self, lab: str) -> dict[str, Any]:
        """
        Fetch completion rate for a specific lab (sync version).

        Args:
            lab: Lab identifier

        Returns:
            Completion rate data
        """
        response = self._sync_client.get(
            "/analytics/completion-rate", params={"lab": lab}
        )
        response.raise_for_status()
        return response.json()

    def sync_pipeline_sync(self) -> dict[str, Any]:
        """
        Trigger ETL sync on the backend (sync version).

        Returns:
            Sync result data
        """
        response = self._sync_client.post("/pipeline/sync", json={})
        response.raise_for_status()
        return response.json()

    def health_check_sync(self) -> dict[str, Any]:
        """
        Check if the backend is healthy by fetching items (sync version).

        Returns:
            Health status with item count

        Raises:
            httpx.RequestError: If the backend is unreachable
            httpx.HTTPStatusError: If the backend returns an error status
        """
        items = self.get_items_sync()
        return {"status": "healthy", "item_count": len(items)}

    async def get_items(self) -> list[dict[str, Any]]:
        """Async version of get_items."""
        response = await self._async_client.get("/items/")
        response.raise_for_status()
        return response.json()

    async def get_pass_rates(self, lab: str) -> list[dict[str, Any]]:
        """Async version of get_pass_rates."""
        response = await self._async_client.get(
            "/analytics/pass-rates", params={"lab": lab}
        )
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> dict[str, Any]:
        """Async version of health_check."""
        items = await self.get_items()
        return {"status": "healthy", "item_count": len(items)}

    async def close(self):
        """Close the HTTP client sessions."""
        await self._async_client.aclose()
        self._sync_client.close()


# Global client instance (created when config is loaded)
_client: LMSAPIClient | None = None


def get_client(base_url: str, api_key: str) -> LMSAPIClient:
    """
    Get or create the global API client instance.

    Args:
        base_url: Backend base URL
        api_key: API key for authentication

    Returns:
        The API client instance
    """
    global _client
    if _client is None:
        _client = LMSAPIClient(base_url, api_key)
    return _client
