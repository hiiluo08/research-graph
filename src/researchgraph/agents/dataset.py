from hashlib import sha1

from researchgraph.graph.state import ResearchState
from researchgraph.tools.dataset_sources import search_huggingface_datasets
from researchgraph.tools.literature_sources import SearchResult
from researchgraph.utils.dates import utc_now_iso

def dataset_node(state: ResearchState) -> dict:
    """ Dataset research agent node """
    task = next(task for task in state['branch_tasks'] if task['branch'] == 'dataset')
    results: list[SearchResult] = []

    for query in task['search_queries'][:3]:
        try:
            results.extend(search_huggingface_datasets(query, limit=2))
        except Exception as exc:
            results.append(
                SearchResult(
                    title='Dataset search warning',
                    url='https://example.com/dataset-search-warning',
                    snippet=f"HuggingFace dataset search failed for query '{query}': {exc}",
                    source_type='web',
                    score=0.0,
                    metadata={'warning': True}
                )
            )
    unique = _dedupe_results(results)[:state['budget']['max_sources_per_branch']]
    sources = [_source_from_result(result) for result in unique]
    findings = [
        {
            "finding_id": f"F_DATA_{index:03d}",
            "branch": "dataset",
            "task_id": task["task_id"],
            "claim": f"Dataset candidate found: {source['title']}",
            "evidence_summary": unique[index - 1].snippet[:500],
            "source_ids": [source["source_id"]],
            "confidence": 0.60 if not unique[index - 1].metadata.get("warning") else 0.2,
            "limitations": ["Dataset relevance must be manually verified"],
            "metadata": unique[index - 1].metadata,
        }
        for index, source in enumerate(sources, start=1)
    ]

    return {"dataset_findings": findings, "sources": sources}

def _dedupe_results(results: list[SearchResult]) -> list[SearchResult]:
    by_url = {}
    for result in results:
        by_url[result.url] = result
    return list(by_url.values())

def _source_from_result(result: SearchResult) -> dict:
    source_id = "SRC_" + sha1(result.url.encode("utf-8")).hexdigest()[:12]
    return {
        "source_id": source_id,
        "source_type": result.source_type,
        "title": result.title,
        "url": result.url,
        "canonical_url": result.url,
        "authors": [],
        "published_at": result.published_at,
        "accessed_at": utc_now_iso(),
        "doi": None,
        "venue": None,
        "license": result.metadata.get("license"),
        "metadata": result.metadata,
    }