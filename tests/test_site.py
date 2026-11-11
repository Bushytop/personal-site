"""Checks on the rendered site. Requires quarto on PATH (~/.local/bin)."""
import json
import re
from pathlib import Path

from conftest import ROOT, page


def _html_files(site: Path):
    files = [p for p in site.rglob("*.html") if "site_libs" not in p.parts]
    assert files, "no rendered pages"
    return files


def test_every_page_title_has_name(site):
    for p in _html_files(site):
        title = re.search(r"<title>(.*?)</title>", p.read_text(), re.S)
        assert title and "Andy Chamberlin" in title.group(1), p


def test_no_raw_email_in_site(site):
    assert _html_files(site)
    for p in site.rglob("*"):
        if p.is_file() and p.suffix in {".html", ".js", ".xml", ".json", ".txt"}:
            text = p.read_text(errors="ignore")
            assert "@" + "gmail.com" not in text, p
            assert "hello" + "@" + "andychamberlin.com" not in text, p


def test_jsonld_person(site):
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', page("index.html"), re.S)
    data = json.loads(m.group(1))
    prof = json.loads((ROOT / "_data" / "profile.json").read_text())
    assert data["@type"] == "Person"
    assert set(data["sameAs"]) == {prof[k] for k in ("orcid", "scholar", "github", "linkedin")}


def test_publications_page_from_export(site):
    html = page("publications.html")
    assert re.search(r"<strong>[^<]*Chamberlin</strong>", html)
    assert "doi.org/10.1073/pnas.1903698116" in html


def test_sitemap_and_og(site):
    assert (site / "sitemap.xml").exists()
    assert 'property="og:image"' in page("index.html")


def test_cname(site):
    assert (site / "CNAME").read_text().strip() == "andychamberlin.com"


LAUNCH_SLUGS = ["senegal-snail-habitat", "senegal-rice-fish", "borneo-canopy-height",
                "mosquito-breeding-sites"]


def test_home_sections_in_order(site):
    html = page("index.html")
    marks = ['class="hero', 'class="intro', 'class="service-card', 'class="project-tile',
             'class="media-highlights', 'class="email"']
    pos = [html.find(m) for m in marks]
    assert all(p >= 0 for p in pos), dict(zip(marks, pos))
    assert pos == sorted(pos)
    assert html.count('class="service-card') == 3
    assert html.count('class="project-tile') == 4


def test_home_service_card_text(site):
    heads = re.findall(r'class="service-card.*?<h3[^>]*>(.*?)</h3>', page("index.html"), re.S)
    clean = [re.sub("<[^>]+>", "", h).replace("&amp;", "&").strip() for h in heads]
    assert clean == ["Drone mapping & spatial analysis", "Satellite remote sensing & modeling",
                     "Computer vision & deep learning"]


def test_home_tiles_link_to_projects(site):
    html = page("index.html")
    for slug in LAUNCH_SLUGS:
        assert f'href="projects/{slug}.html"' in html, slug


def test_images_have_alt(site):
    for p in _html_files(site):
        for tag in re.findall(r"<img\b[^>]*>", p.read_text()):
            m = re.search(r'alt="([^"]*)"', tag)
            assert m and m.group(1).strip(), (p.name, tag[:120])


def test_referenced_images_exist(site):
    for p in _html_files(site):
        for src in re.findall(r'<img\b[^>]*src="([^"]+)"', p.read_text()):
            if not src.startswith(("http", "data:")):
                assert (p.parent / src).resolve().exists(), (p.name, src)


def test_draft_project_not_rendered(site):
    assert not (site / "projects" / "costa-rica-dengue.html").exists()
    for p in _html_files(site):
        assert "costa-rica-dengue" not in p.read_text(), p
    assert "costa-rica-dengue" not in (site / "sitemap.xml").read_text()


def test_project_pages_link_papers(site):
    expect = {
        "senegal-snail-habitat": "doi.org/10.1073/pnas.1903698116",
        "mosquito-breeding-sites": "doi.org/10.1016/j.rsase.2026.102011",
        "brazil-snail-habitat": "doi.org/10.1038/s41467-024-48335-9",
    }
    for slug, doi in expect.items():
        assert doi in page(f"projects/{slug}.html"), slug


JARGON = ["segmentation", "phenotyping", "RADIO", "SAM", "LOSO", "U-Net", "foundation model"]


def test_no_jargon_on_project_pages(site):
    for slug in LAUNCH_SLUGS + ["brazil-snail-habitat"]:
        html = page(f"projects/{slug}.html")
        body = re.search(r"<main.*?</main>", html, re.S).group(0)
        text = re.sub(r"<[^>]+>", " ", body)
        for word in JARGON:
            assert not re.search(rf"\b{re.escape(word)}\b", text, re.I), (slug, word)


