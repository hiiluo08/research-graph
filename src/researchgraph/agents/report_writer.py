from collections import defaultdict

from researchgraph.agents.citation import format_reference
from researchgraph.graph.state import ResearchState


def build_report_markdown(state: ResearchState) -> str:
    title = state["scope"]["normalized_query"]
    claims_by_category = defaultdict(list)
    for claim in state.get("synthesized_claims", []):
        claims_by_category[claim["category"]].append(claim)

    references = []
    citation_map = state.get("citation_map", {})
    for source in state.get("sources", []):
        label = citation_map.get(source["source_id"])
        if label:
            references.append(format_reference(label, source))

    return "\n".join(
        [
            f"# {title}",
            "",
            "## Executive Summary",
            _bullets(_top_claims(state, limit=5)),
            "",
            "## Scope and Assumptions",
            _bullets(state.get("scope", {}).get("assumptions", [])),
            "",
            "## Background Knowledge",
            _claim_bullets(claims_by_category["background"], citation_map),
            "",
            "## Key Concepts",
            _claim_bullets(claims_by_category["concept"], citation_map),
            "",
            "## Literature Review",
            _claim_bullets(claims_by_category["literature"], citation_map),
            "",
            "## Important Papers",
            _source_table(state, "paper"),
            "",
            "## Related Datasets",
            _source_table(state, "dataset"),
            "",
            "## Related GitHub Repositories",
            _source_table(state, "repository"),
            "",
            "## Current Challenges",
            _claim_bullets(claims_by_category["challenge"], citation_map),
            "",
            "## Research Gaps",
            _claim_bullets(claims_by_category["research_gap"], citation_map),
            "",
            "## Future Research Directions",
            _claim_bullets(claims_by_category["future_direction"], citation_map),
            "",
            "## Recommended Learning Roadmap",
            _learning_roadmap(title),
            "",
            "## Limitations",
            _limitations(state),
            "",
            "## References",
            "\n".join(references) if references else "No references available.",
            "",
        ]
    )


def report_writer_node(state: ResearchState) -> dict:
    return {"report_markdown": build_report_markdown(state), "status": "exporting"}


def _top_claims(state: ResearchState, limit: int) -> list[str]:
    claims = sorted(state.get("synthesized_claims", []), key=lambda item: item.get("confidence", 0), reverse=True)
    return [claim["statement"] for claim in claims[:limit]] or ["Insufficient evidence was collected to produce strong conclusions."]


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- No information available."


def _claim_bullets(claims: list[dict], citation_map: dict[str, str]) -> str:
    if not claims:
        return "- No strong evidence found in this category."
    lines = []
    for claim in claims:
        labels = [citation_map.get(source_id, source_id) for source_id in claim.get("supporting_source_ids", [])]
        citations = " ".join(f"[{label}]" for label in labels)
        lines.append(f"- {claim['statement']} {citations}".strip())
    return "\n".join(lines)


def _source_table(state: ResearchState, source_type: str) -> str:
    sources = [source for source in state.get("sources", []) if source.get("source_type") == source_type]
    citation_map = state.get("citation_map", {})
    if not sources:
        return "No sources found for this category."

    rows = ["| Source | Notes | Citation |", "|---|---|---|"]
    for source in sources:
        label = citation_map.get(source["source_id"], source["source_id"])
        notes = source.get("metadata", {})
        note_text = ", ".join(f"{key}: {value}" for key, value in list(notes.items())[:3])
        rows.append(f"| {source['title']} | {note_text or 'No metadata'} | [{label}] |")
    return "\n".join(rows)


def _learning_roadmap(title: str) -> str:
    return "\n".join(
        [
            f"1. Learn the core concepts behind {title}.",
            "2. Read the foundational papers listed in this report.",
            "3. Reproduce one open-source implementation or tutorial.",
            "4. Inspect available datasets and understand their limitations.",
            "5. Identify one research gap and design a small experiment.",
        ]
    )


def _limitations(state: ResearchState) -> str:
    critiques = state.get("critiques", [])
    lines = ["- This report is generated from public sources within a fixed cost and search budget."]
    lines.extend(f"- {critique['description']}" for critique in critiques)
    return "\n".join(lines)