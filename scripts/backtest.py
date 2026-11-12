"""Backtest the matching against the IHC models (needs the private entries).

Run from the project root:  python scripts/backtest.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.catalog import load_entries
from engine.match import rank

PROFILE = {
    "segment": "mfh",
    "domain": "heating",
    "max_customer_capex": "high",
    "provider_can_finance": True,
    "savings_measurable": True,
    "has_installer_network": True,
    "has_own_hardware": True,
    "smart_meter_available": False,
}


def main():
    entries = load_entries(include_private=True)
    result = rank(PROFILE, entries)
    print("Profile: heating in multi-family buildings, landlords can buy and own, provider can finance,")
    print("         savings measurable, installer network and own hardware available\n")
    for i, r in enumerate(result["ranked"], 1):
        print(f"{i:2d}. {r['score']:3d}  {r['name']}  [{r['outcome']}, {r['evidence']}]")
    print("\nExcluded:")
    for x in result["excluded"]:
        print(f" - {x['name']}: {'; '.join(x['reasons'])}")

    ranked = {r["id"]: (i, r) for i, r in enumerate(result["ranked"])}
    failures = []
    if "ihc-rental" not in ranked:
        failures.append("rental is not ranked at all")
    else:
        pos, row = ranked["ihc-rental"]
        better = [r for r in result["ranked"] if r["outcome"] != "failed"]
        if any(row["score"] >= r["score"] for r in better):
            failures.append("rental does not rank below all non-failed models")
        if not any("Failed case" in w for w in row["warnings"]):
            failures.append("rental carries no failed-case warning")
    if "ihc-hardware-plus-saas" in ranked and "ihc-rental" in ranked:
        if ranked["ihc-hardware-plus-saas"][0] > ranked["ihc-rental"][0]:
            failures.append("hardware plus SaaS (worked well) ranks below rental (no takers)")
        else:
            print("Check passed: hardware plus SaaS ranks above rental, as in reality.")
    print()
    if "ihc-shared-leanheat" in ranked:
        pos, _ = ranked["ihc-shared-leanheat"]
        print(f"Info: shared Leanheat model ranks #{pos + 1} of {len(result['ranked'])} "
              "(outcome not yet known, so no expectation is tested).")
    if failures:
        print("BACKTEST FAILED:", "; ".join(failures))
        sys.exit(1)
    print("BACKTEST PASSED: rental ranks below all non-failed models, carries the failed-case warning, and hardware plus SaaS ranks above it.")


if __name__ == "__main__":
    main()
