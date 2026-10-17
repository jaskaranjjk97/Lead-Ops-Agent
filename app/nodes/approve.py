from langgraph.types import interrupt

from app.state import LeadState


def approval_node(state: LeadState) -> dict:
    """Pause the graph and wait for a human to approve or reject the draft."""

    # This sends the draft to the outside world (our API/UI)
    # The graph FREEZES here until the UI sends back a 'Command(resume=...)'
    human_decision = interrupt(
        {
            "draft_email": state.get("draft_email"),
            "company_name": state.get("company_name"),
            "lead_score": state.get("lead_score"),
        }
    )

    # When the graph resumes, 'human_decision' will contain the payload from the UI
    # e.g., {"status": "approved", "feedback": "Looks good!"}

    status = human_decision.get("status", "rejected")
    feedback = human_decision.get("feedback", "")

    return {
        "approval_status": status,
        "human_feedback": feedback,
        "trace": state.get("trace", [])
        + [
            {
                "node": "approve",
                "status": "ok",
                "details": {
                    "decision": status,
                    "feedback": feedback,
                },
            }
        ],
    }
