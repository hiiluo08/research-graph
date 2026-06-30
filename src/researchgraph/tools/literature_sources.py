import xml.etree.ElementTree as ET

import httpx
from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source_type: str
    published_at: str | None = None
    score: float = 0.0
    metadata: dict = {}

def search_arxiv(query: str, limit: int = 5) -> list[SearchResult]:
    params = {
        'search_query': f'all: {query}',
        'start': 0,
        'max_results': limit,
        'sortBy': 'relevance',
        'sortOrder': 'descending'
    }

    response = httpx.get('https://export.arxiv.org/api/query', params=params, timeout=20)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
    
    results: list[SearchResult] = []

    for entry in root.findall('atom:entry', namespace):
        title = ' '.join((entry.findtext('atom:title', default='', namespaces=namespace)).split())
        summary = " ".join((entry.findtext("atom:summary", default="", namespaces=namespace)).split())
        url = entry.findtext('atom:id', default='', namespaces=namespace)
        published = entry.findtext('atom:published', default=None, namespaces=namespace)
        authors = [
            author.findtext('atom:name', default='', namespaces=namespace)
            for author in entry.findall('atom:author', namespace)
        ]
        if title and url:
            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    snippet=summary[:1000],
                    source_type='paper',
                    published_at=published,
                    score=1.0,
                    metadata={'authors': authors, 'provider': 'arxiv'}
                )
            )
    return results