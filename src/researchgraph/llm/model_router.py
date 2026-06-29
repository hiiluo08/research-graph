from researchgraph.config import Settings


def model_for_role(role: str, settings: Settings) -> str:
    if role == "planner":
        return settings.model_planner
    if role in {"literature", "dataset", "repository", "research"}:
        return settings.model_research
    if role == "synthesizer":
        return settings.model_synthesizer
    if role == "critic":
        return settings.model_critic
    if role == "citation":
        return settings.model_citation
    if role == "report_writer":
        return settings.model_report_writer
    return settings.model_research