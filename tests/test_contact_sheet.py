import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import contact_sheet as cs  # noqa: E402


def test_contact_sheet_lists_every_source(tmp_path):
    srcs = []
    for i in range(3):
        p = tmp_path / f"src{i}.jpg"
        Image.new("RGB", (900, 600)).save(p)
        srcs.append(p)
    html = cs.contact_sheet(srcs, tmp_path / "sheet").read_text()
    for p in srcs:
        assert str(p) in html
    assert len(list((tmp_path / "sheet").glob("*.jpg"))) == 3
