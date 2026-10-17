from app.nodes.enrich import enrich_node
from app.nodes.extract import extract_node
from app.nodes.score import score_node

SAMPLES = [
    "Hi, I'm Sarah from TechNova. We are a SaaS company with about 120 employees. We need enterprise pricing for your product. Email me at sarah@technova.com",
    "Hey, I'm a student doing a project. Can I get a discount?",
    "Hello, this is Bob from SmallShop. We have 5 employees and just want to know basic pricing. bob@smallshop.com",
]


def main():
    for text in SAMPLES:
        print(f"\n{'=' * 60}\n> INPUT: {text[:60]}...")

        # 1. Initialize state
        state = {"raw_inbound_text": text, "trace": []}

        # 2. Run Extract
        state.update(extract_node(state))

        # 3. Run Enrich
        enrich_result = enrich_node(state)
        state.update(enrich_result)

        # 4. Run Score
        state.update(score_node(state))

        print(
            f"  Extracted: {state.get('company_name')} | Intent: {state.get('intent')} | Budget: {state.get('budget_tier')}"
        )

        # Check if company_size exists before printing
        if "company_size" in state:
            print(
                f"  Enriched:  {state['company_size']} employees | Industry: {state['industry']}"
            )
        else:
            print(f"  Enriched:  FAILED - enrich_node returned {enrich_result}")

        print(
            f"  Score:     {state['lead_score']} | Qualified: {state['is_qualified']}"
        )
        print(f"  Reason:    {state['trace'][-1]['details']['reason']}")


if __name__ == "__main__":
    main()
