"""Keep configuration tests independent of developer credentials and local files."""

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for name in os.environ:
        if name.upper().startswith("MEDASSIST_"):
            monkeypatch.delenv(name)
    monkeypatch.chdir(tmp_path)
