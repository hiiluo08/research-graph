# State Architecture and Reducers Reference

This document explains the shared state architecture (`ResearchState`) of the Multi-Agent Deep Research system, defining all the sub-schemas and the custom reducer functions used to safely merge data across parallel execution branches.

---

## 1. Conceptual Overview

In a multi-agent LangGraph system, the **Shared State** is the single source of truth that agents read from and write to. Since the system executes multiple research branches in parallel (Literature, Dataset, Repository), the state structure must prevent race conditions and correctly merge findings without data loss.

This system handles concurrency by:
1. **Separating branch outcomes:** Using dedicated keys for branch-specific findings (`literature_findings`, `dataset_findings`, `repository_findings`).
2. **Standardizing reference ingestion:** Merging all retrieved documents into a single deduplicated list (`sources`) using a custom key-based reducer.
3. **Tracking cycle histories:** Appending reflection decisions in a chronological log using Python's list addition.

---

## 2. Reducer Functions Reference

Reducers dictate how new data is merged with existing state data for a specific key. They are defined in [reducers.py](../src/researchgraph/graph/reducers.py).

### `keep_latest(old, new)`
Replaces the old value entirely with the new value.
* **Behavior:** Returns `new`.
* **Used for:** Status updates, configuration thresholds, single-value metrics.

### `merge_dict(old, new)`
Performs a shallow update of a dictionary.
* **Behavior:** Creates a copy of `old` (defaulting to `{}`) and calls `.update(new or {})`.
* **Used for:** Cache storage and key-value mapping expansions.

### `append_unique_by_id(key: str)`
A higher-order function returning a list-reducer that merges items based on a unique identifier field (e.g., ID), updating existing entries or appending new ones.
* **Behavior:** 
  * Keeps track of elements using a lookup dictionary.
  * Assigns fallback anonymous IDs (`anonymous-old-{index}` and `anonymous-new-{index}`) to items lacking the specified identifier.
  * If a new item shares an identifier with an old item, the new item replaces the old one.
* **Used for:** Findings, synthesized claims, tasks, and critiques.

### `merge_sources_by_id(old, new)`
Deduplicates and merges source documents, updating fields in existing sources if the new entry provides additional metadata.
* **Behavior:**
  * Uses a canonical key computed from `source_id`, `canonical_url`, `url`, or `title`.
  * If a source is new, it is appended.
  * If a source exists, its dictionary is updated field-by-field, preserving existing metadata if the incoming value is empty, `None`, or an empty list.
* **Used for:** Standardizing crawled references.

---

## 3. Sub-schema Definitions

The state architecture uses multiple specialized sub-schemas (typed dicts) to organize data:

### `BudgetState`
Tracks financial and processing constraints for the active execution run.
```python
class BudgetState(TypedDict):
    max_cost_usd: float                # Maximum allowed API spend
    estimated_cost_usd: float          # Cumulative calculated cost of OpenRouter calls
    max_iterations: int                # Maximum reflection cycles (default: 2)
    iteration: int                     # Active cycle index
    max_sources_per_branch: int        # Search limit per branch
    max_tool_calls_per_branch: int     # Tool call limit to prevent loops
    max_fetch_chars_per_source: int    # Text limit for crawled content (default: 12000)
```

### `ResearchScope`
Defines the parameters and guardrails of the current research topic.
```python
class ResearchScope(TypedDict):
    normalized_query: str              # The cleaned search query
    domain: str                        # Domain categorization (e.g. computer science)
    time_range: Optional[str]          # Optional temporal boundary
    must_cover: list[str]              # Required themes/subtopics
    out_of_scope: list[str]            # Topics to ignore/avoid
    assumptions: list[str]             # Starting premises
```

### `BranchTask`
The task specification sent to an individual research agent.
```python
class BranchTask(TypedDict):
    task_id: str                       # Unique identifier
    branch: BranchName                 # Target branch ('literature' | 'dataset' | 'repository')
    objective: str                     # Plain text objective
    search_queries: list[str]          # Recommended search engine queries
    required_outputs: list[str]        # Expected outputs to deliver
    success_criteria: list[str]        # Rubric criteria for the agent
    retry_instruction: Optional[str]   # Guidance if the task failed quality checks
```

### `SourceRecord`
A standardized reference document collected by any agent.
```python
class SourceRecord(TypedDict):
    source_id: str                     # Unique reference ID (e.g. arXiv identifier, URL hash)
    source_type: Literal["paper", "dataset", "repository", "web", "documentation"]
    title: str                         # Document title
    url: str                           # Crawl URL
    canonical_url: str                 # Standardized base URL
    authors: list[str]                 # Authors or creators
    published_at: Optional[str]        # Date published
    accessed_at: str                   # Fetch timestamp
    doi: Optional[str]                 # Digital Object Identifier (if applicable)
    venue: Optional[str]               # Publication venue (journal, conference)
    license: Optional[str]             # License information
    metadata: dict                     # Additional fields (downloads, stars, etc.)
```

