import json
import uuid
from datetime import datetime

from app import config
from app.state import LeadState


def save_to_crm(state: LeadState) -> str:
    """Save the approved lead to the mock CRM."""
    crm_data = json.loads(config.CRM_FILE.read_text())

    lead_id = f"LEAD-{uuid.uuid4().hex[:6].upper()}"

    new_lead = {
        "id": lead_id,
        "company": state.get("company_name"),
        "contact": state.get("contact_name"),
        "email": state.get("contact_email"),
        "score": state.get("lead_score"),
        "intent": state.get("intent"),
        "created_at": datetime.now().isoformat(),
        "status": "contacted",
    }

    crm_data["existing_leads"].append(new_lead)
    config.CRM_FILE.write_text(json.dumps(crm_data, indent=2))

    return lead_id
