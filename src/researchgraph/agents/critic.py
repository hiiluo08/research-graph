from researchgraph.graph.state import ResearchState, QualityScore, Critique

def score_research_state(state: ResearchState) -> QualityScore:
    claims = state.get('synthesized_claims', [])
    sources = state.get('sources', [])
    source_types = {source['source_type'] for source in sources}

    citation_grounding = _ratio(
        sum(1 for claim in claims if claim.get('supporting_source_ids')),
        len(claims)
    )
    coverage = _ratio(
        sum(1 for key in ['literature_findings', 'dataset_findings', 'repository_findings']
        if state.get(key)),
        3
    )
    source_diversity = min(len(source_types) / 3, 1.0)
    freshness = 0.7
    conflict_handling = 0.7
    clarity = 0.8 if claims else 0.3

    overall = round(
        0.25 * coverage
        + 0.25 * citation_grounding
        + 0.15 * source_diversity
        + 0.15 * freshness
        + 0.10 * conflict_handling
        + 0.10 * clarity,
        2,
    )

    return {
        "overall": overall,
        "coverage": round(coverage, 2),
        "citation_grounding": round(citation_grounding, 2),
        "source_diversity": round(source_diversity, 2),
        "freshness": freshness,
        "conflict_handling": conflict_handling,
        "clarity": clarity,
    }

def build_critiques(state: ResearchState, score: QualityScore) -> list[Critique]:
    critiques: list[Critique] = []

    if not state.get('literature_findings'):
        critiques.append(_critique('literature', 'Literature findings are missing'))
    if not state.get('dataset_findings'):
        critiques.append(_critique('dataset', 'Dataset findings are missing'))
    if not state.get('repository_findings'):
        critiques.append(_critique('repository', 'Repository findings are missing'))
    if score['citation_grounding'] < 0.8:
        critiques.append(
            {
                'critique_id': 'CRIT_CITATION_001',
                'severity': 'high',
                'issue_type': 'citation_issue',
                'description': 'Some synthesized claims do not have supporting sources.',
                'target_branch': None,
                'recommended_action': 'Remove unsupported claims or find sources before writing the report.'
            }
        )
    
    return critiques

def critic_node(state: ResearchState) -> dict:
    """Critic node to evaluate the quality of the research"""
    score = score_research_state(state)
    return {
        'status': 'reflecting',
        'quality_score': score,
        'critiques': build_critiques(state, score)
    }

def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator

def _critique(branch: str, description: str) -> Critique:
    return {
        'critique_id': f'CRIT_{branch.upper()}_001',
        'severity': 'high',
        'issue_type': 'missing_evidence',
        'description': description,
        'target_branch': branch,
        'recommended_action': f'Retry {branch} research with broader search queries.'
    }