# Business Model Library (energy and IoT)

Encyclopedia of business models with building blocks, evidence tags and sources, plus an advisor and a simulator.

## Parts
- `entries/` one JSON file per model (schema in `schema.md`). Private entries live in `private_entries/` (git-ignored, never pushed, never in the site).
- `site/` static encyclopedia (search, filters). Deploy this folder on Cloudflare.
- `app.py` Streamlit app: Advisor (use case to ranked models with warnings), Simulator (sliders, who gets what, what must be true), Library.
- `engine/` catalog loader, matching (`match.py`), cash-flow simulation per archetype (`sim.py`), text intake (`intake.py`), LLM provider switch (`llm.py`, from Portfolio Copilot).
- `scripts/build.py` validates entries and builds `site/entries.json`. With `--private` it writes `build/entries.private.json` instead (git-ignored).
- `scripts/backtest.py` checks matching against the IHC models (needs private entries).

## Run
```bash
pip install -r requirements.txt
python scripts/build.py                 # validate + build the public site data
streamlit run app.py                    # public entries only
BML_PRIVATE=1 streamlit run app.py      # include private entries (local only)
python scripts/backtest.py              # IHC backtest
cd site && python -m http.server 8000   # preview the static site
```

Optional: copy `.env.example` to `.env` and set a provider key to let the Advisor read free text with an AI model. Without a key it uses keyword rules.

## Ask-AI button and deployment (Cloudflare)
- `worker/index.js` serves the site files and the endpoint `/api/ask`. It answers only from `site/entries.json` (public entries), cites entry ids, says "Not covered yet in the library." otherwise, caps question length and rate-limits per visitor (best effort; add a Cloudflare rate limiting rule for a hard limit).
- `wrangler.jsonc` points the Worker at `site/`.
- Deploy: connect the GitHub repo to Cloudflare Workers, no build command, deploy command `npx wrangler deploy`.
- Add the secret `COHERE_API_KEY` in Cloudflare (Settings, Variables and Secrets). The key never reaches the browser. Without it the button answers "not configured yet".
- Run `python scripts/build.py` before every push so `site/entries.json` is current.

## Important
- All simulation inputs are placeholders (evidence: assumed) until you replace them.
- Entries marked `TO CONFIRM` (the private IHC entries) need your facts before they count as evidence.
- Run `python scripts/build.py` before every push so `site/entries.json` is current.
