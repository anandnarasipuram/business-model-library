"""Hard filters, then a fit score, for a use case profile against catalog entries."""

CAPEX_ORDER = {"none": 0, "low": 1, "high": 2}
EVIDENCE_PENALTY = {"documented": 0, "inferred": 5, "assumed": 10, "speculative": 15}
OUTCOME_PENALTY = {"successful": 0, "unproven": 5, "niche": 10, "pivoted": 15, "failed": 30}
SOFT_PENALTY = 20

SEGMENTS = {
    "sfh": "Single-family homes",
    "mfh": "Multi-family buildings",
    "commercial": "Commercial buildings",
    "public": "Public buildings",
    "industrial": "Industrial sites",
}
DOMAINS = {"heating": "Heating", "electricity": "Electricity supply", "flexibility": "Flexibility and storage", "mobility": "EV charging", "general": "General efficiency"}
CAPEX_LABELS = {"none": "None (zero upfront)", "low": "Low (small upfront)", "high": "Customer can fund it"}

DEFAULT_PROFILE = {
    "segment": "mfh",
    "domain": "heating",
    "max_customer_capex": "none",
    "provider_can_finance": True,
    "savings_measurable": True,
    "has_installer_network": True,
    "has_own_hardware": True,
    "smart_meter_available": False,
}


def rank(profile: dict, entries: list) -> dict:
    """Return {"ranked": [...], "excluded": [...]} sorted by score."""
    ranked, excluded = [], []
    for e in entries:
        m = e.get("match")
        if not m:
            continue
        needs = m["needs"]
        reasons = []
        doms = m.get("domains", ["general"])
        if "general" not in doms and profile["domain"] not in doms:
            reasons.append("Different topic area than your use case")
        if profile["segment"] not in m["segments"]:
            reasons.append("Segment not covered by this model")
        if CAPEX_ORDER[m["customer_capex"]] > CAPEX_ORDER[profile["max_customer_capex"]]:
            reasons.append("Customer would need to pay more upfront than they accept")
        if needs["provider_financing"] and not profile["provider_can_finance"]:
            reasons.append("Needs the provider to finance equipment, which you cannot do")
        if needs["measurable_savings"] and not profile["savings_measurable"]:
            reasons.append("Needs credible savings measurement, which is not available")
        if reasons:
            excluded.append({"id": e["id"], "name": e["name"], "archetype": e["archetype"], "reasons": reasons})
            continue

        penalties = []
        if needs["installer_network"] and not profile["has_installer_network"]:
            penalties.append(("No installer network", SOFT_PENALTY))
        if needs["own_hardware"] and not profile["has_own_hardware"]:
            penalties.append(("No own hardware", SOFT_PENALTY))
        if needs["smart_meter"] and not profile["smart_meter_available"]:
            penalties.append(("Needs smart metering that is not available", SOFT_PENALTY))
        ev = EVIDENCE_PENALTY[e["evidence"]]
        if ev:
            penalties.append((f"Evidence is {e['evidence']}", ev))
        oc = OUTCOME_PENALTY[e["outcome"]]
        if oc:
            penalties.append((f"Outcome is {e['outcome']}", oc))
        documented_risks = sum(1 for r in e["risks_failure_causes"] if r["evidence"] == "documented")
        if documented_risks:
            penalties.append((f"{documented_risks} documented risk(s)", min(15, 3 * documented_risks)))
        score = max(0, 100 - sum(p for _, p in penalties))

        warnings = [f"{r['text']} ({r['evidence']})" for r in e["risks_failure_causes"]]
        for c in e.get("cases", []):
            if c.get("outcome") == "failed":
                warnings.insert(0, f"Failed case: {c['company']}: {c['note']}")
        ranked.append({
            "id": e["id"], "name": e["name"], "archetype": e["archetype"], "score": score,
            "penalties": penalties, "warnings": warnings,
            "evidence": e["evidence"], "outcome": e["outcome"], "visibility": e["visibility"],
        })
    ranked.sort(key=lambda r: (-r["score"], r["name"]))
    return {"ranked": ranked, "excluded": excluded}
