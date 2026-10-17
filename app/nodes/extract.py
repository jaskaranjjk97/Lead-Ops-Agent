from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.llm import get_llm
from app.state import LeadState


class LeadExtraction(BaseModel):
    company_name: str = Field(description="Name of the lead's company")
    contact_name: str = Field(description="First and last name of the contact")
    contact_email: str = Field(description="Email address of the contact")
    budget_tier: Literal["low", "medium", "high", "unknown"] = Field(
        description="Budget tier"
    )
    intent: Literal["demo", "pricing", "support", "other"] = Field(description="Intent")


EXTRACT_SYSTEM = """You are an expert data extractor for a B2B sales team.

Read the inbound message and extract the required fields.

Rules:
- If a field is missing, use "unknown" for budget, "other" for intent, and "Unknown" for names.
- Email must be a valid format.
- Budget tier: "high" means enterprise/custom pricing, "medium" means standard plans, "low" means individual/small.
- Intent: "demo" if they ask to see the product, "pricing" if they ask for cost, "support" if they need help.
"""


def extract_node(state: LeadState) -> dict:
    """LangGraph Node : to extract the required fields from iraw text the lead send."""

    raw_text = state.get("raw_inbound_text", "")
    if not raw_text:
        return {"trace": state.get("trace", [])} + [
            {
                "node": "extract",
                "status": "error",
                "details": {"error": "No text provided."},
            }
        ]

    llm = get_llm().with_structured_output(LeadExtraction)
    result: LeadExtraction = llm.invoke(
        [
            SystemMessage(content=EXTRACT_SYSTEM),
            HumanMessage(content=raw_text),
        ]
    )

    # Normalize string literals to match our Literal types (just in case)
    budget = result.budget_tier.lower()
    if budget not in ["low", "medium", "high", "unknown"]:
        budget = "unknown"

    intent = result.intent.lower()
    if intent not in ["demo", "pricing", "support", "other"]:
        intent = "other"

    return {
        "company_name": result.company_name,
        "contact_name": result.contact_name,
        "contact_email": result.contact_email,
        "budget_tier": budget,
        "intent": intent,
        "trace": state.get("trace", [])
        + [
            {
                "node": "extract",
                "status": "ok",
                "details": {"company": result.company_name, "intent": intent},
            }
        ],
    }
