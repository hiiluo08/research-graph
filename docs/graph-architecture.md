# ResearchGraph — LangGraph Architecture

## Overview

ResearchGraph is a multi-agent research pipeline built on [LangGraph](https://github.com/langchain-ai/langgraph).
It takes a user query, fans it out across three parallel research branches (literature, datasets, repositories),
synthesizes the findings, scores them with a critic, and loops through a reflection gate before producing
a final Markdown report.

---

## Graph Topology

```
  START
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  INITIALIZATION                                                     │
│                                                                     │
│   ┌────────┐       ┌──────────┐                                     │
│   │ intake │ ────► │ planner  │                                     │
│   └────────┘       └────┬─────┘                                     │
└────────────────────────-┼───────────────────────────────────────────┘
                          │  fan-out (parallel)
             ┌────────────┼────────────┐
             ▼            ▼            ▼
     ┌────────────┐ ┌───────────┐ ┌────────────┐
     │ literature │ │  dataset  │ │ repository │
     └─────┬──────┘ └─────┬─────┘ └─────┬──────┘
           └──────────────┼──────────────┘  fan-in
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│  EVALUATION LOOP  ·  repeats until accepted or budget exhausted     │
│                                                                     │
│              ┌───────────────┐                                      │
│              │  synthesizer  │  merge findings → SynthesizedClaims  │
│              └──────┬────────┘                                      │
│                     │                                               │
│                     ▼                                               │
│              ┌───────────────┐                                      │
│              │    critic     │  score → QualityScore + Critiques    │
│              └──────┬────────┘                                      │
│                     │                                               │
│                     ▼                                               │
│         ┌───────────────────────┐                                   │
│         │      reflection       │  increment budget.iteration       │
│         │   ◄ decision gate ►   │  emit ReflectionDecision          │
│         └──┬───────┬──────┬──┬──┘                                   │
└────────────┼───────┼──────┼──┼──────────────────────────────────────┘
             │       │      │  │
          [accept] [retry [re- [forced_
                   branch] plan] finalize]
             │       │      │       │
             │       │      └───────┼──────► planner  (loop restarts)
             │       │              │
             │       └──────────────┼──────► literature / dataset / repository
             │                      │
             │               ┌──────┴──────┐
             │               │forced_final.│  set status = "writing"
             │               └──────┬──────┘
             │                      │
             ▼                      │
┌─────────────────────────────────────────────────────────────────────┐
│  WRITING PIPELINE                 │                                 │
│                                   │                                 │
│   ┌──────────────────────┐        │                                 │
│   │  citation_normalize  │◄───────┘  assign S1, S2, … to sources   │
│   └──────────┬───────────┘                                          │
│              │                                                      │
│              ▼                                                      │
│   ┌──────────────────────┐                                          │
│   │    citation_check    │  validate labels used in report draft    │
│   └──────────┬───────────┘                                          │
│              │                                                      │
│              ▼                                                      │
│   ┌──────────────────────┐                                          │
│   │    report_writer     │  render final Markdown report            │
│   └──────────┬───────────┘                                          │
│              │                                                      │
│              ▼                                                      │
│   ┌──────────────────────┐                                          │
│   │    export_files      │  write to disk → ExportPaths             │
│   └──────────┬───────────┘                                          │
└──────────────┼──────────────────────────────────────────────────────┘
               ▼
              END
```

---

## Nodes

### Control / Lifecycle

| Node | Function | Description |
|------|----------|-------------|
| `intake` | `intake_node` | Sets `status = "planning"`. Entry point that initialises the run before handing off to the planner. |
| `forced_finalize` | `forced_finalize_node` | Sets `status = "writing"`. Triggered when the budget is exhausted. Skips further research and moves straight to citation/report. |

### Research Planning

| Node | Function | Description |
|------|----------|-------------|
| `planner` | `planner_node` | Analyses the user query, defines `ResearchScope`, and emits a list of `BranchTask` objects — one per branch — that guide the three research agents. Also called on `replan` if the reflection loop decides the whole research plan needs to be rethought. |

### Research Branches (parallel fan-out)

All three branches are independent and run in parallel after the planner.

| Node | Function | Branch | Description |
|------|----------|--------|-------------|
| `literature` | `literature_node` | `literature` | Searches for academic papers and written sources. Produces `Finding` objects and `SourceRecord` entries. |
| `dataset` | `dataset_node` | `dataset` | Searches for relevant datasets. Produces `Finding` objects and `SourceRecord` entries. |
| `repository` | `repository_node` | `repository` | Searches for relevant code repositories (e.g. GitHub). Produces `Finding` objects and `SourceRecord` entries. |

### Synthesis & Evaluation

| Node | Function | Description |
|------|----------|-------------|
| `synthesizer` | `synthesis_node` | Merges findings from all three branches into a unified list of `SynthesizedClaim` objects. Sets `status = "critiquing"`. |
| `critic` | `critic_node` | Scores the synthesised claims against seven quality dimensions (coverage, citation grounding, source diversity, freshness, conflict handling, clarity, overall). Emits a `QualityScore` and zero or more `Critique` objects flagging specific issues. Sets `status = "reflecting"`. |
| `reflection` | `reflection_node` | Reads the latest `QualityScore` and `Critique` list, increments `budget.iteration`, and appends a `ReflectionDecision` that tells the router where to go next. |

### Citation

| Node | Function | Description |
|------|----------|-------------|
| `citation_normalize` | `citation_normalize_node` | Assigns a stable short label (`S1`, `S2`, …) to every source in the state and writes the mapping to `citation_map`. Sets `status = "writing"`. |
| `citation_check` | `citation_check_node` | Scans the draft `report_markdown` for citation labels and validates that every used label exists in `citation_map`. Appends warnings to the report for any orphan labels. |

### Reporting & Export

| Node | Function | Description |
|------|----------|-------------|
| `report_writer` | `report_writer_node` | Renders the final Markdown report from synthesised claims, citation labels, and references. Sets `status = "exporting"`. |
| `export_files` | `export_files_node` | Writes the report and source data to disk (Markdown, JSON). Populates `ExportPaths` in the state. |

---

## Conditional Routing — `route_after_reflection`

The only conditional edge in the graph sits between `reflection` and the rest of the graph.

```
reflection ──► route_after_reflection() ──► one of:
    "accept"            → citation_normalize   (quality passed, proceed to write)
    "retry_literature"  → literature           (re-run only the literature branch)
    "retry_dataset"     → dataset              (re-run only the dataset branch)
    "retry_repository"  → repository           (re-run only the repository branch)
    "replan"            → planner              (start research over with a new plan)
    "forced_finalize"   → forced_finalize      (budget exhausted, write whatever we have)
```

Priority order inside `route_after_reflection`:

1. **Budget guard** — if `budget.iteration >= budget.max_iterations`, always route to `forced_finalize` regardless of the decision.
2. **Accept** — if `next_action == "accept"`.
3. **Replan** — if `next_action == "replan"`.
4. **Retry branch** — if `next_action == "retry_branch"`, maps `target_branch` → specific retry route.
5. **Fallback** — any unrecognised state routes to `forced_finalize`.

---

## State (`ResearchState`)

Key fields that flow through the graph. Full type definitions live in [src/researchgraph/graph/state.py](../src/researchgraph/graph/state.py).

| Field | Type | Reducer | Purpose |
|-------|------|---------|---------|
| `user_query` | `str` | — | Original query from the user. Immutable after intake. |
| `status` | `RunStatus` | `keep_latest` | Current lifecycle stage (e.g. `"planning"`, `"researching"`, `"writing"`). |
| `budget` | `BudgetState` | `keep_latest` | Tracks iteration count, max iterations, and estimated API cost. |
| `scope` | `ResearchScope` | `keep_latest` | Query boundaries produced by the planner (domain, time range, must-cover topics). |
| `branch_tasks` | `list[BranchTask]` | `append_unique_by_id` | Per-branch task specs emitted by the planner. Updated in-place on replan. |
| `literature_findings` | `list[Finding]` | `append_unique_by_id` | Findings from the literature branch. Accumulated across retry iterations. |
| `dataset_findings` | `list[Finding]` | `append_unique_by_id` | Findings from the dataset branch. |
| `repository_findings` | `list[Finding]` | `append_unique_by_id` | Findings from the repository branch. |
| `sources` | `list[SourceRecord]` | `merge_sources_by_id` | Deduplicated source registry. All branches write here; metadata is merged on overlap. |
| `synthesized_claims` | `list[SynthesizedClaim]` | `append_unique_by_id` | Processed claims produced by the synthesizer. |
| `quality_score` | `QualityScore` | `keep_latest` | Latest scores from the critic. Overwritten each iteration. |
| `critiques` | `list[Critique]` | `append_unique_by_id` | Specific issues flagged by the critic. |
| `reflection_decisions` | `list[ReflectionDecision]` | `operator.add` | One entry per reflection loop iteration. Kept in chronological order. |
| `citation_map` | `dict` | `merge_dict` | Maps `source_id → "S1"` labels. Written by `citation_normalize`. |
| `report_markdown` | `str` | `keep_latest` | Active draft of the Markdown report. |
| `exports` | `ExportPaths` | `keep_latest` | Absolute paths to the artefacts written to disk. |

---

## Reflection Loop

The graph can revisit research nodes multiple times before accepting the output.
Each pass through `critic → reflection → route` is one **iteration**.

```
iteration 1:  planner → [lit, data, repo] → synthesizer → critic → reflection
                                                                         │
                             ┌───────────────────────────────────────────┘
                             │  next_action?
                             ├─ accept          ──► citation pipeline
                             ├─ retry_branch    ──► single branch re-runs, rest is cached
                             ├─ replan          ──► full restart from planner
                             └─ forced_finalize ──► skip to citation (budget exhausted)

iteration N:  same cycle; budget.iteration is incremented each time by reflection_node
              when budget.iteration >= budget.max_iterations, router forces finalize
```

Findings and sources from previous iterations are **preserved** (reducers append/merge).
Only `quality_score` and the report draft are overwritten each cycle.

---

## File Map

```
src/researchgraph/
├── graph/
│   ├── state.py         — ResearchState TypedDict + all sub-TypedDicts
│   ├── builder.py       — StateGraph wiring (nodes + edges)
│   ├── routing.py       — route_after_reflection()
│   └── reducers.py      — Custom LangGraph reducers
└── agents/
    ├── planner.py       — planner_node
    ├── literature.py    — literature_node
    ├── dataset.py       — dataset_node
    ├── repository.py    — repository_node
    ├── synthesizer.py   — synthesis_node
    ├── critic.py        — critic_node
    ├── reflection.py    — reflection_node
    ├── citation.py      — citation_normalize_node, citation_check_node
    └── report_writer.py — report_writer_node
```
