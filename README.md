# Business Model Library (energy and IoT)

Encyclopedia of business models with building blocks, evidence tags and sources. Static site, plus an engine
(copied from Portfolio Copilot) for the later dashboard.

- `entries/` one JSON file per model (see `schema.md`)
- `scripts/build.py` validates entries, builds `site/entries.json` (`--private` includes private entries)
- `site/` static page (deploy on Cloudflare Workers/Pages from GitHub)
- `engine/` business_case, scoring, llm from Portfolio Copilot, to be generalised in stage 3

Preview: `python scripts/build.py && cd site && python -m http.server 8000`
