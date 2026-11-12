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
    "max_customer_capex": "none",
    "provider_can_finance": True,
    "savings_measurable": True,
    "has_installer_network": True,
    "has_own_hardware": True,
    "smart_meter_available": False,
}


def main():
    entries = load_entries(include_private=True)
    result = rank(PROFILE, entries)
    print("Profile: heating in multi-family buildings, zero upfront for customer, provider can finance,")
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
    print()
    if "ihc-shared-leanheat" in ranked:
        pos, _ = ranked["ihc-shared-leanheat"]
        print(f"Info: shared Leanheat model ranks #{pos + 1} of {len(result['ranked'])} "
              "(its mechanics are still marked TO CONFIRM, so this is not yet a real test).")
    if failures:
        print("BACKTEST FAILED:", "; ".join(failures))
        sys.exit(1)
    print("BACKTEST PASSED: rental ranks below all non-failed models and carries the failed-case warning.")


if __name__ == "__main__":
    main()
