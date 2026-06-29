from __future__ import annotations

import operator
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from .reducers import append_unique_by_id, keep_latest, merge_dict, merge_sources_by_id

BranchName = Literal['literature', 'dataset', 'repository']
SourceType = Literal['paper', 'dataset', 'repository', 'web', 'documentation', 'other']
RunStatus = Literal[
    # Lifecycle
    "created",
    "queued",
    "initializing",
    "validating",

    # Execution
    "planning",
    "researching",
    "synthesizing",
    "critiquing",
    "revising",
    "writing",
    "exporting",

    # Recovery
    "retrying",

    # Terminal
    "completed",
    "failed",
    "cancelled",
    "timed_out",
]
ClaimCategory = Literal[
    # Context
    "background",
    "motivation",
    "definition",

    # Knowledge
    "concept",
    "architecture",
    "method",

    # Evidence
    "finding",
    "evidence",
    "benchmark",

    # Analysis
    "comparison",
    "insight",
    "implication",

    # Evaluation
    "strength",
    "limitation",
    "risk",

    # Research
    "research_gap",
    "future_direction",

    # Practical
    "application",
    "recommendation",

    # Consensus
    "consensus",
    "controversy",
]
SeverityLevel = Literal['low', 'medium', 'high', 'critical']
IssueType = Literal[
    # Evidence
    "missing_evidence",
    "weak_evidence",
    "conflicting_evidence",

    # Logic
    "unsupported_claim",
    "logical_gap",
    "overgeneralization",

    # Completeness
    "missing_context",
    "incomplete_analysis",
    "missing_counterargument",

    # Accuracy
    "factual_error",
    "misinterpretation",

    # Quality
    "ambiguity",
    "redundancy",
    "irrelevance",

    # Structure
    "poor_organization",

    # Citation
    "citation_issue",

    # Confidence
    "low_confidence",
]

class BudgetState(TypedDict):
    max_cost_usd: float             # Maximum allowed API spend
    estimated_cost_usd: float       # Current estimated cost
    max_iterations: int             # Maximum number of reflection cycles
    iteration: int                  # Current iteration number
    max_sources_per_branch: int     # Maximum sources per branch
    max_tool_calls_per_branch: int  # Maximum tool calls per branch
    max_fetch_chars_per_source: int # Text limit for crawled content (default: 12000)

class ResearchScope(TypedDict):
    normalized_query: str       # The cleaned search query
    domain: str                 # Domain categorization (e.g. computer science, biology,...)
    time_range: str | None      # Optional temporal boundary
    must_cover: list[str]       # Required themes/subtopics
    out_of_scope: list[str]     # Topics to ignore/avoid
    assumptions: list[str]      # Starting assumptions

class BranchTask(TypedDict):
    task_id: str                    # Unique identifier
    branch: BranchName              # Target branch (literature, dataset or repository)
    objective: str                  # Plain-text objective
    search_queries: list[str]       # Recommended search queries
    required_output: list[str]      # Expected outputs to deliver
    success_criteria: list[str]     # Rubric criteria for the agent
    retry_instruction: str | None   # Guidance if the task failed quality checks

class SourceRecord(TypedDict):
    source_id: str              # Unique reference ID (e.g. arXiv identifier, URL hash)
    source_type: SourceType     # paper, dataset, repository, web, documentation, other
    title: str                  # Title of the source
    url: str                    # URL of the source
    canonical_url: str          # Canonical URL of the source
    authors: list[str]          # List of authors
    published_at: str | None    # Date published
    accessed_at: str            # Date accessed
    doi: str | None             # Digital Object Identifier (if applicable)
    venue: str | None           # Publication venue (journal, conference)
    license: str | None         # License information
    metadata: dict              # Additional fields (downloads, stars, etc.)

class Finding(TypedDict):
    finding_id: str         # Unique ID for finding
    branch: BranchName      # Branch that produced the finding
    task_id: str            # Task that produced the finding
    claim: str              # Claim made by the finding
    evidence_summary: str   # Summary of evidence supporting the claim
    source_ids: list[str]   # List of source IDs supporting the claim
    confidence: float       # Confidence score (0-1)
    limitations: list[str]  # Limitations of the finding
    metadata: dict          # Additional fields (e.g. metrics, insights)

