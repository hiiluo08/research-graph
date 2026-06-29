from researchgraph.graph.state import ResearchState
from researchgraph.utils.dates import utc_now_iso

def repository_node(state: ResearchState) -> dict:
    """Repository research agent node"""
    source = {
        'source_id': 'S_REPO_STUB',
        'source_type': 'repository',
        'title': 'Stub repository source',
        'url': 'https://github.com/example/repo',
        'canonical_url': 'https://github.com/example/repo',
        'authors': ['ResearchGraph'],
        'published_at': None,
        'accessed_at': utc_now_iso(),
        'doi': None,
        'venue': None,
        'license': 'unknown',
        'metadata': {'stars': 0, 'stub': True},
    }
    finding = {
        'finding_id': 'F_REPO_STUB',
        'branch': 'repository',
        'task_id': 'task_repository_001',
        'claim': 'Repository quality should be evaluated by relevance, maintenance, and documentation.',
        'evidence_summary': 'Stub repository evidence for graph integration.',
        'source_ids': ['S_REPO_STUB'],
        'confidence': 0.5,
        'limitations': ['Stub data'],
        'metadata': {'stub': True},
    }
    return {'repository_findings': [finding], 'sources': [source]}