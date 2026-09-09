import json
import os
from pathlib import Path

from openai import OpenAI

from retriever import Retriever
from tools.billing import get_billing_history
from tools.org import get_org_seats
from tools.plan import get_user_plan
from tools.usage import get_usage_status

MODEL_NAME = os.environ.get("NIMBUS_MODEL", "deepseek/deepseek-v4-flash")
MAX_TOOL_ITERATIONS = 5

SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "system_prompt.md").read_text()

# Tool definitions for OpenAI format.
#
# Note that get_user_plan / get_billing_history / get_usage_status / get_org_seats
# expose NO identity parameter — there is no user_id, email, or account field in
# any of these schemas. The model has no way to name whose data it wants; the
# orchestrator always binds the current session's user_id when it actually
# executes the call. This is what makes cross-user data access structurally
# impossible rather than prompt-dependent.
TOOL_DEFS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": (
                "Search Nimbus AI's help-center articles (plans, billing policy, "
                "usage/rate-limit policy, troubleshooting guides, admin/org docs). "
                "Use this for anything about how Nimbus AI works or what its "
                "policies are."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural-language search query.",
                    },
                    "category": {
                        "type": "string",
                        "enum": ["plans", "billing", "usage", "troubleshooting", "admin"],
                        "description": "Optional category filter, if the topic is unambiguous.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_plan",
            "description": "Get the current logged-in user's plan tier, role, org, and signup date.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_billing_history",
            "description": "Get the current logged-in user's recent charges (up to 10, most recent first).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_usage_status",
            "description": "Get the current logged-in user's message usage for the current billing cycle and when it resets.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_org_seats",
            "description": (
                "Get the current logged-in user's org seat roster. Only works if "
                "the user is an org admin/owner; returns a permission error otherwise."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


class Orchestrator:
    def __init__(self):
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. "
                "Copy .env.example to .env and add your key from https://openrouter.ai/keys"
            )
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.retriever = Retriever()

    def _execute_tool(self, name: str, arguments: dict, user_id: int) -> str:
        if name == "search_knowledge_base":
            return str(self.retriever.search(
                query=arguments.get("query", ""),
                category=arguments.get("category"),
                k=4,
            ))
        if name == "get_user_plan":
            return str(get_user_plan(user_id))
        if name == "get_billing_history":
            return str(get_billing_history(user_id))
        if name == "get_usage_status":
            return str(get_usage_status(user_id))
        if name == "get_org_seats":
            return str(get_org_seats(user_id))
        return str({"error": f"unknown tool '{name}'"})

    def handle_message(self, user_id: int, history: list[dict], user_message: str) -> str:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for turn in history:
            messages.append(turn)
        messages.append({"role": "user", "content": user_message})

        for _ in range(MAX_TOOL_ITERATIONS):
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                max_tokens=1024,
                tools=TOOL_DEFS,
                messages=messages,
            )

            choice = response.choices[0]
            msg = choice.message

            # No tool calls → return text reply
            if not msg.tool_calls:
                return msg.content or ""

            messages.append(msg)

            for tool_call in msg.tool_calls:
                try:
                    arguments = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                except (TypeError, json.JSONDecodeError):
                    arguments = {}
                result = self._execute_tool(tool_call.function.name, arguments, user_id)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

        return (
            "I wasn't able to resolve this after several attempts — let me "
            "connect you with a human agent instead."
        )