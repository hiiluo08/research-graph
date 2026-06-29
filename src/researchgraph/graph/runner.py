from researchgraph.config import get_settings
from researchgraph.graph.builder import build_research_graph
from researchgraph.graph.state import ResearchState
from researchgraph.utils.ids import new_run_id

from typing import cast

def run_research(query: str) -> ResearchState:
    settings = get_settings()
    run_id = new_run_id()

    initial_state = cast(ResearchState, {
        'run_id': run_id,
        'user_query': query,
        'status': 'created',
        'budget': {
            'max_cost_usd': settings.max_cost_per_run_usd,
            'estimated_cost_usd': 0.0,
            'max_iterations': settings.max_reflection_iterations,
            'iteration': 0,
            'max_sources_per_branch': settings.max_sources_per_branch,
            'max_tool_calls_per_branch': settings.max_tool_calls_per_branch,
            'max_fetch_chars_per_source': settings.max_fetch_chars_per_source
        }
    })

    graph = build_research_graph()
    return graph.invoke(initial_state)