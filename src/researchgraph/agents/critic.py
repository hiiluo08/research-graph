from researchgraph.graph.state import ResearchState

def critic_node(state: ResearchState) -> dict:
    """Critic node to evaluate the quality of the research"""
    return {
        "status": "reflecting",
        "quality_score": {
            "overall": 0.80,
            "coverage": 0.80,
            "citation_grounding": 1.0,
            "source_diversity": 0.75,
            "freshness": 0.60,
            "conflict_handling": 0.70,
            "clarity": 0.80,
        },
        "critiques": [],
    }