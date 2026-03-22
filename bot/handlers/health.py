"""
Handler for /health command.

Calls the LMS backend to check if it's healthy.
"""

import httpx
from services.api_client import get_client
from config import load_config


def handle_health() -> str:
    """
    Handle the /health command.

    Returns:
        Backend health status with item count, or error message
    """
    config = load_config()

    try:
        client = get_client(config.lms_api_url, config.lms_api_key)
        result = client.health_check_sync()
        return (
            f"🏥 Health Check:\n\n"
            f"Backend is healthy. {result['item_count']} items available."
        )
    except httpx.ConnectError as e:
        # Backend is unreachable
        error_detail = str(e)
        if "Connection refused" in error_detail:
            return (
                f"❌ Backend error: connection refused ({config.lms_api_url}). "
                f"Check that the services are running."
            )
        return f"❌ Backend error: {error_detail}"
    except httpx.HTTPStatusError as e:
        # Backend returned an HTTP error status
        return (
            f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. "
            f"The backend service may be down."
        )
    except httpx.RequestError as e:
        # Other request errors (timeout, DNS, etc.)
        return f"❌ Backend error: {e}"
    except Exception as e:
        # Unexpected errors
        return f"❌ Backend error: {e}"
