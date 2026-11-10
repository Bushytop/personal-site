#!/usr/bin/env python3
"""Make an HTML grid of thumbnails so Andy can pick site images.

Usage: python scripts/contact_sheet.py OUT_DIR SRC [SRC ...]   (files or folders of JPGs)
Writes OUT_DIR/index.html plus thumbnails; each caption is the full source path to copy
into images.yml. OUT_DIR is scratch and stays out of git.
"""
import html
import sys
from pathlib import Path

from prepare_images import prepare


def contact_sheet(sources: list[Path], out_dir: Path, thumbs: int = 400) -> Path:
    """Write thumbnails and index.html for sources into out_dir; return the HTML path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    cells = []
    for i, src in enumerate(sources):
        thumb = out_dir / f"t{i:04d}.jpg"
        prepare(src, thumb, long_edge=thumbs, quality=75)
        cells.append(
            f'<figure><img src="{thumb.name}" loading="lazy">'
            f"<figcaption>{html.escape(str(src))}</figcaption></figure>"
        )
    page = out_dir / "index.html"
    page.write_text(
        "<!doctype html><meta charset=utf-8><title>Contact sheet</title><style>"
        "body{font:12px sans-serif;margin:16px;display:grid;"
        "grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}"
        "img{width:100%}figure{margin:0}figcaption{word-break:break-all}</style>"
        + "".join(cells)
    )
    return page


def _expand(args: list[str]) -> list[Path]:
    out = []
    for a in map(Path, args):
        out += sorted(p for p in a.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg"}) if a.is_dir() else [a]
    return out


if __name__ == "__main__":
    print(contact_sheet(_expand(sys.argv[2:]), Path(sys.argv[1])))
