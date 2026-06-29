from researchgraph.graph.routing import route_after_reflection

def test_route_accept_when_reflection_accepts():
    state = {
        'budget': {'iteration': 0, 'max_iterations': 2},
        'reflection_decisions': [
            {
                'approved': True,
                'next_action': 'accept',
                'target_branch': None,
                'reason': 'good enough',
                'revised_instruction': None
            }
        ]
    }

    assert route_after_reflection(state) == 'accept'

def test_route_retry_dataset():
    state = {
        "budget": {"iteration": 0, "max_iterations": 2},
        "reflection_decisions": [
            {
                "approved": False,
                "next_action": "retry_branch",
                "target_branch": "dataset",
                "reason": "datasets weak",
                "revised_instruction": "Find more datasets"
            }
        ]
    }

    assert route_after_reflection(state) == 'retry_dataset'

def test_route_forced_finalize_when_iteration_limit_reached():
    state = {
        "budget": {"iteration": 2, "max_iterations": 2},
        "reflection_decisions": [
            {
                "approved": False,
                "next_action": "retry_branch",
                "target_branch": "literature",
                "reason": "weak literature",
                "revised_instruction": "retry"
            }
        ]
    }

    assert route_after_reflection(state) == 'forced_finalize'