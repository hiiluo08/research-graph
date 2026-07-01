from hashlib import sha1

from researchgraph.graph.state import BranchTask, ResearchState
from researchgraph.tools.literature_sources import SearchResult, search_arxiv
from researchgraph.utils.dates import utc_now_iso

def literature_node(state: ResearchState) -> dict:
    """Literature research agent node"""
    task = next(task for task in state['branch_tasks'] if task['branch'] == 'literature')
    results: list[SearchResult] = []

    for query in task['search_queries'][:3]:
        try:
            results.extend(search_arxiv(query, limit=2))
        except Exception as exc:
            results.append(
                SearchResult(
                    title='Literature search warning',
                    url='https://example.com/literature-search-warning',
                    snippet=f"arXiv search failed for query '{query}': {exc}",
                    source_type='web',
                    score=0.0,
                    metadata={'warning': True}
                )
            )
    
    unique = _dedupe_results(results)[:state['budget']['max_sources_per_branch']]
    sources = [_source_from_result(result) for result in unique]

    findings = [
        {
            'finding_id': f'F_LIT_{index:03d}',
            'branch': 'literature',
            'task_id': task['task_id'],
            'claim': f"Relevant literature source found: {source['title']}",
            'evidence_summary': unique[index-1].snippet[:500],
            'source_ids': [source['source_id']],
            'confidence': 0.65 if not unique[index - 1].metadata.get('warning') else 0.2,
            'limitations': [] if not unique[index-1].metadata.get('warning') else ['Search tool warning'],
            'metadata': unique[index-1].metadata
        }
        for index, source in enumerate(sources, start=1)
    ]
    return {'literature_findings': findings, 'sources': sources}


def _dedupe_results(results: list[SearchResult]) -> list[SearchResult]:
    by_url = {}
    for result in results:
        by_url[result.url] = result
    return list(by_url.values())

def _source_from_result(result: SearchResult) -> dict:
    source_id = 'SRC_' + sha1(result.url.encode('utf-8')).hexdigest()[:12]
    return {
        'source_id': source_id,
        'source_type': result.source_type,
        'title': result.title,
        'url': result.url,
        'canonical_url': result.url,
        'authors': result.metadata.get('authors') or [],
        'published_at': result.published_at,
        'accessed_at': utc_now_iso(),
        'doi': result.metadata.get('doi'),
        'venue': result.metadata.get('venue'),
        'license': result.metadata.get('license'),
        'metadata': result.metadata
    }