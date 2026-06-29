from langgraph.graph import StateGraph, START, END

from researchgraph.agents.citation import citation_normalize_node, citation_check_node
from researchgraph.agents.critic import critic_node
from researchgraph.agents.dataset import dataset_node
from researchgraph.agents.literature import literature_node
from researchgraph.agents.planner import planner_node
from researchgraph.agents.reflection import reflection_node
from researchgraph.agents.report_writer import report_writer_node
from researchgraph.agents.repository import repository_node
from researchgraph.agents.synthesizer import synthesis_node
from researchgraph.graph.routing import route_after_reflection
from researchgraph.graph.state import ResearchState
from researchgraph.reporting.exporter import export_files_node

def intake_node(state: ResearchState) -> dict:
    return {'status': 'planning'}

def forced_finalize_node(state: ResearchState) -> dict:
    return {"status": "writing"}

def build_research_graph():
    builder = StateGraph(ResearchState) #type: ignore

    builder.add_node('intake', intake_node)
    builder.add_node('forced_finalize', forced_finalize_node)
    builder.add_node('citation_normalize', citation_normalize_node)
    builder.add_node('citation_check', citation_check_node)
    builder.add_node('critic', critic_node)
    builder.add_node('dataset', dataset_node)
    builder.add_node('literature', literature_node)
    builder.add_node('planner', planner_node)
    builder.add_node('reflection', reflection_node)
    builder.add_node('report_writer', report_writer_node)
    builder.add_node('repository', repository_node)
    builder.add_node('synthesizer', synthesis_node)
    builder.add_node('export_files', export_files_node)

    builder.add_edge(START, 'intake')
    builder.add_edge('intake', 'planner')

    builder.add_edge('planner', 'literature')
    builder.add_edge('planner', 'dataset')
    builder.add_edge('planner', 'repository')

    builder.add_edge('literature', 'synthesizer')
    builder.add_edge('dataset', 'synthesizer')
    builder.add_edge('repository', 'synthesizer')

    builder.add_edge('synthesizer', 'critic')
    builder.add_edge('critic', 'reflection')

    builder.add_conditional_edges(
        'reflection',
        route_after_reflection,
        {
            'accept': 'citation_normalize',
            'retry_literature': 'literature',
            'retry_dataset': 'dataset',
            'retry_repository': 'repository',
            'replan': 'planner',
            'forced_finalize': 'forced_finalize'
        }
    )

    builder.add_edge('forced_finalize', 'citation_normalize')
    builder.add_edge('citation_normalize', 'citation_check')
    builder.add_edge('citation_check', 'report_writer')
    builder.add_edge('report_writer', 'export_files')
    builder.add_edge('export_files', END)

    return builder.compile()
    