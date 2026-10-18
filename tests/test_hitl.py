import uuid

from langgraph.types import Command

from app.graph import compiled_graph


def run_lead(text: str, human_decision: str):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print(f"\n{'=' * 60}\n> INPUT: {text[:60]}...")

    # 1. Invoke the graph
    compiled_graph.invoke({"raw_inbound_text": text, "trace": []}, config=config)

    # Check if the graph paused at the interrupt
    state = compiled_graph.get_state(config)

    if state.next:
        # The graph is paused at the 'human_approval' node
        print("\n⏸️  GRAPH PAUSED FOR HUMAN REVIEW")

        # We can access the payload sent by interrupt()
        # Note: In LangGraph 0.2.x, it's stored in state.tasks[0].interrupts[0].value
        interrupt_payload = state.tasks[0].interrupts[0].value
        print(f"  Draft to review:\n---\n{interrupt_payload['draft_email']}\n---")

        print(f"  👤 Human Action: {human_decision.upper()}")

        # 2. Resume the graph with the human's decision
        resume_payload = {"status": human_decision, "feedback": "Test feedback"}
        final_state = compiled_graph.invoke(
            Command(resume=resume_payload), config=config
        )

        print(f"  🏁 Final Trace: {[t['node'] for t in final_state.get('trace', [])]}")
        print(f"  CRM ID: {final_state.get('crm_record_id', 'N/A (Rejected)')}")
    else:
        print("\n⏭️  GRAPH COMPLETED WITHOUT PAUSING (Lead not qualified)")


if __name__ == "__main__":
    # Test 1: High quality lead, approved by human
    run_lead(
        "Hi, I'm Sarah from TechNova. We need enterprise pricing. sarah@technova.com",
        "approved",
    )

    # Test 2: High quality lead, rejected by human
    run_lead(
        "Hi, I'm John from TechCorp. We want a demo. john@techcorp.com", "rejected"
    )

    # Test 3: Unqualified lead (skips drafting entirely)
    run_lead(
        "Hey, I'm a student. Can I get a discount?",
        "approved",  # This won't even be called
    )
