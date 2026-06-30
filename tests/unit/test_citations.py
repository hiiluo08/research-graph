from researchgraph.tools.literature_sources import SearchResult


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