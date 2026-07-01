from researchgraph.agents.synthesizer import build_synthesized_claims


def test_synthesizer_drops_findings_without_sources():
    state = {
        "literature_findings": [
            {
                "finding_id": "f1",
                "branch": "literature",
                "claim": "Supported claim",
                "source_ids": ["s1"],
                "confidence": 0.8,
                "limitations": [],
            },
            {
                "finding_id": "f2",
                "branch": "literature",
                "claim": "Unsupported claim",
                "source_ids": [],
                "confidence": 0.9,
                "limitations": [],
            },
        ],
        "dataset_findings": [],
        "repository_findings": [],
    }

    claims = build_synthesized_claims(state)

    # Mong đợi 2 claims: 1 background claim tự động chèn + 1 supported claim từ f1
    assert len(claims) == 2
    assert claims[0]["claim_id"] == "C_BACKGROUND_001"
    assert claims[1]["statement"] == "Supported claim"
    assert claims[1]["supporting_source_ids"] == ["s1"]
