from researchgraph.agents.planner import build_fallback_plan


def test_fallback_plan_always_creates_three_branch_tasks():
    plan = build_fallback_plan("Gaussian Splatting for endoscopic reconstruction")

    branches = {task.branch for task in plan.branch_tasks}

    assert branches == {"literature", "dataset", "repository"}
    assert plan.normalized_query == "Gaussian Splatting for endoscopic reconstruction"
    assert len(plan.must_cover) >= 5
