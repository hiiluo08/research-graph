import json

from researchgraph.memory.artifact_store import ArtifactStore
from researchgraph.memory.run_store import RunStore
from researchgraph.utils.ids import new_run_id


def test_new_run_id_has_expected_prefix():
    run_id = new_run_id()

    assert run_id.startswith('run_')
    assert len(run_id) >= 12

def test_artifact_store_writes_text_and_json(tmp_path):
    store = ArtifactStore(base_dir=tmp_path)

    text_path = store.write_text('run_test', 'report.md', '# Hello')
    json_path = store.write_json('run_test', 'sources.json', {'sources': ['s1']})

    assert text_path.read_text(encoding='utf-8') == '# Hello'
    assert json.loads(json_path.read_text(encoding='utf-8')) == {'sources': ['s1']}

def test_run_store_creates_and_updates_status(tmp_path):
    db_path = tmp_path / 'run.sqlite'
    store = RunStore(db_path=db_path)

    store.create_run('run_test', 'test_query')
    store.update_status('run_test', 'completed')
    record = store.get_run('run_test')

    assert record['run_id'] == 'run_test'
    assert record['query'] == 'test_query'
    assert record['status'] == 'completed'