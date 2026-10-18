import traceback
import uuid

from fastapi import FastAPI
from langgraph.types import Command
from pydantic import BaseModel

from app.graph import compiled_graph

app = FastAPI(title="Lead Ops Agent API")


class LeadRequest(BaseModel):
    text: str


class ApprovalRequest(BaseModel):
    status: str
    feedback: str = ""

@app.post("/webhook/lead")
def process_lead(req: LeadRequest):
    try:
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        compiled_graph.invoke({"raw_inbound_text": req.text, "trace": []}, config=config)
        state = compiled_graph.get_state(config)
        
        if state.next:
            payload = state.tasks[0].interrupts[0].value
            return {
                "thread_id": thread_id,
                "status": "pending_approval",
                "draft_email": payload.get("draft_email", ""),
                "company_name": payload.get("company_name", ""),
                "lead_score": payload.get("lead_score", 0),
            }
        else:
            return {
                "thread_id": thread_id,
                "status": "completed",
                "message": "Lead did not qualify for outreach."
            }
            
    except Exception as e:  # noqa: BLE001
        print("\n=== API ERROR ===")
        traceback.print_exc()
        print("=================\n")
        # FastAPI handles this properly and returns a 500 status code
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/approve/{thread_id}")
def approve_lead(thread_id: str, req: ApprovalRequest):
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state = compiled_graph.get_state(config)
        
        if not state or not state.next:
            return {"error": "Graph is not paused."}
            
        resume_payload = {"status": req.status, "feedback": req.feedback}
        result = compiled_graph.invoke(Command(resume=resume_payload), config=config)
        
        return {
            "status": "completed",
            "crm_id": result.get("crm_record_id"),
            "trace": [t["node"] for t in result.get("trace", [])]
        }
    except Exception as e:  # noqa: BLE001
        print("\n=== API ERROR ===")
        traceback.print_exc()
        print("=================\n")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))