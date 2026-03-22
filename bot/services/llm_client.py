"""
LLM client with tool calling support.

This client wraps the Qwen Code API (or any OpenAI-compatible API)
and supports tool/function calling for intent-based routing.
"""

import json
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


# =============================================================================
# Tool schemas for all 9 backend endpoints
# =============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get the list of all labs and tasks. Use this to find available labs or to get lab IDs for other queries.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get the list of all enrolled learners. Use this to answer questions about how many students are enrolled.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab. Use this to see how scores are distributed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'. Use get_items to find lab IDs.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab. Use this to see which tasks are hardest or to compare task difficulty.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'. Use get_items to find lab IDs.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a lab. Use this to see when students were most active.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'. Use get_items to find lab IDs.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group performance for a lab. Use this to compare groups or find which group is doing best/worst.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'. Use get_items to find lab IDs.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by average score for a lab. Use this to find the best performing students.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'. Use get_items to find lab IDs.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return. Default is 5.",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab. Use this to see what percentage of students completed the lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'. Use get_items to find lab IDs.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync to refresh data from the autochecker. Use this when the user asks to update or refresh data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


class LLMClient:
    """Client for interacting with the LLM API with tool calling support."""

    def __init__(self, api_key: str, base_url: str, model: str):
        """
        Initialize the LLM client.

        Args:
            api_key: API key for authentication
            base_url: Base URL of the LLM API (e.g., http://localhost:42005/v1)
            model: Model name to use (e.g., 'coder-model')
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """
        Send a chat request to the LLM.

        Args:
            messages: List of conversation messages
            tools: Optional list of tool schemas for function calling
            system_prompt: Optional system prompt to prepend

        Returns:
            LLM response with either text content or tool calls
        """
        # Build messages list with system prompt if provided
        request_messages = []
        if system_prompt:
            request_messages.append({"role": "system", "content": system_prompt})
        request_messages.extend(messages)

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": request_messages,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = await self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()

    async def chat_with_tools(
        self,
        user_message: str,
        tools: list[dict[str, Any]],
        system_prompt: str,
        max_iterations: int = 5,
    ) -> str:
        """
        Chat with the LLM using tool calling loop.

        This implements the full tool calling loop:
        1. Send user message + tools to LLM
        2. If LLM returns tool calls, execute them
        3. Feed tool results back to LLM
        4. Repeat until LLM returns final answer

        Args:
            user_message: The user's message
            tools: List of tool schemas
            system_prompt: System prompt for the LLM
            max_iterations: Maximum tool calling iterations

        Returns:
            Final response from the LLM
        """
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": user_message}
        ]

        for iteration in range(max_iterations):
            logger.debug(
                f"[Iteration {iteration + 1}] Calling LLM with {len(messages)} messages"
            )

            response = await self.chat(messages, tools=tools, system_prompt=system_prompt)

            # Get the assistant message
            assistant_message = response.get("choices", [{}])[0].get("message", {})
            content = assistant_message.get("content", "")
            tool_calls = assistant_message.get("tool_calls", [])

            # If no tool calls, return the content
            if not tool_calls:
                return content or "I'm not sure how to help with that. Try asking about labs, scores, or students."

            # Execute tool calls
            tool_results = []
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                function_name = function.get("name", "")
                function_args_str = function.get("arguments", "{}")

                try:
                    function_args = json.loads(function_args_str)
                except json.JSONDecodeError:
                    function_args = {}

                logger.info(f"[tool] LLM called: {function_name}({function_args})")

                # Execute the tool
                result = await self._execute_tool(function_name, function_args)
                result_str = json.dumps(result, default=str)

                logger.info(f"[tool] Result: {result_str[:200]}...")

                tool_results.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id", ""),
                        "content": result_str,
                    }
                )

            # Add assistant message and tool results to conversation
            messages.append(assistant_message)
            messages.extend(tool_results)

            logger.info(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM")

        # If we exhausted iterations, return what we have
        return content or "I need more iterations to answer this question completely."

    async def _execute_tool(
        self, function_name: str, arguments: dict[str, Any]
    ) -> Any:
        """
        Execute a tool function by name.

        Args:
            function_name: Name of the tool function
            arguments: Arguments to pass to the function

        Returns:
            Result from the tool function
        """
        # Import here to avoid circular imports
        from services.api_client import get_client
        from config import load_config

        config = load_config()
        client = get_client(config.lms_api_url, config.lms_api_key)

        tool_map = {
            "get_items": lambda: client.get_items_sync(),
            "get_learners": lambda: client.get_learners_sync(),
            "get_scores": lambda: client.get_scores_sync(arguments.get("lab", "")),
            "get_pass_rates": lambda: client.get_pass_rates_sync(arguments.get("lab", "")),
            "get_timeline": lambda: client.get_timeline_sync(arguments.get("lab", "")),
            "get_groups": lambda: client.get_groups_sync(arguments.get("lab", "")),
            "get_top_learners": lambda: client.get_top_learners_sync(
                arguments.get("lab", ""), arguments.get("limit", 5)
            ),
            "get_completion_rate": lambda: client.get_completion_rate_sync(
                arguments.get("lab", "")
            ),
            "trigger_sync": lambda: client.sync_pipeline_sync(),
        }

        if function_name not in tool_map:
            return {"error": f"Unknown tool: {function_name}"}

        try:
            result = tool_map[function_name]()
            return result
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        """Close the HTTP client session."""
        await self._client.aclose()


# Global client instance
_client: LLMClient | None = None


def get_llm_client(api_key: str, base_url: str, model: str) -> LLMClient:
    """
    Get or create the global LLM client instance.

    Args:
        api_key: API key for authentication
        base_url: Base URL of the LLM API
        model: Model name to use

    Returns:
        The LLM client instance
    """
    global _client
    if _client is None:
        _client = LLMClient(api_key, base_url, model)
    return _client
