# personal-site — Claude Context

Andy Chamberlin's public website, andychamberlin.com. Quarto, GitHub Pages (`gh-pages` branch),
DNS and email forwarding (the `hello` alias → Gmail) on Cloudflare. No PI or funder.

Design and plan live in the private cv repo: `~/Projects/cv/docs/2026-11-09-personal-site-design.md`
and `...-plan.md`. Read the design before changing content.

## Rules
- Public repo. Nothing from `~/Projects/cv` comes here except via `export_site_data.py`.
- Never put the Gmail address or the literal contact address in the repo; use the
  `<a class="email" data-u="hello" data-d="andychamberlin.com">` hook.
- Facts and drone claims follow `~/Projects/cv/facts.md` ("Drone work: who flew what").
- No unpublished results. Costa Rica stays `projects/_costa-rica-dengue.qmd` until a preprint posts.
- Images go through `scripts/prepare_images.py` and loops through `scripts/prepare_clips.py`
  (both strip GPS/metadata); never commit originals.
- Photo & video page: no shots centered on private homes or recognizable people without their
  okay. bioGraphic's *Protected by Prawns* is their film: link it, never re-host it.
  Manifest paths are relative to named roots in the gitignored `image_roots.yml`.
- Copy: Andy's voice, plain words, no jargon on project pages (tests enforce a word list).
- Run `pytest -q` before every push.
- Images: no Maxar/DigitalGlobe imagery (grant terms; a test enforces it). Paper figures only
  from CC BY papers, credited on the page. Code links only to public repos Andy owns or mainly
  develops (a test holds the allowlist in `CODE_LINKS`).
- Credit framing: "I lead/trained" for Andy's role, "our" for team products.

## Adding an Earth Engine app
Apps come from the `gee-inventory` work. For each public app: link it from the project page it
belongs to (`**App:** [name](url)`), and add a screenshot through `images.yml`. Once two or more
are live, add an "Interactive maps" listing group to `projects/index.qmd`; once there are
several, consider an "Apps" navbar item. Only apps that open without sign-in, showing published
or cleared products (De Leo cleared the Kalimantan canopy height map, 2026-11-11).

## Publishing
- Push to `main`; the `Publish site` workflow renders and pushes `gh-pages`. Repo:
  github.com/Bushytop/personal-site (public since 2026-11-11).
- Commits here use the GitHub no-reply address (set in this repo's git config); keep it that way.
