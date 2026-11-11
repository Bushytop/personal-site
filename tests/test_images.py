"""Tests for scripts/prepare_images.py."""
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prepare_images as pi  # noqa: E402


def _jpeg(path: Path, size=(4000, 3000), gps=False, orientation=None) -> Path:
    img = Image.new("RGB", size, (90, 140, 90))
    exif = Image.Exif()
    exif[0x010F] = "DJI"  # Make
    if gps:
        exif[0x8825] = {1: "N", 2: (14.0, 30.0, 0.0), 3: "W", 4: (16.0, 10.0, 0.0)}
    if orientation:
        exif[0x0112] = orientation
    img.save(path, exif=exif.tobytes())
    return path


def test_prepare_strips_all_exif(tmp_path):
    src = _jpeg(tmp_path / "drone.jpg", gps=True)
    assert Image.open(src).getexif().get_ifd(0x8825)  # fixture really has GPS
    dst = tmp_path / "out.jpg"
    pi.prepare(src, dst)
    out = Image.open(dst)
    assert len(out.getexif()) == 0
    assert "exif" not in out.info


def test_prepare_resizes_long_edge(tmp_path):
    pi.prepare(_jpeg(tmp_path / "big.jpg"), tmp_path / "b.jpg")
    assert Image.open(tmp_path / "b.jpg").size == (2000, 1500)
    pi.prepare(_jpeg(tmp_path / "small.jpg", size=(800, 600)), tmp_path / "s.jpg")
    assert Image.open(tmp_path / "s.jpg").size == (800, 600)


def test_prepare_respects_orientation(tmp_path):
    src = _jpeg(tmp_path / "rot.jpg", size=(1200, 800), orientation=6)
    pi.prepare(src, tmp_path / "r.jpg")
    w, h = Image.open(tmp_path / "r.jpg").size
    assert h > w


def test_manifest_missing_source_fails_loudly(tmp_path):
    m = tmp_path / "images.yml"
    m.write_text(f"- src: {tmp_path / 'nope.jpg'}\n  out: a.jpg\n  alt: x\n")
    with pytest.raises(FileNotFoundError, match="nope.jpg"):
        pi.build_from_manifest(m, tmp_path / "out")


def test_manifest_requires_alt(tmp_path):
    src = _jpeg(tmp_path / "a.jpg", size=(100, 100))
    m = tmp_path / "images.yml"
    m.write_text(f"- src: {src}\n  out: a.jpg\n")
    with pytest.raises(ValueError, match="alt"):
        pi.build_from_manifest(m, tmp_path / "out")


def test_manifest_resolves_named_roots(tmp_path):
    (tmp_path / "photos" / "sub").mkdir(parents=True)
    _jpeg(tmp_path / "photos" / "sub" / "a.jpg", size=(100, 100))
    m = tmp_path / "images.yml"
    m.write_text("- root: photos\n  src: sub/a.jpg\n  out: a.jpg\n  alt: x\n")
    outs = pi.build_from_manifest(m, tmp_path / "out", roots={"photos": tmp_path / "photos"})
    assert [p.name for p in outs] == ["a.jpg"]


def test_manifest_unknown_root_fails_loudly(tmp_path):
    m = tmp_path / "images.yml"
    m.write_text("- root: nowhere\n  src: a.jpg\n  out: a.jpg\n  alt: x\n")
    with pytest.raises(KeyError, match="nowhere"):
        pi.build_from_manifest(m, tmp_path / "out", roots={})


def test_manifest_crop_box(tmp_path):
    _jpeg(tmp_path / "a.jpg", size=(1000, 800))
    m = tmp_path / "images.yml"
    m.write_text(f"- src: {tmp_path / 'a.jpg'}\n  out: a.jpg\n  alt: x\n  crop: [100, 50, 500, 350]\n")
    (out,) = pi.build_from_manifest(m, tmp_path / "out")
    assert Image.open(out).size == (400, 300)
