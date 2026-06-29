from researchgraph.graph.state import ResearchState
from researchgraph.utils.dates import utc_now_iso

def literature_node(state: ResearchState) -> dict:
    """Literature research agent node"""
    source = {
        'source_id': 'S_LIT_STUB',
        'source_type': 'paper',
        'title': 'Stub literature source',
        'url': 'https://example.com/literature',
        'canonical_url': 'https://example.com/literature',
        'authors': ['ResearchGraph'],
        'published_at': None,
        'accessed_at': utc_now_iso(),
        'doi': None,
        'venue': None,
        'license': None,
        'metadata': {'stub': True},
    }
    finding = {
        'finding_id': 'F_LIT_STUB',
        'branch': 'literature',
        'task_id': 'task_literature_001',
        'claim': 'The topic has relevant literature that should be reviewed.',
        'evidence_summary': 'Stub evidence for graph integration.',
        'source_ids': ['S_LIT_STUB'],
        'confidence': 0.5,
        'limitations': ['Stub data'],
        'metadata': {'stub': True},
    }
    return {'literature_findings': [finding], 'sources': [source]}