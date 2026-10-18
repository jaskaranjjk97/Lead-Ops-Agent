from app.nodes.enrich import enrich_node
from app.nodes.extract import extract_node
from app.nodes.score import score_node

state = {
    "raw_inbound_text": "Hi, I'm Sarah from TechNova. We are a SaaS company with about 120 employees. We need enterprise pricing for your product. Email me at sarah@technova.com",
    "trace": [],
}
state.update(extract_node(state))
state.update(enrich_node(state))
state.update(score_node(state))

print(f"Company: {state['company_name']}")
print(f"Size: {state['company_size']} | Industry: {state['industry']}")
print(f"Score: {state['lead_score']} | Qualified: {state['is_qualified']}")
print(f"Reason: {state['trace'][-1]['details']['reason']}")
