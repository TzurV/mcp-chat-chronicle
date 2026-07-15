from __future__ import annotations

import os
import subprocess
import sys
import zipfile
from pathlib import Path


def test_built_wheel_initializes_ai_catalogs_outside_checkout(tmp_path: Path) -> None:
    repo = Path(__file__).resolve().parents[1]
    environment = subprocess.run(
        ["poetry", "env", "info", "--path"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert Path(environment).resolve() == (repo / ".venv").resolve()

    wheel_dir = tmp_path / "wheel"
    subprocess.run(
        ["poetry", "build", "-f", "wheel", "--output", str(wheel_dir)],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    wheel = next(wheel_dir.glob("*.whl"))
    target = tmp_path / "installed"
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        assert "chat_chronicle/resources/ai-tasks.default.yaml" in names
        assert "chat_chronicle/resources/ai-models.default.yaml" in names
        archive.extractall(target)

    run_dir = tmp_path / "outside-checkout"
    run_dir.mkdir()
    code = (
        "from pathlib import Path; "
        "from typer.testing import CliRunner; "
        "from chat_chronicle.cli import app; "
        "r=CliRunner().invoke(app,['init']); "
        "assert r.exit_code == 0, r.output; "
        "assert Path('.chronicle/ai-tasks.yaml').is_file(); "
        "assert Path('.chronicle/ai-models.yaml').is_file()"
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(target)
    subprocess.run([sys.executable, "-c", code], cwd=run_dir, env=env, check=True)
