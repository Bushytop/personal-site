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
- Images go through `scripts/prepare_images.py` (strips GPS/EXIF); never commit originals.
  Manifest paths are relative to named roots in the gitignored `image_roots.yml`.
- Copy: Andy's voice, plain words, no jargon on project pages (tests enforce a word list).
- Run `pytest -q` before every push.
