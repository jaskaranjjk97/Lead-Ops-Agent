from typing import Literal, TypedDict


class LeadState(TypedDict):
    # 1.Input
    raw_inbound_text: str

    # 2.Extraction structure
    company_name: str
    contact_name: str
    contact_email: str
    budget_tier: Literal["low", "medium", "high", "unknown"]
    intent: Literal["demo", "pricing", "support", "other"]

    # 3.Enrichment
    company_size: int
    industry: str

    # 4. Scoring
    lead_score: int  # 0-100
    is_qualified: bool

    # 5. Action & HITL (Human-in-the-Loop)
    draft_email: str  # The email the AI wrote
    approval_status: Literal["pending", "approved", "rejected"]
    human_feedback: str  # Optional reason if rejected
    crm_record_id: str  # ID of the created/updated CRM record

    # 6. Observability
    trace: list[dict]
