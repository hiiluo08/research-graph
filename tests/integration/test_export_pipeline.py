from researchgraph.agents.report_writer import build_report_markdown

REQUIRED_SECTIONS = [
    "Executive Summary",
    "Scope and Assumptions",
    "Background Knowledge",
    "Key Concepts",
    "Literature Review",
    "Important Papers",
    "Related Datasets",
    "Related GitHub Repositories",
    "Current Challenges",
    "Research Gaps",
    "Future Research Directions",
    "Recommended Learning Roadmap",
    "Limitations",
    "References",
]


def test_report_contains_required_sections():
    state = {
        "scope": {
            "normalized_query": "Test Topic",
            "assumptions": ["Use public sources"],
            "out_of_scope": ["Unsupported claims"],
        },
        "synthesized_claims": [
            {
                "statement": "A literature claim",
                "category": "literature",
                "supporting_source_ids": ["src1"],
                "confidence": 0.8,
                "notes": [],
            }
        ],
        "citation_map": {"src1": "S1"},
        "sources": [
            {
                "source_id": "src1",
                "title": "Paper A",
                "url": "https://example.com/a",
                "authors": ["Author"],
                "published_at": "2024",
                "accessed_at": "2026-06-18T00:00:00+00:00",
                "venue": "arXiv",
                "doi": None,
                "source_type": "paper",
            }
        ],
        "quality_score": {"overall": 0.8},
        "critiques": [],
    }

    markdown = build_report_markdown(state)

    for section in REQUIRED_SECTIONS:
        assert f"## {section}" in markdown
    assert "[S1]" in markdown