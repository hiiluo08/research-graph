from typing import Any

from researchgraph.graph.state import ResearchState


def reflection_node(state: ResearchState) -> dict:
    """Reflection node to evaluate the quality of the research"""
    budget: dict[str, Any] = dict(state["budget"])
    budget["iteration"] += 1
    score = state["quality_score"]["overall"]
    decision = {
        "approved": score >= 0.78,
        "next_action": "accept" if score >= 0.78 else "forced_finalize",
        "target_branch": None,
        "reason": f"Quality score is {score:.2f}",
        "revised_instruction": None,
    }
    return {"budget": budget, "reflection_decisions": [decision]}
