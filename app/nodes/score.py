import json

from app import config
from app.state import LeadState


def score_node(state: LeadState) -> dict:
    """Score the enriched lead against the ICP using deterministic Python logic."""

    # 1. Load the ICP rules
    icp = json.loads(config.ICP_FILE.read_text())

    score = 0
    reasons = []

    # 2. Extract facts from the state
    industry = state.get("industry", "Unknown")
    size = state.get("company_size", 0)
    budget = state.get("budget_tier", "unknown")
    intent = state.get("intent", "other")

    # 3. Apply the rules (Pure Python)
    # Make matching case-insensitive
    target_industries_lower = [i.lower() for i in icp["target_industries"]]
    industry_lower = industry.lower()

    if industry_lower in target_industries_lower:
        score += 30
        reasons.append(f"Industry ({industry}) matches")
    else:
        reasons.append(f"Industry ({industry}) does not match")
    if size >= icp["min_company_size"]:
        score += 30
        reasons.append(f"Size ({size}) meets minimum")
    else:
        reasons.append(f"Size ({size}) is too small")

    if budget == icp["target_budget_tier"]:
        score += 20
        reasons.append(f"Budget ({budget}) matches")
    else:
        reasons.append(f"Budget ({budget}) is not high")

    if intent in ["demo", "pricing"]:
        score += 20
        reasons.append(f"Intent ({intent}) is strong")
    else:
        reasons.append(f"Intent ({intent}) is weak")

    # 4. Calculate qualification (Python handles the math perfectly)
    is_qualified = score >= 60
    reason_string = ", ".join(reasons)

    return {
        "lead_score": score,
        "is_qualified": is_qualified,
        "trace": state.get("trace", [])
        + [
            {
                "node": "score",
                "status": "ok",
                "details": {
                    "score": score,
                    "qualified": is_qualified,
                    "reason": reason_string,
                },
            }
        ],
    }
