from researchgraph.graph.reducers import (
    append_unique_by_id,
    keep_latest,
    merge_dict,
    merge_sources_by_id,
)


def test_keep_latest_replaces_old_value():
    assert keep_latest('old', 'new') == 'new'

def test_merge_dict_updates_without_losing_old_values():
    old = {'a': 1, 'b': 2}
    new = {'b': 3, 'c': 4}
    expected = {'a': 1, 'b': 3, 'c': 4}
    assert merge_dict(old, new) == expected

def test_append_unique_by_id_replaces_duplicate_id():
    reducer = append_unique_by_id('finding_id')

    old = [{'finding_id': 'f1', 'claim': 'old'}]
    new = [
        {'finding_id': 'f1', 'claim': 'new'},
        {'finding_id': 'f2', 'claim': 'second'}
    ]

    expected = [
        {'finding_id': 'f1', 'claim': 'new'},
        {'finding_id': 'f2', 'claim': 'second'}
    ]

    assert reducer(old, new) == expected

def test_merge_sources_by_id_deduplicates_and_preserves_existing_metadata():
    old = [
        {
            "source_id": "s1",
            "title": "Old title",
            "url": "https://example.com/a",
            "canonical_url": "https://example.com/a",
            "doi": None,
        }
    ]

    new = [
        {
            "source_id": "s1",
            "title": "New title",
            "url": "https://example.com/a",
            "canonical_url": "https://example.com/a",
            "doi": "10.123/example",
        }
    ]

    expected = [
        {
            "source_id": "s1",
            "title": "New title",
            "url": "https://example.com/a",
            "canonical_url": "https://example.com/a",
            "doi": "10.123/example",
        }
    ]

    assert merge_sources_by_id(old, new) == expected