import pytest

from researchgraph.config import Settings
from researchgraph.llm.model_router import model_for_role
from researchgraph.llm.structured_output import parse_json_object


def test_model_router_uses_role_specific_model():
    settings = Settings(
        openrouter_api_key='test-key',
        model_planner="planner-model",
        model_research="research-model"
    )

    assert model_for_role("planner", settings) == "planner-model"
    assert model_for_role("literature", settings) == "research-model"
    assert model_for_role("dataset", settings) == "research-model"
    assert model_for_role("repository", settings) == "research-model"

def test_parse_json_object_accepts_clean_json():
    assert parse_json_object('{"a": 1}') == {"a": 1}

def test_parse_json_object_accepts_fenced_json():
    assert parse_json_object('```json\n{"a": 1}\n```') == {"a": 1}

def test_parse_json_object_raises_for_invalid_json():
    with pytest.raises(ValueError):
        parse_json_object("not json")