class SynthesizedClaim(TypedDict):
    claim_id: str                       # Unique ID for claim
    statement: str                      # Claim statement
    category: ClaimCategory             # Category of the claim
    supporting_source_ids: list[str]    # List of source IDs supporting the claim
    conficting_source_ids: list[str]    # List of source IDs conflicting with the claim
    confidence: float                   # Confidence score (0-1)
    notes: list[str]                    # Additional notes

class QualityScore(TypedDict):
    overall: float              # Overall quality score (0-1)
    coverage: float             # Coverage score
    citation_grounding: float   # Citation grounding score
    source_diversity: float     # Source diversity score
    freshness: float            # Freshness score
    conflict_handling: float    # Conflict handling score
    clarity: float              # Clarity score

class Critique(TypedDict):
    critique_id: str                    # Unique ID for critique
    severity: SeverityLevel             # Severity level of critique
    issue_type: IssueType               # Type of issue
    description: str                    # Description of issue
    target_branch: BranchName | None    # Target branch of critique
    recommend_action: str               # Recommended action

class ReflectionDecision(TypedDict):
    approved: bool                   # Whether reflection passed or failed
    next_action: Literal['accept', 'retry_branch', 'replan', 'forced_finalized']  # Next action
    target_branch: BranchName | None # Target branch of critique
    reason: str                      # Reason for decision
    revised_instruction: str | None  # Revised instruction for next action

class ExportPaths(TypedDict):
    markdown: str | None     # Path to Markdown report
    html: str | None         # Path to HTML report
    pdf: str | None          # Path to PDF report
    docx: str | None         # Path to DOCX report
    sources_json: str | None # Path to sources JSON
    trace_json: str | None   # Path to trace JSON

class ResearchState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]                                     # Full agent conversation history logs.
    run_id: str                                                                             # Unique ID of this run.
    user_query: str                                                                         # Original prompt text entered by the user.
    status: RunStatus                                                                       # Current run state.
    error: str | None                                                                       # Failure traceback (if graph errors out).
    budget: Annotated[BudgetState, keep_latest]                                             # Running token and reflection count tally.
    scope: Annotated[ResearchScope, keep_latest]                                            # Boundary definition parameters.
    planner_output: Annotated[dict, keep_latest]                                            # Raw output of the planner node.
    branch_tasks: Annotated[list[BranchTask], append_unique_by_id('task_id')]               # Ongoing and completed tasks. Updates matching IDs.
    literature_findings: Annotated[list[Finding], append_unique_by_id('finding_id')]        # Output findings from Literature Branch.
    dataset_findings: Annotated[list[Finding], append_unique_by_id('finding_id')]           # Output findings from Dataset Branch.
    repository_findings: Annotated[list[Finding], append_unique_by_id('finding_id')]        # Output findings from Repository Branch.
    sources: Annotated[SourceRecord, merge_sources_by_id]                                   # Consolidated references. Merges metadata on overlap.
    extraction_cache: Annotated[dict, merge_dict]                                           # Cached raw page text from URLs to avoid redundant fetching.
    synthesized_claims: Annotated[list[SynthesizedClaim], append_unique_by_id('claim_id')]  # Processed claims. Overwrites on retry iteration.
    quality_score: Annotated[QualityScore, keep_latest]                                     # Scoring metrics for synthesized results.
    critiques: Annotated[list[Critique], append_unique_by_id('critique_id')]                # Outstanding items flagged for correction.
    reflection_decisions: Annotated[list[ReflectionDecision], operator.add]                 # Loop execution path. Keeps all iterations chronologically.
    report_markdown: Annotated[str, keep_latest]                                            # Active draft of the Markdown report.
    citation_map: Annotated[dict, merge_dict]                                               # UUID key to citation standard map (e.g., {"s1": "S1"}).
    exports: Annotated[ExportPaths, keep_latest]                                            # Local paths to final file artifacts.