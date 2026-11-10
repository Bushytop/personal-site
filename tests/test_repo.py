"""Checks on the repo source itself (it's public)."""
import subprocess

from conftest import ROOT

ALIAS = "hello" + "@" + "andychamberlin.com"


def _tracked_text_files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    for name in out.stdout.splitlines():
        p = ROOT / name
        if p.suffix.lower() not in {".jpg", ".jpeg", ".png"} and p.is_file():
            yield p


def test_no_literal_email_in_repo():
    for p in _tracked_text_files():
        text = p.read_text(errors="ignore")
        assert ALIAS not in text, p
        assert "@" + "gmail.com" not in text, p


def test_no_absolute_local_paths_in_repo():
    for p in _tracked_text_files():
        text = p.read_text(errors="ignore")
        for bad in ("/home/" + "andy", "/mnt/" + "idrive", "/mnt/" + "datasets2"):
            assert bad not in text, (p, bad)
