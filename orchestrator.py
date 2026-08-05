import os
from pathlib import Path

from anthropic import Anthropic

from retriever import Retriever
from tools.billing import get_billing_history
from tools.org import get_org_seats
from tools.plan import get_user_plan
from tools.usage import get_usage_status

MODEL_NAME = os.environ.get("NIMBUS_MODEL", "claude-sonnet-5")
MAX_TOOL_ITERATIONS = 5

SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "system_prompt.md").read_text()

# Tool schemas exposed to Claude. Note that get_user_plan / get_billing_history /
# get_usage_status / get_org_seats take NO identity parameter — there is no
# user_id, email, or account field in any of these schemas. The model has no
# way to name whose data it wants; the orchestrator always binds the current
# session's user_id when it actually executes the call. This is what makes
# cross-user data access structurally impossible rather than prompt-dependent.
TOOL_DEFS = [
    {
        "name": "search_knowledge_base",
        "description": (
            "Search Nimbus AI's help-center articles (plans, billing policy, "
            "usage/rate-limit policy, troubleshooting guides, admin/org docs). "
            "Use this for anything about how Nimbus AI works or what its "
            "policies are."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural-language search query."},
                "category": {
                    "type": "string",
                    "enum": ["plans", "billing", "usage", "troubleshooting", "admin"],
                    "description": "Optional category filter, if the topic is unambiguous.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_user_plan",
        "description": "Get the current logged-in user's plan tier, role, org, and signup date.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_billing_history",
        "description": "Get the current logged-in user's recent charges (up to 10, most recent first).",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_usage_status",
        "description": "Get the current logged-in user's message usage for the current billing cycle and when it resets.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_org_seats",
        "description": (
            "Get the current logged-in user's org seat roster. Only works if "
            "the user is an org admin/owner; returns a permission error otherwise."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
]


class Orchestrator:
    def __init__(self):
        self.client = Anthropic()  # reads ANTHROPIC_API_KEY from env
        self.retriever = Retriever()

    def _execute_tool(self, name: str, tool_input: dict, user_id: int):
        if name == "search_knowledge_base":
            return self.retriever.search(
                query=tool_input["query"], category=tool_input.get("category"), k=4
            )
        if name == "get_user_plan":
            return get_user_plan(user_id)
        if name == "get_billing_history":
            return get_billing_history(user_id)
        if name == "get_usage_status":
            return get_usage_status(user_id)
        if name == "get_org_seats":
            return get_org_seats(user_id)
        return {"error": f"unknown tool '{name}'"}

    def handle_message(self, user_id: int, history: list[dict], user_message: str) -> str:
        """
        history: prior turns as [{"role": "user"|"assistant", "content": ...}, ...]
        Returns the assistant's final text reply. Caller is responsible for
        appending both the user_message and the returned reply to history.
        """
        messages = history + [{"role": "user", "content": user_message}]

        for _ in range(MAX_TOOL_ITERATIONS):
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFS,
                messages=messages,
            )

            if response.stop_reason != "tool_use":
                return "".join(
                    block.text for block in response.content if block.type == "text"
                )

            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                result = self._execute_tool(block.name, block.input, user_id)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    }
                )
            messages.append({"role": "user", "content": tool_results})

        return (
            "I wasn't able to resolve this after several attempts — let me "
            "connect you with a human agent instead."
        )
