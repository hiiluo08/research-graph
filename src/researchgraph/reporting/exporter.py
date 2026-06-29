from researchgraph.config import get_settings
from researchgraph.graph.state import ResearchState
from researchgraph.memory.artifact_store import ArtifactStore

def export_files_node(state: ResearchState) -> dict:
    settings = get_settings()
    store = ArtifactStore(base_dir=settings.artifacts_dir)
    run_id = state['run_id']

    markdown_path = store.write_text(run_id, 'report.md', state['report_markdown'])
    sources_path = store.write_json(run_id, 'sources.json', {'sources': state.get('sources', [])})
    trace_path = store.write_json(
        run_id, 
        'trace.json', 
        {
            'run_id': run_id, 
            'quality_score': state.get('quality_score'), 
            'reflection_decisions': state.get('reflection_decisions', [])
        }
    )

    return {
        "status": "completed",
        "exports": {
            "markdown": str(markdown_path),
            "html": None,
            "pdf": None,
            "docx": None,
            "sources_json": str(sources_path),
            "trace_json": str(trace_path),
        },
    }