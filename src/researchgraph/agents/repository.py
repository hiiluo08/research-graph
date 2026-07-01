from hashlib import sha1

from researchgraph.graph.state import ResearchState
from researchgraph.tools.repository_sources import search_github_repos
from researchgraph.tools.literature_sources import SearchResult
from researchgraph.utils.dates import utc_now_iso

def repository_node(state: ResearchState) -> dict:
    task = next(task for task in state["branch_tasks"] if task["branch"] == "repository")
    results: list[SearchResult] = []

    for query in task["search_queries"][:3]:
        try:
            results.extend(search_github_repos(query, limit=2))
        except Exception as exc:
            results.append(
                SearchResult(
                    title="Repository search warning",
                    url="https://example.com/repository-search-warning",
                    snippet=f"GitHub search failed for query '{query}': {exc}",
                    source_type="web",
                    score=0.0,
                    metadata={"warning": True},
                )
            )

    unique = _dedupe_results(results)[: state["budget"]["max_sources_per_branch"]]
    sources = [_source_from_result(result) for result in unique]
    findings = [
        {
            "finding_id": f"F_REPO_{index:03d}",
            "branch": "repository",
            "task_id": task["task_id"],
            "claim": f"Repository candidate found: {source['title']}",
            "evidence_summary": unique[index - 1].snippet[:500],
            "source_ids": [source["source_id"]],
            "confidence": _repo_confidence(unique[index - 1]),
            "limitations": [] if not unique[index - 1].metadata.get("warning") else ["GitHub search warning"],
            "metadata": unique[index - 1].metadata,
        }
        for index, source in enumerate(sources, start=1)
    ]

    return {"repository_findings": findings, "sources": sources}


def _repo_confidence(result: SearchResult) -> float:
    if result.metadata.get("warning"):
        return 0.2
    stars = result.metadata.get("stars", 0) or 0
    if stars >= 1000:
        return 0.80
    if stars >= 100:
        return 0.70
    return 0.55


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