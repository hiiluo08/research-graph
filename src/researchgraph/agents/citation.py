from researchgraph.graph.state import ResearchState, SourceRecord
from researchgraph.tools.citation_tools import extract_citation_labels

def build_citation_map(sources: list[SourceRecord]) -> dict[str, str]:
    return {source['source_id']: f'S{index}' for index, source in enumerate(sources, start=1)}

def format_reference(label:str, source: SourceRecord) -> str:
    authors = ', '.join(source.get('authors') or []) or 'Unknown author'
    title = source.get('title') or 'Untitled source'
    venue = source.get('venue') or source.get('source_type') or 'Source'
    published = source.get('published_at') or 'n.d.'
    url = source.get('url') or source.get('canonical_url') or ''
    doi = source.get('doi')
    doi_text = f'DOI: {doi}.' if doi else ''
    return f"[{label}] {authors}. \"{title}.\" {venue}, {published}.{doi_text} {url}"

def citation_normalize_node(state: ResearchState) -> dict:
    """Normalize citation map for report writer"""
    return {"citation_map": build_citation_map(state.get("sources", [])), "status": "writing"}


def citation_check_node(state: ResearchState) -> dict:
    """Check if all citations are valid"""
    markdown = state['report_markdown']
    known_labels = set(state.get('citation_map', {}).values())
    used_labels = set(extract_citation_labels(markdown))
    missing = sorted(used_labels - known_labels)

    if missing:
        warning = "\n\n## Citation Warnings\n\n" + "\n".join(
            f"- Citation label [{label}] was used but not found in citation_map." for label in missing
        )
        markdown = markdown + warning
    
    return {"report_markdown": markdown}