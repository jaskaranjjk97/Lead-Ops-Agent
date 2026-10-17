from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app import config
from app.llm import get_llm
from app.state import LeadState


class LeadScore(BaseModel):
    score: int = Field(description="score between 0-100 based on ICP match.")
    is_qualified: bool = Field(description="True if score>60 else False.")
    reason: str = Field(description="A single sentence reason explaning the score.")


SCORE_SYSTEM = """You are a sales operations analyst. Score the lead from 0-100 based on the Ideal Customer Profile (ICP).

Rules:
- Match industry? +30 points
- Company size meets minimum? +30 points
- Budget tier is 'high'? +20 points
- Intent is 'demo' or 'pricing'? +20 points
- If they are a competitor or student, score 0.

Return the score, a boolean is_qualified (score >= 60), and a one-sentence reason."""


def score_node(state: LeadState) -> dict:
    """LangGraph Node: Score with LLM based on ICP match."""
    icp_data = config.ICP_FILE.read_text()

    lead_summary = f"""
        Company: {state.get("company_name")}
        Industry: {state.get("industry")}
        Size: {state.get("company_size")}
        Budget: {state.get("budget_tier")}
        Intent: {state.get("intent")}
"""
    llm = get_llm().with_structured_output(LeadScore)
    result: LeadScore = llm.invoke(
        [
            SystemMessage(content=SCORE_SYSTEM),
            HumanMessage(content=f"ICP:\n{icp_data}\n\nLead Data:\n{lead_summary}"),
        ]
    )

    return {
        "lead_score": result.score,
        "is_qualified": result.is_qualified,
        "trace": state.get("trace", [])
        + [
            {
                "node": "score",
                "status": "ok",
                "details": {
                    "score": result.score,
                    "is_qualified": result.is_qualified,
                    "reason": result.reason,
                },
            }
        ],
    }
