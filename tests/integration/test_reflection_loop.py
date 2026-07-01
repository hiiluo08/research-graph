from researchgraph.agents.reflection import decide_next_action

def test_reflection_accepts_high_score():
    state = {
        'budget': {'iteration': 0, 'max_iterations': 2},
        'quality_score': {'overall': 0.85},
        'critiques': []
    }

    decision = decide_next_action(state)
    
    assert decision['approved'] is True
    assert decision['next_action'] == 'accept'

def test_reflection_retries_target_branch_from_high_severity_critique():
    state = {
        'budget': {'iteration': 0, 'max_iterations': 2},
        'quality_score': {'overall': 0.65},
        'critiques': [
            {
                'severity': 'high',
                'target_branch': 'dataset',
                'description': 'Dataset evidence missing',
                'recommend_action': 'Retry dataset search'
            }
        ]
    }

    decision = decide_next_action(state)

    assert decision['approved'] is False
    assert decision['next_action'] == 'retry_branch'
    assert decision['target_branch'] == 'dataset'

def test_reflection_forces_finalize_when_iteration_limit_reached():
    state = {
        'budget': {'iteration': 2, 'max_iterations': 2},
        'quality_score': {'overall': 0.40},
        'critiques': []
    }

    decision = decide_next_action(state)

    assert decision['next_action'] == 'forced_finalize'