MEDIA_URLS = [
    "https://www.npr.org/2026/07/12/nx-s1-5803170/farmers-fish-rice-snails-tropical-disease",
    "https://news.stanford.edu/stories/2026/03/ai-platform-disease-mapping-schistosomiasis-research",
    "https://news.stanford.edu/stories/2026/01/schistosomiasis-river-fever-transmission-research",
    "https://hai.stanford.edu/news/how-a-hai-seed-grant-helped-launch-a-disease-fighting-ai-platform",
    "https://hai.stanford.edu/news/bringing-ai-neglected-tropical-disease",
    "https://woods.stanford.edu/news/satellites-and-drones-could-help-slow-tropical-disease",
    "https://stanfordmag.org/contents/just-add-prawns",
    "https://www.nsf.gov/news/eliminating-public-health-scourge-can-also-benefit",
]


def test_media_drops_fisheries_report(site):
    assert "montereybayfisheriestrust" not in page("media.html")


def test_media_order_newest_first(site):
    items = re.findall(r"<li>\s*(\d{4})-(\d{2})", page("media.html"))
    assert len(items) >= 4
    assert items == sorted(items, reverse=True)


def test_media_known_items(site):
    html = page("media.html")
    for url in MEDIA_URLS:
        assert url in html, url


def test_contact_page_has_email_hook(site):
    assert re.search(r'<a class="email"[^>]*data-u="hello"', page("contact.html"))


def test_titles_name_once(site):
    for p in _html_files(site):
        title = re.search(r"<title>(.*?)</title>", p.read_text(), re.S).group(1)
        assert title.count("Andy Chamberlin") == 1, (p.name, title)


def test_home_share_image_and_description(site):
    html = page("index.html")
    og = re.search(r'<meta property="og:image" content="([^"]+)"', html).group(1)
    assert og.endswith("assets/img/share.jpg"), og
    assert re.search(r'<meta name="description" content="[^"]+"', html)


def test_profile_links_match_profile_json():
    prof = json.loads((ROOT / "_data" / "profile.json").read_text())
    for f in ("_quarto.yml", "contact.qmd"):
        text = (ROOT / f).read_text()
        for k in ("orcid", "scholar", "github", "linkedin"):
            assert prof[k] in text, (f, k)


def test_project_paper_links_have_years(site):
    for slug in LAUNCH_SLUGS + ["brazil-snail-habitat"]:
        line = next((l for l in page(f"projects/{slug}.html").splitlines() if "Papers:" in l), "")
        for a in re.findall(r'<a href="https://doi.org[^"]*">(.*?)</a>', line, re.S):
            assert re.search(r"\b(19|20)\d\d\b", a), (slug, a)


def test_indonesia_links_rosser_lab_papers(site):
    html = page("projects/mosquito-breeding-sites.html")
    for doi in ("10.1186/s13071-026-07646-0", "10.1186/s13071-025-06706-1",
                "10.1007/s11356-024-33801-0", "10.1186/s44263-026-00250-5"):
        assert f"doi.org/{doi}" in html, doi


def test_senegal_links_jones_2021(site):
    assert "doi.org/10.1371/journal.pntd.0009712" in page("projects/senegal-snail-habitat.html")


def test_indonesia_tile_credited_on_home(site):
    html = page("index.html")
    tile = re.search(r'href="projects/mosquito-breeding-sites.html".*?</a>', html, re.S).group(0)
    assert "CC BY-NC" in tile


def test_no_unloaded_webfont():
    for f in (ROOT / "styles").glob("*.scss"):
        assert '"Inter"' not in f.read_text(), f


def test_dengue_page_and_tile_name_all_three_countries(site):
    tile = re.search(r'href="projects/mosquito-breeding-sites.html".*?</a>', page("index.html"), re.S).group(0)
    body = re.search(r"<main.*?</main>", page("projects/mosquito-breeding-sites.html"), re.S).group(0)
    for country in ("Indonesia", "Kenya", "Costa Rica"):
        assert country in tile, country
        assert country in body, country


def test_old_dengue_slug_gone(site):
    assert not (site / "projects" / "indonesia-tire-detection.html").exists()


def test_deep_learning_named_on_home_and_project_pages(site):
    intro = re.search(r'class="intro.*?</section>', page("index.html"), re.S).group(0)
    assert "deep learning" in intro
    for slug in ("mosquito-breeding-sites", "senegal-snail-habitat", "senegal-rice-fish"):
        assert "deep learning" in page(f"projects/{slug}.html"), slug


def test_makassar_model_credited_to_me(site):
    assert "I trained the deep learning model" in page("projects/mosquito-breeding-sites.html")


