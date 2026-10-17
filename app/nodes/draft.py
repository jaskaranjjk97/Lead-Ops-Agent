from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import get_llm
from app.state import LeadState

DRAFT_PROMPT = """ You are a sales development representative for a B2B SaaS company.
write a short,personalized email to qualified lead.

Rules:
- Keep it under 100 words.
- Reference their specific intent (e.g., if they want pricing, mention pricing).
- Do not make up features or pricing numbers.
- Be friendly and direct.
- End with a call to action (e.g., "Do you have 15 minutes for a call next week?").
"""


def draft_node(state: LeadState) -> dict:
    """LangGraph Node: Write a personalized email to qualified Lead."""
    prompt = f"""
    Company: {state.get("company_name")}
    Contact: {state.get("contact_name")}
    Budget Tier : {state.get("budget_tier")}
    Intent : {state.get("intent")}
"""

    llm = get_llm(temperature=0.5)
    response = llm.invoke(
        [
            SystemMessage(content=DRAFT_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    return {
        "draft_email": response.content,
        "trace": state.get("trace", [])
        + [
            {
                "node": "draft_email",
                "status": "ok",
                "details": {"draft_length": len(response.content)},
            }
        ],
    }
