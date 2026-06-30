import httpx

from researchgraph.tools.literature_sources import SearchResult


def search_github_repos(query: str, limit: int = 5) -> list[SearchResult]:
    response = httpx.get(
        'https://api.github.com/search/repositories',
        params={'q': query, 'sort': 'stars', 'order': 'desc', 'per_page': limit},
        headers={'Accept': 'application/vnd.github+json'},
        timeout=20
    )

    response.raise_for_status()
    data = response.json()

    results: list[SearchResult] = []

    for item in data.get('items', [])[:limit]:
        results.append(
            SearchResult(
                title=item['full_name'],
                url=item['html_url'],
                snippet=item.get('description') or '',
                source_type='repository',
                published_at=item.get('created_at'),
                score=float(item.get('stargazers_count', 0)),
                metadata={
                    'provider': 'github',
                    'stars': item.get('stargazers_count', 0),
                    'forks': item.get('forks_count', 0),
                    'updated_at': item.get('updated_at'),
                    'published_at': item.get('created_at'),
                    'language': item.get('language'),
                    'license': (item.get('license') or {}).get('spdx_id')
                }
            )
        )

    return results
    