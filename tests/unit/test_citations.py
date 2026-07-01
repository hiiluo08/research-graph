from researchgraph.tools.literature_sources import SearchResult
from researchgraph.agents.citation import build_citation_map, format_reference


def test_search_result_requires_title_and_url():
    result = SearchResult(
        title='A paper',
        url='https://example.com/paper',
        snippet='Short summary',
        source_type='paper',
        pushblished_at=None,
        score=1.0,
        metadata={'doi': '10.123/example'}
    )

    assert result.title == 'A paper'
    assert result.source_type == 'paper'
    assert result.metadata['doi'] == '10.123/example'

def test_build_citation_map_is_stable_by_input_order():
    sources = [
        {"source_id": "src_a", "title": "A", "url": "https://a.com"},
        {"source_id": "src_b", "title": "B", "url": "https://b.com"},
    ]

    assert build_citation_map(sources) == {"src_a": "S1", "src_b": "S2"}


def test_format_reference_contains_label_title_and_url():
    reference = format_reference(
        "S1",
        {
            "source_id": "src_a",
            "title": "A Paper",
            "url": "https://a.com",
            "authors": ["Ada Lovelace"],
            "published_at": "2024-01-01",
            "accessed_at": "2026-06-18T00:00:00+00:00",
            "venue": "arXiv",
            "doi": None,
        },
    )

    assert reference.startswith("[S1]")
    assert "A Paper" in reference
    assert "https://a.com" in reference