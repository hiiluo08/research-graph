from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    openrouter_api_key: str = Field(alias='OPENROUTER_API_KEY')
    app_url: str = Field(default='http://localhost:8000', alias='APP_URL')
    app_name: str = Field(default='ResearchGraph', alias='APP_NAME')

    model_planner: str = Field(default="openrouter/auto", alias="MODEL_PLANNER")
    model_research: str = Field(default="openrouter/auto", alias="MODEL_RESEARCH")
    model_synthesizer: str = Field(default="openrouter/auto", alias="MODEL_SYNTHESIZER")
    model_critic: str = Field(default="openrouter/auto", alias="MODEL_CRITIC")
    model_report_writer: str = Field(default="openrouter/auto", alias="MODEL_REPORT_WRITER")
    model_citation: str = Field(default="openrouter/auto", alias="MODEL_CITATION")


    max_cost_per_run_usd: float = Field(default=0.3, alias='MAX_COST_PER_RUN_USD')
    max_reflection_iterations: int = Field(default=2, alias='MAX_REFLECTION_ITERATIONS')
    max_sources_per_branch: int = Field(default=6, alias='MAX_SOURCES_PER_BRANCH')
    max_tool_calls_per_branch: int = Field(default=10, alias='MAX_TOOL_CALLS_PER_BRANCH')
    max_fetch_chars_per_source: int = Field(default=12000, alias='MAX_FETCH_CHARS_PER_SOURCE')
    
    data_dir: str = Field(default='data', alias='DATA_DIR')
    artifacts_dir: str = Field(default='artifacts', alias='ARTIFACTS_DIR')

def get_settings() -> Settings:
    return Settings()