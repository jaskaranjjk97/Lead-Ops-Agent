def mock_enrich_company(company_name: str) -> dict:
    """Simulate an API call to Clearbit/Apollo to get company data."""
    name_lower = company_name.lower()

    if "tech" in name_lower or "saas" in name_lower:
        return {"company_size": 150, "industry": "SaaS"}  # <-- Fixed spelling
    elif "bank" in name_lower or "fin" in name_lower:
        return {"company_size": 500, "industry": "Fintech"}
    elif "shop" in name_lower or "store" in name_lower:
        return {"company_size": 30, "industry": "E-commerce"}

    return {"company_size": 10, "industry": "Unknown"}  # <-- Fixed spelling
