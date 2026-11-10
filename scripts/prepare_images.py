#!/usr/bin/env python3
"""Turn curated source photos into web images for the site.

Inputs:  images.yml at the repo root, a list of {root: name, src: path under that root,
         out: name.jpg, alt: text}; image_roots.yml (gitignored) maps each root name to a local
         folder, so no local paths land in this public repo
Outputs: assets/img/<out>, long edge <= 2000 px, JPEG quality 82, no EXIF/XMP

Drone JPGs carry GPS in EXIF, so every output is re-encoded from pixels only.
Usage: python scripts/prepare_images.py [--manifest images.yml] [--out assets/img]
"""
import argparse
from pathlib import Path

import yaml
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def prepare(src: Path, dst: Path, long_edge: int = 2000, quality: int = 82) -> None:
    """Write src to dst as an upright, metadata-free JPEG no larger than long_edge px."""
    with Image.open(src) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        img.thumbnail((long_edge, long_edge), Image.LANCZOS)
        clean = Image.new("RGB", img.size)
        clean.paste(img)
    dst.parent.mkdir(parents=True, exist_ok=True)
    clean.save(dst, "JPEG", quality=quality, optimize=True, progressive=True)


def _source(entry: dict, roots: dict) -> Path:
    """Resolve an entry's source path, through its named root if it has one."""
    if "root" not in entry:
        return Path(entry["src"])
    if entry["root"] not in roots:
        raise KeyError(f"unknown image root '{entry['root']}'; add it to image_roots.yml")
    return Path(roots[entry["root"]]).expanduser() / entry["src"]


def build_from_manifest(manifest: Path, out_dir: Path, roots: dict | None = None) -> list[Path]:
    """Prepare every manifest entry into out_dir; validates all entries before writing any.

    roots maps root names used in the manifest to local folders.
    """
    roots = roots or {}
    entries = yaml.safe_load(manifest.read_text()) or []
    sources = []
    for e in entries:
        if not str(e.get("alt", "")).strip():
            raise ValueError(f"missing alt text for {e.get('out')}")
        src = _source(e, roots)
        if not src.exists():
            raise FileNotFoundError(f"source not found: {src}")
        sources.append(src)
    outs = []
    for e, src in zip(entries, sources):
        dst = out_dir / e["out"]
        prepare(src, dst)
        outs.append(dst)
    return outs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "images.yml")
    parser.add_argument("--out", type=Path, default=ROOT / "assets" / "img")
    parser.add_argument("--roots", type=Path, default=ROOT / "image_roots.yml")
    args = parser.parse_args()
    roots = yaml.safe_load(args.roots.read_text()) if args.roots.exists() else {}
    for p in build_from_manifest(args.manifest, args.out, roots):
        print(p.relative_to(ROOT) if p.is_relative_to(ROOT) else p)


if __name__ == "__main__":
    main()
