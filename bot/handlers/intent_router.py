"""
Intent router for natural language queries.

This handler uses the LLM to understand user intent and route to the appropriate
backend API calls. It supports multi-step reasoning and tool calling.
"""

import logging

from services.llm_client import get_llm_client, TOOLS
from config import load_config

logger = logging.getLogger(__name__)

# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS). 
You have access to tools that let you fetch data about labs, tasks, students, scores, and analytics.

Your job is to:
1. Understand what the user is asking
2. Use the available tools to fetch the relevant data
3. Analyze the data and provide a clear, helpful answer

When answering:
- Be specific and include numbers from the data
- If comparing labs or tasks, mention the actual values
- If data is not available, say so clearly
- For greetings or unclear queries, be friendly and suggest what you can help with

Available capabilities:
- List all available labs and tasks
- Show pass rates and scores for specific labs
- Find top performing students
- Compare groups
- Show completion rates
- Show submission timelines
- Refresh data from the autochecker

Always use tools to get real data before answering questions about labs, scores, or students."""


def handle_natural_language(message: str) -> str:
    """
    Handle a natural language message using the LLM.

    This function:
    1. Sends the message to the LLM with tool definitions
    2. The LLM decides which tools to call
    3. Executes the tools and feeds results back
    4. Returns the LLM's final answer

    Args:
        message: The user's natural language message

    Returns:
        Response text to send to the user
    """
    import asyncio

    config = load_config()

    # Check if LLM is configured
    if not config.llm_api_key or not config.llm_api_base_url or not config.llm_api_model:
        return (
            "LLM is not configured. Please set LLM_API_KEY, LLM_API_BASE_URL, and LLM_API_MODEL "
            "in your .env.bot.secret file."
        )

    try:
        # Run the async LLM call in a sync context
        result = asyncio.run(_route_with_llm(message, config))
        return result
    except Exception as e:
        logger.exception("Error in natural language routing")
        return f"LLM error: {e}. Please try again or use /help for available commands."


async def _route_with_llm(message: str, config) -> str:
    """
    Internal async function to route with LLM.

    Args:
        message: The user's message
        config: Bot configuration

    Returns:
        LLM response text
    """
    client = get_llm_client(
        config.llm_api_key,
        config.llm_api_base_url,
        config.llm_api_model,
    )

    response = await client.chat_with_tools(
        user_message=message,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        max_iterations=5,
    )

    return response
