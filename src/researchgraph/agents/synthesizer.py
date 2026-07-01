from typing import cast

from researchgraph.graph.state import ClaimCategory, Finding, ResearchState, SynthesizedClaim

CATEGORY_BY_BRANCH: dict[str, ClaimCategory] = {
    "literature": "concept",
    "dataset": "evidence",
    "repository": "method",
}


def build_synthesized_claims(state: ResearchState) -> list[SynthesizedClaim]:
    findings: list[Finding] = (
        state.get("literature_findings", [])
        + state.get("dataset_findings", [])
        + state.get("repository_findings", [])
    )

    claims: list[SynthesizedClaim] = []
    for index, finding in enumerate(findings, start=1):
        source_ids = finding.get("source_ids", [])
        if not source_ids:
            continue
        claims.append(
            {
                "claim_id": f"C_{index:03d}",
                "statement": finding["claim"],
                "category": CATEGORY_BY_BRANCH.get(finding["branch"], "concept"),
                "supporting_source_ids": source_ids,
                "conflicting_source_ids": [],
                "confidence": finding["confidence"],
                "notes": finding.get("limitations", []),
            }
        )

    if claims:
        claims.insert(
            0,
            {
                "claim_id": "C_BACKGROUND_001",
                "statement": "The topic should be understood through literature, dataset availability, repository maturity, current challenges, and research gaps.",
                "category": "background",
                "supporting_source_ids": claims[0]["supporting_source_ids"],
                "conflicting_source_ids": [],
                "confidence": 0.7,
                "notes": ["Generated as a structural background claim from available evidence"],
            },
        )

    return claims


def synthesis_node(state: ResearchState) -> dict:
    """Synthesizer node to synthesize findings from all branches"""
    return {"status": "critiquing", "synthesized_claims": build_synthesized_claims(state)}
