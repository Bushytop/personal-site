"""Tests for scripts/prepare_clips.py. Needs ffmpeg/ffprobe on PATH (personal-site env)."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prepare_clips as pc  # noqa: E402


def _src(path: Path) -> Path:
    """A 4 s 4K clip with audio and a GPS-like location tag, like a DJI file."""
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=3840x2160:rate=30",
                    "-f", "lavfi", "-i", "sine", "-t", "4", "-metadata", "location=+14.5-016.1/",
                    "-c:v", "libx264", "-preset", "ultrafast", "-y", str(path)], check=True)
    return path


def _probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json",
                          str(path)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def test_clip_is_muted_1080p_and_trimmed(tmp_path):
    dst = tmp_path / "loop.mp4"
    pc.prepare_clip(_src(tmp_path / "src.mp4"), dst, start=1, duration=2)
    info = _probe(dst)
    assert [s["codec_type"] for s in info["streams"]] == ["video"]
    v = info["streams"][0]
    assert (v["width"], v["height"]) == (1920, 1080)
    assert abs(float(info["format"]["duration"]) - 2) < 0.2


def test_clip_drops_location_metadata(tmp_path):
    src = _src(tmp_path / "src.mp4")
    assert "location" in _probe(src)["format"].get("tags", {})  # fixture really has it
    dst = tmp_path / "loop.mp4"
    pc.prepare_clip(src, dst, start=0, duration=2)
    assert "location" not in _probe(dst)["format"].get("tags", {})


def test_clip_writes_poster(tmp_path):
    dst = tmp_path / "loop.mp4"
    pc.prepare_clip(_src(tmp_path / "src.mp4"), dst, start=0, duration=2)
    assert dst.with_suffix(".jpg").stat().st_size > 0
