from app.state import LeadState
from app.tools.crm import save_to_crm


def finalize_node(state: LeadState) -> dict:
    """Save to CRM and send the email."""
    status = state.get("approval_status", "rejected")

    if status == "approved":
        lead_id = save_to_crm(state)

        return {
            "crm_record_id": lead_id,
            "trace": state.get("trace", [])
            + [
                {
                    "node": "finalize",
                    "status": "ok",
                    "details": {
                        "action": "Saved to CRM and sent email",
                        "crm_id": lead_id,
                    },
                }
            ],
        }

    else:
        return {
            "trace": state.get("trace", [])
            + [
                {
                    "node": "finalize",
                    "status": "ok",
                    "details": {"action": "Rejected by human. Email not sent."},
                }
            ],
        }
