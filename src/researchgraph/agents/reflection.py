from researchgraph.graph.state import ResearchState, ReflectionDecision, BudgetState

ACCEPT_THRESHOLD = 0.78

def decide_next_action(state: ResearchState) -> ReflectionDecision:
    budget = state['budget']
    score = state['quality_score']['overall']

    if budget['iteration'] >= budget['max_iterations']:
        return {
            'approved': False,
            'next_action': 'forced_finalize',
            'target_branch': None,
            'reason': 'Maximum reflection iterations reached',
            'revised_instruction': None
        }

    if score >= ACCEPT_THRESHOLD and not _has_high_severity_critique(state):
        return {
            'approved': True,
            'next_action': 'accept',
            'target_branch': None,
            'reason': f'Quality score {score:.2f} meets threshold {ACCEPT_THRESHOLD:.2f}',
            'revised_instruction': None
        }

    for critique in state.get('critiques', []):
        target = critique.get('target_branch')
        if critique.get('severity') == 'high' and target in {'literature', 'dataset', 'repository'}:
            revised_instruction = critique.get('recommended_action')
            if not revised_instruction:
                recommend_legacy = critique.get('recommend_action')
                if isinstance(recommend_legacy, str):
                    revised_instruction = recommend_legacy
            return {
                'approved': False,
                'next_action': 'retry_branch',
                'target_branch': target,
                'reason': critique.get('description', ''),
                'revised_instruction': revised_instruction
            }

    return {
        'approved': False,
        'next_action': 'replan',
        'target_branch': None,
        'reason': f'Quality score {score:.2f} is below threshold and no single branch explains the issue',
        'revised_instruction': 'Create a narrower plan with more targeted search queries.'
    }

def reflection_node(state: ResearchState) -> dict:
    """Reflection node to evaluate the quality of the research"""
    budget: BudgetState = state['budget'].copy()
    decision = decide_next_action(state)
    budget['iteration'] += 1
    return {'budget': budget, 'reflection_decisions': [decision]}

def _has_high_severity_critique(state: ResearchState) -> bool:
    return any(c.get('severity') == 'high' for c in state.get('critiques', []))

