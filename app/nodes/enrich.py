from app.state import LeadState
from app.tools.enrichment import mock_enrich_company


def enrich_node(state: LeadState) -> dict:
    """Enrich the lead using text-extracted data + mock API fallback."""
    company = state.get("company_name", "")

    # 1. What did the user explicitly tell us in the text?
    extracted_size = state.get("company_size")
    extracted_industry = state.get("industry")

    # Clean up LLM hallucinations: If it said "unknown", treat it as missing
    if extracted_industry and extracted_industry.lower() == "unknown":
        extracted_industry = None
    if extracted_size == 0:
        extracted_size = None

    # 2. What does our mock API say?
    api_data = (
        mock_enrich_company(company)
        if company
        else {"company_size": 10, "industry": "Unknown"}
    )

    # 3. Merge: Text wins, API is the fallback
    final_size = extracted_size if extracted_size else api_data["company_size"]
    final_industry = extracted_industry if extracted_industry else api_data["industry"]

    return {
        "company_size": final_size,
        "industry": final_industry,
        "trace": state.get("trace", [])
        + [
            {
                "node": "enrich",
                "status": "ok",
                "details": {
                    "size": final_size,
                    "industry": final_industry,
                    "source": "text + mock_api",
                },
            }
        ],
    }
