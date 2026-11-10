#!/usr/bin/env python3
"""Write _includes/jsonld.html (schema.org Person) from _data/profile.json.

Re-run after export_site_data.py changes the profile. No email: scrapers read JSON-LD too.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(profile: dict) -> str:
    """Return a <script type="application/ld+json"> block for the profile."""
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": profile["name"],
        "alternateName": profile["full_name"],
        "jobTitle": profile["title"],
        "affiliation": {"@type": "Organization", "name": profile["affiliation"]},
        "url": "https://andychamberlin.com",
        "sameAs": [profile[k] for k in ("orcid", "scholar", "github", "linkedin")],
    }
    return '<script type="application/ld+json">\n' + json.dumps(data, indent=1) + "\n</script>\n"


if __name__ == "__main__":
    profile = json.loads((ROOT / "_data" / "profile.json").read_text())
    (ROOT / "_includes" / "jsonld.html").write_text(build(profile))
