from typing import Literal, cast

from pydantic import BaseModel, Field

from researchgraph.graph.state import BranchTask, ResearchScope, ResearchState


class BranchTaskModel(BaseModel):
    task_id: str
    branch: Literal["literature", "dataset", "repository"]
    objective: str
    search_queries: list[str] = Field(min_length=1)
    required_outputs: list[str] = Field(min_length=1)
    success_criteria: list[str] = Field(min_length=1)
    retry_instruction: str | None = None


class PlannerOutput(BaseModel):
    normalized_query: str
    domain: str
    time_range: str | None = None
    must_cover: list[str]
    out_of_scope: list[str]
    assumptions: list[str]
    branch_tasks: list[BranchTaskModel]


def build_fallback_plan(query: str) -> PlannerOutput:
    return PlannerOutput(
        normalized_query=query.strip(),
        domain="technical research",
        time_range=None,
        must_cover=[
            "Executive summary",
            "Background knowledge",
            "Key concepts",
            "Literature review",
            "Important papers",
            "Related datasets",
            "Related GitHub repositories",
            "Current challenges",
            "Research gaps",
            "Future directions",
            "Learning roadmap",
        ],
        out_of_scope=[
            "Unsupported medical or legal advice",
            "Claims without cited sources",
            "Exhaustive crawling beyond the configured budget",
        ],
        assumptions=[
            "Use public web-accessible sources only",
            "Prefer authoritative sources over blogs",
            "State limitations when evidence is weak",
        ],
        branch_tasks=[
            BranchTaskModel(
                task_id="task_literature_001",
                branch="literature",
                objective=f"Find foundational, survey, and recent papers about {query}",
                search_queries=[
                    query,
                    f"{query} survey paper",
                    f"{query} review",
                    f"{query} benchmark",
                    f"{query} recent arxiv",
                ],
                required_outputs=["foundational papers", "survey papers", "recent works"],
                success_criteria=["Return at least 3 paper-like sources or explain the gap"],
            ),
            BranchTaskModel(
                task_id="task_dataset_001",
                branch="dataset",
                objective=f"Find datasets directly or indirectly related to {query}",
                search_queries=[
                    f"{query} dataset",
                    f"{query} benchmark dataset",
                    f"{query} public dataset",
                    f"{query} data repository",
                ],
                required_outputs=["dataset candidates", "license/access notes", "limitations"],
                success_criteria=["Return direct datasets or clearly labeled proxy datasets"],
            ),
            BranchTaskModel(
                task_id="task_repository_001",
                branch="repository",
                objective=f"Find GitHub repositories and implementations related to {query}",
                search_queries=[
                    f"{query} GitHub",
                    f"{query} implementation",
                    f"{query} code",
                    f"{query} repository",
                ],
                required_outputs=["repository candidates", "maintenance signals", "quality notes"],
                success_criteria=["Return repositories or explain why no reliable implementation was found"],
            ),
        ],
    )


def planner_node(state: ResearchState) -> dict:
    query = state["user_query"]
    plan = build_fallback_plan(query)

    scope: ResearchScope = {
        "normalized_query": plan.normalized_query,
        "domain": plan.domain,
        "time_range": plan.time_range,
        "must_cover": plan.must_cover,
        "out_of_scope": plan.out_of_scope,
        "assumptions": plan.assumptions,
    }

    branch_tasks = cast(list[BranchTask], [task.model_dump() for task in plan.branch_tasks])

    return {
        "status": "researching",
        "scope": scope,
        "planner_output": plan.model_dump(),
        "branch_tasks": branch_tasks,
    }
