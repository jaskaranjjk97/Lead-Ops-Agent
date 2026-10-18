from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.llm import get_llm
from app.state import LeadState


class LeadExtraction(BaseModel):
    company_name: str = Field(
        description="Name of the lead's company. If not found, use 'Unknown'."
    )
    contact_name: str = Field(
        description="First and last name of the contact. If not found, use 'Unknown'."
    )
    contact_email: str = Field(
        description="Email address of the contact. If not found, use 'Unknown'."
    )
    budget_tier: Literal["low", "medium", "high", "unknown"] = Field(
        description="Budget tier"
    )
    intent: Literal["demo", "pricing", "support", "other"] = Field(description="Intent")
    company_size: int | None = Field(
        default=None, description="Number of employees mentioned, if any"
    )
    industry: str | None = Field(default=None, description="Industry mentioned, if any")


EXTRACT_SYSTEM = """You are an expert data extractor for a B2B sales team.
Read the inbound message and extract the required fields.

Rules:
- If a field is missing, use "unknown" for budget, "other" for intent, and "Unknown" for names.
- Budget tier: "high" means enterprise/custom pricing, "medium" means standard plans, "low" means individual/small.
- Intent: Be very careful here. 
  - "demo" if they ask to see the product or request a meeting.
  - "pricing" if they ask for cost, discounts, or specifically mention "pricing".
  - "support" if they need help with an existing product.
  - "other" for anything else.
"""


def extract_node(state: LeadState) -> dict:
    raw_text = state.get("raw_inbound_text", "")
    if not raw_text:
        return {
            "trace": state.get("trace", [])
            + [
                {
                    "node": "extract",
                    "status": "error",
                    "details": {"error": "No text provided"},
                }
            ]
        }

    llm = get_llm(temperature=0.0).with_structured_output(LeadExtraction)
    result: LeadExtraction = llm.invoke(
        [
            SystemMessage(content=EXTRACT_SYSTEM),
            HumanMessage(content=raw_text),
        ]
    )

    return {
        "company_name": result.company_name,
        "contact_name": result.contact_name,
        "contact_email": result.contact_email,
        "budget_tier": result.budget_tier,
        "intent": result.intent,
        "company_size": result.company_size,
        "industry": result.industry,
        "trace": state.get("trace", [])
        + [
            {
                "node": "extract",
                "status": "ok",
                "details": {"company": result.company_name, "intent": result.intent},
            }
        ],
    }
