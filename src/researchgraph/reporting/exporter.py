from researchgraph.config import get_settings
from researchgraph.graph.state import ResearchState
from researchgraph.memory.artifact_store import ArtifactStore
from researchgraph.reporting.docx_renderer import write_docx_from_markdown
from researchgraph.reporting.html_renderer import markdown_to_html
from researchgraph.reporting.pdf_renderer import write_pdf_from_markdown

def export_files_node(state: ResearchState) -> dict:
    settings = get_settings()
    store = ArtifactStore(base_dir=settings.artifacts_dir)
    run_id = state['run_id']

    markdown_path = store.write_text(run_id, 'report.md', state['report_markdown'])
    html_path = store.write_text(run_id, 'report.html', markdown_to_html(state['report_markdown']))
    pdf_path = store.run_dir(run_id) /'report.pdf'
    docx_path = store.run_dir(run_id) / 'report.docx'
    
    pdf_ok = write_pdf_from_markdown(markdown_path, pdf_path)
    docx_ok = write_docx_from_markdown(markdown_path, docx_path)

    sources_path = store.write_json(run_id, 'sources.json', {'sources': state.get('sources', [])})
    claims_path = store.write_json(
        run_id, 'claims.json', 
        {'claims': state.get('synthesized_claims', [])}
    )
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
            "html": str(html_path),
            "pdf": str(pdf_path) if pdf_ok else None,
            "docx": str(docx_path) if docx_ok else None,
            "sources_json": str(sources_path),
            "trace_json": str(trace_path)
        }
    }