def test_intro_says_i_lead_the_analysis(site):
    intro = re.search(r'class="intro.*?</section>', page("index.html"), re.S).group(0)
    assert "I lead the analysis" in intro


def test_tire_model_is_ours(site):
    html = page("projects/mosquito-breeding-sites.html")
    assert "our tire model" in html
    assert "my tire model" not in html


def test_about_page(site):
    html = page("about.html")
    body = re.search(r"<main.*?</main>", html, re.S).group(0)
    for s in ("Disease Ecology in a Changing World (DECO)", "Center for Human and Planetary Health",
              "De Leo", "Rosser", "Mordecai", "Bayesian", "Part 107", "Collaborators"):
        assert s in body, s
    assert 'href="./about.html"' in page("index.html") or 'href="about.html"' in page("index.html")


def test_home_media_highlights(site):
    sec = re.search(r'class="media-highlights.*?</section>', page("index.html"), re.S).group(0)
    assert "hai.stanford.edu/news/bringing-ai-neglected-tropical-disease" in sec
    assert "news.stanford.edu/stories/2026/04/mosquito-borne-disease-breeding-sites-drones-ai" in sec
    assert "river-fever" not in sec


def test_canopy_page(site):
    html = page("projects/borneo-canopy-height.html")
    assert "doi.org/10.3390/rs17213592" in html
    assert "doi.org/10.1016/j.lanplh.2026.101455" in html
    assert "CC BY" in html


def test_home_tiles_canopy_not_brazil(site):
    html = page("index.html")
    assert 'href="projects/borneo-canopy-height.html"' in html
    assert 'href="projects/brazil-snail-habitat.html"' not in html
    assert "brazil-snail-habitat.html" in page("projects/index.html")


def test_snail_id_page(site):
    body = re.search(r"<main.*?</main>", page("projects/snail-parasite-id.html"), re.S).group(0).replace("&nbsp;", " ")
    assert "doi.org/10.3389/fpubh.2021.642895" in body
    assert "Tallam et al. 2021" in body
    assert "Côte d’Ivoire" in body or "Côte d'Ivoire" in body
    assert "github.com" not in body


def test_senegal_satellite_page(site):
    body = re.search(r"<main.*?</main>", page("projects/senegal-satellite-habitat.html"), re.S).group(0)
    assert "doi.org/10.3390/rs14061345" in body
    assert "hai.stanford.edu/news/bringing-ai-neglected-tropical-disease" in body
    assert "Maxar" not in body


def test_no_maxar_imagery_anywhere(site):
    for p in _html_files(site):
        assert "Maxar" not in p.read_text(), p.name


def test_projects_page_grouped(site):
    html = page("projects/index.html")
    heads = ["Drone mapping", "Satellite mapping", "Image identification"]
    pos = [html.find(h) for h in heads]
    assert all(x >= 0 for x in pos) and pos == sorted(pos), pos
    groups = {0: ["senegal-snail-habitat", "senegal-rice-fish", "brazil-snail-habitat",
                  "mosquito-breeding-sites"],
              1: ["borneo-canopy-height", "senegal-satellite-habitat"],
              2: ["snail-parasite-id"]}
    bounds = pos + [len(html)]
    for g, slugs in groups.items():
        sec = html[bounds[g]:bounds[g + 1]]
        for s in slugs:
            assert f"{s}.html" in sec, (g, s)


def test_snail_id_says_co_developed(site):
    body = re.search(r"<main.*?</main>", page("projects/snail-parasite-id.html"), re.S).group(0)
    assert "I co-developed" in body
    assert "Zac Liu" not in body


CODE_LINKS = {
    "mosquito-breeding-sites": "https://github.com/Rosser-Lab/Aedes-Tire-Detection",
    "borneo-canopy-height": "https://github.com/Bushytop/canopy_height_ml",
}


def test_project_code_links(site):
    for slug, url in CODE_LINKS.items():
        assert url in page(f"projects/{slug}.html"), slug
    allowed = set(CODE_LINKS.values()) | {"https://github.com/Bushytop"}
    for p in _html_files(site):
        body = re.search(r"<main.*?</main>", p.read_text(), re.S)
        for url in re.findall(r'href="(https://github\.com/[^"]+)"', body.group(0) if body else ""):
            assert url.rstrip("/") in allowed, (p.name, url)


def test_favicon_linked(site):
    html = page("index.html")
    m = re.search(r'<link href="([^"]+)" rel="icon"', html)
    assert m, "no favicon link"
    assert (site / m.group(1).lstrip("./")).exists()


def test_404_page(site):
    html = page("404.html")
    assert "Page not found" in html
    assert 'href="/"' in html or 'href="/index.html"' in html
