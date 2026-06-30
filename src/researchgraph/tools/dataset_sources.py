import httpx

from researchgraph.tools.literature_sources import SearchResult


def search_huggingface_datasets(query: str, limit: int = 5) -> list[SearchResult]:
    response = httpx.get(
        'https://huggingface.co/api/datasets',
        params={'search': query, 'limit': limit},
        timeout=20
    )

    response.raise_for_status()
    data = response.json()

    results: list[SearchResult] = []

    for item in data[:limit]:
        dataset_id = item.get('id') or item.get('_id')
        if not dataset_id:
            continue
        results.append(
            SearchResult(
                title=dataset_id,
                url=f'https://huggingface.co/datasets/{dataset_id}',
                snippet=f'Hugging Face dataset: {dataset_id}',
                source_type='dataset',
                published_at=item.get("createdAt"),
                score=float(item.get('downloads', 0) or 0),
                metadata={
                    'provider': 'huggingface',
                    'downloads': item.get('downloads'),
                    'likes': item.get('likes'),
                    'tags': item.get('tags', [])
                }
            )
        )
    return results