"""
Handler for /scores command.

Fetches per-task pass rates for a specific lab from the LMS backend.
"""

import httpx
from services.api_client import get_client
from config import load_config


def handle_scores(lab_id: str | None = None) -> str:
    """
    Handle the /scores command.

    Args:
        lab_id: Optional lab identifier (e.g., "lab-04")

    Returns:
        Score information for the specified lab
    """
    config = load_config()

    # Check if lab_id was provided
    if not lab_id:
        return (
            "📊 Scores:\n\n"
            "Usage: /scores <lab_id>\n\n"
            "Examples:\n"
            "/scores lab-04\n"
            "/scores lab-03"
        )

    try:
        client = get_client(config.lms_api_url, config.lms_api_key)
        pass_rates = client.get_pass_rates_sync(lab_id)

        if not pass_rates:
            return (
                f"📊 Scores for {lab_id}:\n\n"
                f"No data available yet. This could mean:\n"
                f"1. No learners have submitted this lab yet\n"
                f"2. Lab '{lab_id}' doesn't exist\n\n"
                f"Use /labs to see available labs."
            )

        # Build the response
        # API returns: [{"task": "Task name", "avg_score": 0.75, "attempts": 10}, ...]
        response_lines = [f"📊 Pass rates for {lab_id}:"]
        for task_data in pass_rates:
            task_name = task_data.get("task", "Unknown Task")
            avg_score = task_data.get("avg_score", 0)
            attempts = task_data.get("attempts", 0)
            # avg_score is 0.0-1.0, convert to percentage
            pass_rate = avg_score * 100 if avg_score <= 1.0 else avg_score
            response_lines.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")

        return "\n".join(response_lines)

    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused. Check that the services are running."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return (
                f"📊 Scores for {lab_id}:\n\n"
                f"Lab '{lab_id}' not found. Use /labs to see available labs."
            )
        return (
            f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. "
            f"The backend service may be down."
        )
    except httpx.RequestError as e:
        return f"❌ Backend error: {e}"
    except Exception as e:
        return f"❌ Backend error: {e}"
