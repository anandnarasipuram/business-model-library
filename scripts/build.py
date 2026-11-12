"""Validate all entries and build site/entries.json (public layer only by default).

Usage:
    python scripts/build.py            # public entries only -> site/entries.json
    python scripts/build.py --private  # include private entries (local use only)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHETYPES = {
    "hardware_saas", "rental_leasing", "shared_savings", "guaranteed_savings",
    "partner_commission", "flexibility_revenue_share", "tariff_bundle", "submetering",
    "tenant_energy", "ev_charging", "data_platform", "marketplace", "other",
}
EVIDENCE = {"documented", "inferred", "assumed", "speculative"}
OUTCOMES = {"successful", "failed", "pivoted", "unproven", "niche"}
BLOCKS = {"hardware", "software", "sites_assets", "partners", "regulation", "financing", "channel", "data"}
REQUIRED = [
    "id", "name", "archetype", "sector", "summary", "perspective", "how_it_makes_money",
    "building_blocks", "what_must_be_true", "risks_failure_causes", "evidence", "outcome",
    "sources", "last_verified", "status", "visibility",
]


def check(entry: dict, filename: str) -> list:
    errors = []
    for key in REQUIRED:
        if key not in entry:
            errors.append(f"missing field '{key}'")
    if errors:
        return errors
    if entry["id"] != filename:
        errors.append(f"id '{entry['id']}' does not match file name '{filename}'")
    if entry["archetype"] not in ARCHETYPES:
        errors.append(f"unknown archetype '{entry['archetype']}'")
    if entry["evidence"] not in EVIDENCE:
        errors.append(f"bad evidence '{entry['evidence']}'")
    if entry["outcome"] not in OUTCOMES:
        errors.append(f"bad outcome '{entry['outcome']}'")
    if entry["visibility"] not in {"public", "private"}:
        errors.append("visibility must be public or private")
    missing_blocks = BLOCKS - set(entry["building_blocks"])
    if missing_blocks:
        errors.append(f"building_blocks missing: {sorted(missing_blocks)}")
    source_ids = {s.get("id") for s in entry["sources"]}
    for case in entry.get("cases", []):
        for sid in case.get("source_ids", []):
            if sid not in source_ids:
                errors.append(f"case '{case.get('company')}' cites unknown source '{sid}'")
    for risk in entry["risks_failure_causes"]:
        if risk.get("evidence") not in EVIDENCE:
            errors.append(f"risk '{risk.get('tag')}' has bad evidence")
    return errors


def main():
    include_private = "--private" in sys.argv
    out, failed = [], False
    for path in sorted((ROOT / "entries").glob("*.json")):
        entry = json.loads(path.read_text(encoding="utf-8"))
        errors = check(entry, path.stem)
        if errors:
            failed = True
            print(f"FAIL {path.name}")
            for e in errors:
                print(f"   - {e}")
            continue
        if entry["visibility"] == "private" and not include_private:
            print(f"skip {path.name} (private)")
            continue
        out.append(entry)
        print(f"ok   {path.name}")
    if failed:
        sys.exit(1)
    (ROOT / "site" / "entries.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"built site/entries.json with {len(out)} entries")


if __name__ == "__main__":
    main()
