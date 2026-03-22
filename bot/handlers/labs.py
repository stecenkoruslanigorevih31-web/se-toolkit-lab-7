"""
Handler for /labs command.

Fetches available labs from the LMS backend.
"""

import httpx
from services.api_client import get_client
from config import load_config


def handle_labs() -> str:
    """
    Handle the /labs command.

    Returns:
        List of available labs with their names
    """
    config = load_config()

    try:
        client = get_client(config.lms_api_url, config.lms_api_key)
        items = client.get_items_sync()

        # Filter only labs (items with type 'lab')
        labs = [item for item in items if item.get("type") == "lab"]

        if not labs:
            return "📚 Available Labs:\n\nNo labs found in the backend."

        # Build the response
        response_lines = ["📚 Available Labs:"]
        for lab in labs:
            lab_id = lab.get("id", "unknown")
            lab_name = lab.get("title", "Unnamed Lab")
            response_lines.append(f"- {lab_id} — {lab_name}")

        return "\n".join(response_lines)

    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused. Check that the services are running."
    except httpx.HTTPStatusError as e:
        return (
            f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. "
            f"The backend service may be down."
        )
    except httpx.RequestError as e:
        return f"❌ Backend error: {e}"
    except Exception as e:
        return f"❌ Backend error: {e}"
