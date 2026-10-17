from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.nodes.approve import approval_node
from app.nodes.draft import draft_node
from app.nodes.enrich import enrich_node
from app.nodes.extract import extract_node
from app.nodes.finalize import finalize_node
from app.nodes.score import score_node
from app.state import LeadState


def route_after_scoring(state: LeadState) -> str:
    if state.get("is_qualified"):
        return "draft"
    return "end"


def route_after_approval(state: LeadState) -> str:
    # We always go to finalize (which handles both approved/rejected)
    return "finalize"


def build_graph():
    graph = StateGraph(LeadState)

    graph.add_node("extract", extract_node)
    graph.add_node("enrich", enrich_node)
    graph.add_node("score", score_node)
    graph.add_node("draft", draft_node)
    graph.add_node("human_approval", approval_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "extract")
    graph.add_edge("extract", "enrich")
    graph.add_edge("enrich", "score")

    graph.add_conditional_edges(
        "score", route_after_scoring, {"draft": "draft", "end": END}
    )
    graph.add_edge("draft", "human_approval")
    graph.add_edge("human_approval", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile(checkpointer=MemorySaver())


compiled_graph = build_graph()
