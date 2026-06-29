from typing import Literal

from researchgraph.graph.state import ResearchState

Route = Literal['accept', 'retry_literature', 'retry_dataset', 'retry_repository', 'replan', 'forced_finalize']

def route_after_reflection(state: ResearchState) -> Route:
    budget = state['budget']
    latest_decision = state['reflection_decisions'][-1]

    if budget['iteration'] >= budget['max_iterations']:
        return 'forced_finalize'
    
    if latest_decision['next_action'] == 'accept':
        return 'accept'

    if latest_decision['next_action'] == 'replan':
        return 'replan'

    if latest_decision['next_action'] == 'retry_branch':
        target = latest_decision['target_branch']
        if target == 'literature':
            return 'retry_literature'
        if target == 'dataset':
            return 'retry_dataset'
        if target == 'repository':
            return 'retry_repository'

    return 'forced_finalize'