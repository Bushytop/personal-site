#!/usr/bin/env python3
"""Cut short, muted web loops from source video for the site.

Inputs:  clips.yml at the repo root, a list of {root: name, src: path under that root,
         out: name.mp4, start: seconds, duration: seconds}; image_roots.yml (gitignored) maps
         each root name to a local folder, as for prepare_images.py
Outputs: assets/video/<out> (H.264, 1080p, no audio, no metadata, faststart) and a poster
         JPEG of its first frame beside it

DJI files carry GPS in their metadata, so every output drops all metadata.
Usage: python scripts/prepare_clips.py [--manifest clips.yml] [--out assets/video]
"""
import argparse
import subprocess
from pathlib import Path

import yaml

from prepare_images import _source

ROOT = Path(__file__).resolve().parents[1]


def prepare_clip(src: Path, dst: Path, start: float, duration: float,
                 width: int = 1920, crf: int = 32) -> None:
    """Write duration seconds of src from start (seconds) to dst, plus dst.with_suffix('.jpg')."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-v", "error", "-ss", str(start), "-t", str(duration), "-i", str(src),
        "-an", "-map_metadata", "-1", "-map_chapters", "-1",
        "-vf", f"scale={width}:-2", "-c:v", "libx264", "-crf", str(crf), "-preset", "slow",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-y", str(dst),
    ], check=True)
    subprocess.run([
        "ffmpeg", "-v", "error", "-i", str(dst), "-frames:v", "1", "-map_metadata", "-1",
        "-q:v", "4", "-y", str(dst.with_suffix(".jpg")),
    ], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "clips.yml")
    parser.add_argument("--out", type=Path, default=ROOT / "assets" / "video")
    parser.add_argument("--roots", type=Path, default=ROOT / "image_roots.yml")
    args = parser.parse_args()
    roots = yaml.safe_load(args.roots.read_text()) if args.roots.exists() else {}
    for e in yaml.safe_load(args.manifest.read_text()) or []:
        dst = args.out / e["out"]
        prepare_clip(_source(e, roots), dst, e["start"], e["duration"])
        print(dst.relative_to(ROOT) if dst.is_relative_to(ROOT) else dst)


if __name__ == "__main__":
    main()
