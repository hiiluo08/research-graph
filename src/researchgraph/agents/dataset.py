from researchgraph.graph.state import ResearchState
from researchgraph.utils.dates import utc_now_iso

def dataset_node(state: ResearchState) -> dict:
    """Dataset research agent node"""
    source = {
        'source_id': 'S_DATA_STUB',
        'source_type': 'dataset',
        'title': 'Stub dataset source',
        'url': 'https://example.com/dataset',
        'canonical_url': 'https://example.com/dataset',
        'authors': ['ResearchGraph'],
        'published_at': None,
        'accessed_at': utc_now_iso(),
        'doi': None,
        'venue': None,
        'license': 'unknown',
        'metadata': {'stub': True},
    }
    finding = {
        'finding_id': 'F_DATA_STUB',
        'branch': 'dataset',
        'task_id': 'task_dataset_001',
        'claim': 'The topic may require direct or proxy datasets.',
        'evidence_summary': 'Stub dataset evidence for graph integration.',
        'source_ids': ['S_DATA_STUB'],
        'confidence': 0.5,
        'limitations': ['Stub data'],
        'metadata': {'stub': True},
    }
    return {'dataset_findings': [finding], 'sources': [source]}