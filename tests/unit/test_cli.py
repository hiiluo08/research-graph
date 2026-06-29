from typer.testing import CliRunner

from researchgraph.cli import app

runner = CliRunner()


def test_version_subcommand_prints_package_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "ResearchGraph 0.1.0" in result.stdout
