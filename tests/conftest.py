"""Shared fixtures: render the site once per test session."""
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"


def render_site() -> Path:
    """Run `quarto render` on the repo and return the output directory."""
    env = dict(os.environ, PATH=f"{Path.home() / '.local/bin'}:{os.environ['PATH']}")
    subprocess.run(["quarto", "render", "--quiet"], cwd=ROOT, check=True, env=env)
    return SITE


def page(path: str) -> str:
    """Rendered HTML of one page, path relative to _site."""
    return (SITE / path).read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def site() -> Path:
    return render_site()
