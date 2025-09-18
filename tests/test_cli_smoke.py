# file: tests/test_cli_smoke.py
from typer.testing import CliRunner

from arxds.cli import app

runner = CliRunner()


def test_help_runs():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "arXiv dataset CLI" in result.stdout
