from app.state import LeadState
from app.tools.enrichment import mock_enrich_company


def enrich_node(state: LeadState) -> dict:
    """Call external APIs to get company size and industry."""
    company_name = state.get("company_name", "")
    if not company_name or company_name == "Unknown":
        return {
            "company_size": 0,
            "industry": "Unknown",
            "trace": state.get("trace", [])
            + [
                {
                    "node": "enrich",
                    "status": "skipped",
                    "details": {"reason": "No company name is provided."},
                }
            ],
        }
    data = mock_enrich_company(company_name)

    return {
        "company_size": data["company_size"],
        "industry": data["industry"],
        "trace": state.get("trace", [])
        + [
            {
                "node": "enrich",
                "status": "ok",
                "details": {
                    "industry": data["industry"],
                    "size": data["company_size"],
                },
            }
        ],
    }
