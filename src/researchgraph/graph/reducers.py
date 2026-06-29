from collections.abc import Callable
from typing import Any


def keep_latest(old: Any, new: Any) -> Any:
    return new

def merge_dict(old: dict | None, new: dict | None) -> dict:
    merge = dict(old or {})
    merge.update(new or {})
    return merge

def append_unique_by_id(key: str) -> Callable[[list[dict] | None, list[dict] | None], list[dict]]:
    def reducer(old: list[dict] | None, new: list[dict] | None) -> list[dict]:
        by_id: dict[str, dict] = {}
        anonymous_index = 0

        for item in old or []:
            item_id = item.get(key)
            if item_id is None:
                item_id = f'anonymous-old-{anonymous_index}'
                anonymous_index += 1
            by_id[str(item_id)] = item
        
        for item in new or []:
            item_id = item.get(key)
            if item_id is None:
                item_id = f'anonymous-new-{anonymous_index}'
                anonymous_index += 1
            by_id[str(item_id)] = item

        return list(by_id.values())

    return reducer

def merge_sources_by_id(old: list[dict] | None, new: list[dict] | None) -> list[dict]:
    by_key: dict[str, dict] = {}
    
    for source in old or []:
        key = _source_key(source)
        by_key[key] = source

    for source in new or []:
        key = _source_key(source)
        if key in by_key:
            merged = dict(by_key[key])
            for field, value in source.items():
                if value not in (None, "", []):
                    merged[field] = value
            by_key[key] = merged
        else:
            by_key[key] = source

    return list(by_key.values())


def _source_key(source: dict) -> str:
    """ Canonical key for a source """
    return str(
        source.get('source_id')
        or source.get('canonical_url')
        or source.get('url')
        or source.get('title')
    )
