from researchgraph.graph.state import ResearchState

def planner_node(state: ResearchState) -> dict:
    """Planner node to plan the research"""
    query = state['user_query']

    return {
        'status': 'researching',
        'scope': {
            'normalized_query': query,
            'domain': 'technical research',
            'time_range': None,
            'must_cover': ['literature', 'datasets', 'repositories', 'research gaps'],
            'out_of_scope': ['clinical advice', 'unverified claims'],
            'assumptions': ['Use public sources only.']
        },
        'planner_output': {"mode": "stub"},
        'branch_tasks': [
            {
                'task_id': 'task_literature_001',
                'branch': 'literature',
                'objective': f'Find paper out {query}',
                'search_queries': [query, f"{query} survey", f"{query} recent paper"],
                'required_outputs': ["foundational papers", "recent papers"],
                'success_criteria': ["at least one paper-like source"],
                'retry_instruction': None,
            },
            {
                "task_id": "task_dataset_001",
                "branch": "dataset",
                "objective": f"Find datasets about {query}",
                "search_queries": [f"{query} dataset"],
                "required_outputs": ["related datasets"],
                "success_criteria": ["at least one dataset or limitation"],
                "retry_instruction": None,
            },
            {
                "task_id": "task_repository_001",
                "branch": "repository",
                "objective": f"Find repositories about {query}",
                "search_queries": [f"{query} GitHub"],
                "required_outputs": ["related repositories"],
                "success_criteria": ["at least one repository or limitation"],
                "retry_instruction": None,
            }
        ]
    }