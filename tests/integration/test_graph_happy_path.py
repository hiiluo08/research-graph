from researchgraph.graph.runner import run_research

def test_stub_graph_creates_markdown_report(tmp_path, monkeypatch):
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path / "artifacts"))
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    final_state = run_research("Gaussian Splatting for endoscopic scene reconstruction")

    assert final_state["status"] == "completed"
    assert "Executive Summary" in final_state["report_markdown"]
    assert final_state["exports"]["markdown"] is not None