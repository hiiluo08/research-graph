from researchgraph.config import Settings


def test_settings_defaults_without_env_key():
    settings = Settings(
        openrouter_api_key="just-testing",
        app_name="ResearchGraph",
        app_url="http://localhost:8000",
        max_cost_per_run_usd=0.30,
        max_reflection_iterations=2,
        max_sources_per_branch=6,
        max_tool_calls_per_branch=10,
        max_fetch_chars_per_source=12000,
    )

    assert settings.openrouter_api_key == 'just-testing'
    assert settings.app_url == 'http://localhost:8000'
    assert settings.app_name == 'ResearchGraph'

    assert settings.model_planner == 'openrouter/auto'
    assert settings.model_research == 'openrouter/auto'
    assert settings.model_synthesizer == 'openrouter/auto'
    assert settings.model_critic == 'openrouter/auto'
    assert settings.model_report_writer == 'openrouter/auto'
    assert settings.model_citation == 'openrouter/auto'  

    assert settings.max_cost_per_run_usd == 0.3
    assert settings.max_reflection_iterations == 2
    assert settings.max_sources_per_branch == 6
    assert settings.max_tool_calls_per_branch == 10
    assert settings.max_fetch_chars_per_source == 12000