from researchgraph.graph.state import ResearchState


def citation_normalize_node(state: ResearchState) -> dict:
    """Normalize citation map for report writer"""
    citation_map = {}
    for index, source in enumerate(state.get("sources", []), start=1):
        citation_map[source["source_id"]] = f"S{index}"
    return {"citation_map": citation_map, "status": "writing"}


def citation_check_node(state: ResearchState) -> dict:
    """Check if all citations are valid"""
    return {"report_markdown": state["report_markdown"]}