### `Finding`
An individual, raw assertion extracted from sources by a branch agent.
```python
class Finding(TypedDict):
    finding_id: str                    # Unique ID
    branch: BranchName                 # Source branch
    task_id: str                       # Associated task
    claim: str                         # Core claim statement
    evidence_summary: str              # Text summarizing supporting evidence
    source_ids: list[str]              # Supporting source IDs from sources list
    confidence: float                  # Agent confidence score (0.0 - 1.0)
    limitations: list[str]             # Context limits or caveats
    metadata: dict                     # Raw parsing details
```

### `SynthesizedClaim`
An integrated claim generated by the Synthesizer by grouping related findings.
```python
class SynthesizedClaim(TypedDict):
    claim_id: str                      # Unique ID
    statement: str                     # Unified claim sentence
    category: Literal[
        "background", "concept", "literature", "dataset", 
        "repository", "challenge", "research_gap", 
        "future_direction", "learning_step"
    ]
    supporting_source_ids: list[str]   # Positive reference citations
    conflicting_source_ids: list[str]  # Discrepancy citations
    confidence: float                  # Calculated confidence score
    notes: list[str]                   # Synthesis observations
```

### `QualityScore`
Graded evaluation of synthesized output.
```python
class QualityScore(TypedDict):
    overall: float                     # Mean score
    coverage: float                    # Scope compliance
    citation_grounding: float          # Citation precision
    source_diversity: float            # Balance of branches and sources
    freshness: float                   # Temporal recency
    conflict_handling: float           # Reconciliation transparency
    clarity: float                     # Prose quality
```

### `Critique`
An itemized list of bugs or information gaps raised by the Critic Agent.
```python
class Critique(TypedDict):
    critique_id: str                   # Unique ID
    severity: Literal["low", "medium", "high", "critical"]
    issue_type: IssueType               # Type of issue (see state.py)
    description: str                   # Detailed error report
    target_branch: Optional[BranchName] # Responsible agent (if applicable)
    recommended_action: str            # Recommended remediation action
```

### `ReflectionDecision`
Determines routing after evaluating critiques.
```python
class ReflectionDecision(TypedDict):
    approved: bool                     # Yes/No approval to write report
    next_action: Literal["accept", "retry_branch", "replan", "forced_finalize"]
    target_branch: Optional[BranchName] # Which agent to rerun (if applicable)
    reason: str                        # Justification for decision
    revised_instruction: Optional[str] # Direct instructions for rerun
```

---

## 4. Shared State Schema (`ResearchState`)

Defined in [state.py](../src/researchgraph/graph/state.py), this is the central configuration of the LangGraph object:

| Key | Type | Reducer | Role / Purpose |
| :--- | :--- | :--- | :--- |
| `messages` | `list[AnyMessage]` | `add_messages` | Full agent conversation history logs. |
| `run_id` | `str` | Default (Override) | ID unique to this run. |
| `user_query` | `str` | Default (Override) | Original prompt text entered by the user. |
| `status` | `RunStatus` | Default (Override) | State progress (e.g. `planning`, `synthesizing`). |
| `error` | `Optional[str]` | Default (Override) | Failure traceback message (if graph errors out). |
| `budget` | `BudgetState` | `keep_latest` | Running token and reflection count tally. |
| `scope` | `ResearchScope` | `keep_latest` | Boundary definition parameters. |
| `planner_output` | `dict` | `keep_latest` | Raw planner planning object. |
| `branch_tasks` | `list[BranchTask]` | `append_unique_by_id("task_id")` | Ongoing and completed tasks. Updates matching IDs. |
| `literature_findings` | `list[Finding]` | `append_unique_by_id("finding_id")` | Output findings from Literature Branch. |
| `dataset_findings` | `list[Finding]` | `append_unique_by_id("finding_id")` | Output findings from Dataset Branch. |
| `repository_findings`| `list[Finding]` | `append_unique_by_id("finding_id")` | Output findings from Repository Branch. |
| `sources` | `list[SourceRecord]`| `merge_sources_by_id` | Consolidated references. Merges metadata on overlap. |
| `extraction_cache` | `dict` | `merge_dict` | Cached raw page text from URLs to avoid redundant fetching. |
| `synthesized_claims` | `list[SynthesizedClaim]`| `append_unique_by_id("claim_id")` | Processed claims. Overwrites on retry iteration. |
| `quality_score` | `QualityScore` | `keep_latest` | Scoring metrics evaluating synthesized results. |
| `critiques` | `list[Critique]` | `append_unique_by_id("critique_id")` | Outstanding items flagged for correction. |
| `reflection_decisions`| `list[ReflectionDecision]`| `operator.add` | Loop execution path. Keeps all iterations chronologically. |
| `report_markdown` | `str` | `keep_latest` | Active draft of the Markdown report. |
| `citation_map` | `dict` | `merge_dict` | UUID key to citation standard map (e.g., `{"s1": "S1"}`). |
| `exports` | `ExportPaths` | `keep_latest` | Local paths to final file artifacts. |
