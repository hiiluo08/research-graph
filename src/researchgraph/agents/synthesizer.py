from researchgraph.graph.state import ResearchState

def synthesis_node(state: ResearchState) -> dict:
    """Synthesizer node to synthesize findings from all branches"""
    findings = (
        state.get('literature_findings', [])
        + state.get('dataset_findings', [])
        + state.get('repository_findings', [])
    )

    claims = []

    for index, finding in enumerate(findings, start=1):
        claims.append(
            {
                "claim_id": f"C_STUB_{index}",
                "statement": finding["claim"],
                "category": finding["branch"],
                "supporting_source_ids": finding["source_ids"],
                "conflicting_source_ids": [],
                "confidence": finding["confidence"],
                "notes": finding["limitations"],
            }
        )
    return {"status": "critiquing", "synthesized_claims": claims}