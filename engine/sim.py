"""Cash-flow simulation per archetype. All default values are placeholders
(evidence: assumed) to be replaced with real inputs. Output is a standard
structure so the dashboard treats every archetype the same way."""

COMMON = [
    {"key": "years", "label": "Contract or analysis horizon", "unit": "years", "default": 7, "low": 5, "high": 10, "min": 3, "max": 20},
    {"key": "discount_rate", "label": "Discount rate", "unit": "share", "default": 0.08, "low": 0.05, "high": 0.12, "min": 0.0, "max": 0.2},
]


def P(key, label, unit, default, low, high, mn, mx):
    return {"key": key, "label": label, "unit": unit, "default": default, "low": low, "high": high, "min": mn, "max": mx}


PARAMS = {
    "hardware_saas": [
        P("units", "Customers (units sold)", "units", 5000, 2500, 10000, 50, 100000),
        P("hw_price", "Hardware price to customer", "EUR", 300, 200, 450, 0, 2000),
        P("hw_cost", "Hardware cost to provider", "EUR", 150, 120, 200, 0, 1500),
        P("install_cost", "Installation cost", "EUR", 120, 80, 200, 0, 1000),
        P("install_charged_share", "Share of installation charged to customer", "share", 0.5, 0.0, 1.0, 0.0, 1.0),
        P("saas_fee", "Software fee per year", "EUR", 40, 20, 80, 0, 400),
        P("support_cost", "Support cost per customer per year", "EUR", 15, 8, 30, 0, 200),
        P("churn", "Annual churn", "share", 0.08, 0.03, 0.15, 0.0, 0.5),
        P("saving_per_unit", "Customer energy saving per year", "EUR", 120, 60, 200, 0, 1000),
        P("fixed_cost", "Fixed platform cost per year", "EUR", 100000, 60000, 200000, 0, 2000000),
    ],
    "rental_leasing": [
        P("units", "Customers (units rented)", "units", 3000, 1500, 6000, 50, 100000),
        P("hw_cost", "Hardware cost to provider", "EUR", 300, 200, 450, 0, 3000),
        P("install_cost", "Installation cost", "EUR", 200, 120, 350, 0, 2000),
        P("monthly_rent", "Monthly rent", "EUR", 15, 8, 25, 0, 200),
        P("service_cost", "Service cost per customer per year", "EUR", 20, 10, 40, 0, 300),
        P("churn", "Annual early termination", "share", 0.05, 0.02, 0.15, 0.0, 0.5),
        P("saving_per_unit", "Customer energy saving per year", "EUR", 90, 40, 150, 0, 1000),
        P("fixed_cost", "Fixed platform cost per year", "EUR", 100000, 60000, 200000, 0, 2000000),
    ],
    "shared_savings": [
        P("units", "Sites", "units", 500, 250, 1000, 10, 10000),
        P("baseline_cost", "Baseline energy cost per site per year", "EUR", 20000, 10000, 40000, 1000, 200000),
        P("saving_pct", "Energy saving", "share", 0.12, 0.05, 0.15, 0.0, 0.4),
        P("provider_share", "Provider share of savings", "share", 0.4, 0.2, 0.6, 0.0, 0.9),
        P("measurement_haircut", "Savings not recognised after dispute", "share", 0.10, 0.0, 0.25, 0.0, 0.8),
        P("hw_cost", "Hardware cost per site", "EUR", 1500, 1000, 2500, 0, 20000),
        P("install_cost", "Installation cost per site", "EUR", 800, 500, 1500, 0, 10000),
        P("monitoring_cost", "Monitoring and service per site per year", "EUR", 150, 80, 300, 0, 2000),
        P("fixed_cost", "Fixed platform cost per year", "EUR", 100000, 60000, 200000, 0, 2000000),
    ],
    "guaranteed_savings": [
        P("units", "Sites", "units", 300, 150, 600, 5, 5000),
        P("baseline_cost", "Baseline energy cost per site per year", "EUR", 20000, 10000, 40000, 1000, 200000),
        P("guaranteed_pct", "Guaranteed saving", "share", 0.08, 0.05, 0.12, 0.0, 0.4),
        P("actual_pct", "Actual saving", "share", 0.12, 0.05, 0.15, 0.0, 0.4),
        P("excess_share", "Provider share of savings above the guarantee", "share", 0.3, 0.1, 0.5, 0.0, 1.0),
        P("hw_cost", "Hardware cost per site", "EUR", 1500, 1000, 2500, 0, 20000),
        P("install_cost", "Installation cost per site", "EUR", 800, 500, 1500, 0, 10000),
        P("project_margin", "Project margin on hardware and installation", "share", 0.2, 0.1, 0.35, 0.0, 1.0),
        P("service_fee", "Service fee per site per year", "EUR", 150, 100, 250, 0, 2000),
        P("service_cost", "Service cost per site per year", "EUR", 100, 60, 180, 0, 2000),
        P("fixed_cost", "Fixed platform cost per year", "EUR", 100000, 60000, 200000, 0, 2000000),
    ],
    "partner_commission": [
        P("units_per_year", "Units sold through the partner per year", "units", 500, 200, 1000, 10, 20000),
        P("unit_price", "Net price per unit", "EUR", 600, 450, 750, 0, 3000),
        P("unit_cost", "Cost per unit", "EUR", 250, 180, 330, 0, 2000),
        P("commission", "Commission per unit", "EUR", 80, 40, 150, 0, 1000),
        P("saas_fee", "Software fee per unit per year", "EUR", 40, 20, 80, 0, 400),
        P("support_cost", "Support cost per unit per year", "EUR", 10, 5, 20, 0, 200),
        P("churn", "Annual churn of installed base", "share", 0.08, 0.03, 0.15, 0.0, 0.5),
        P("saving_per_unit", "Customer energy saving per year", "EUR", 90, 40, 150, 0, 1000),
        P("onboarding_cost", "Partner onboarding and integration (one-off)", "EUR", 150000, 80000, 300000, 0, 2000000),
        P("fixed_cost", "Fixed cost per year", "EUR", 50000, 30000, 100000, 0, 2000000),
    ],
    "flexibility_revenue_share": [
        P("units", "Connected assets", "units", 5000, 2000, 10000, 100, 100000),
        P("revenue_per_asset", "Gross flexibility revenue per asset per year", "EUR", 150, 50, 300, 0, 1000),
        P("owner_share", "Share paid to asset owner", "share", 0.5, 0.3, 0.7, 0.0, 1.0),
        P("market_fee_share", "Share paid to trading partner", "share", 0.1, 0.05, 0.2, 0.0, 0.5),
        P("platform_cost", "Platform cost per asset per year", "EUR", 12, 6, 25, 0, 200),
        P("hw_subsidy", "Hardware subsidy per asset (one-off)", "EUR", 0, 0, 200, 0, 2000),
        P("churn", "Annual churn", "share", 0.05, 0.02, 0.12, 0.0, 0.5),
        P("fixed_cost", "Fixed cost per year", "EUR", 300000, 150000, 600000, 0, 5000000),
    ],
    "tenant_energy": [
        P("units", "Buildings", "units", 5, 1, 20, 1, 500),
        P("pv_kwp", "PV size per building", "kWp", 60, 30, 100, 5, 500),
        P("yield_kwh", "Yield per kWp per year", "kWh", 950, 850, 1050, 500, 1400),
        P("tenant_use_share", "Share of PV output consumed by tenants", "share", 0.6, 0.4, 0.8, 0.0, 1.0),
        P("participation", "Tenant participation rate", "share", 0.7, 0.3, 0.9, 0.0, 1.0),
        P("grid_price", "Grid electricity price", "EUR/kWh", 0.35, 0.28, 0.45, 0.05, 1.0),
        P("tenant_discount", "Discount of tenant price vs grid price", "share", 0.1, 0.05, 0.2, 0.0, 0.5),
        P("surcharge", "Federal surcharge per tenant-consumed kWh", "EUR/kWh", 0.02, 0.0, 0.03, 0.0, 0.1),
        P("feed_in", "Feed-in tariff for surplus", "EUR/kWh", 0.08, 0.06, 0.1, 0.0, 0.3),
        P("capex_per_kwp", "Capex per kWp", "EUR", 1400, 1100, 1800, 300, 4000),
        P("opex_per_kwp", "Opex per kWp per year", "EUR", 20, 10, 30, 0, 100),
        P("admin_cost", "Billing and administration per building per year", "EUR", 1500, 800, 3000, 0, 20000),
    ],
    "ev_charging": [
        P("units", "Chargers", "units", 20, 5, 50, 1, 2000),
        P("kwh_per_day", "Energy sold per charger per day", "kWh", 80, 30, 150, 5, 500),
        P("margin_per_kwh", "Gross margin per kWh", "EUR", 0.12, 0.06, 0.2, 0.0, 0.5),
        P("host_share", "Share of margin paid to site host", "share", 0.1, 0.0, 0.25, 0.0, 0.6),
        P("capex_per_charger", "Capex per charger incl. grid connection", "EUR", 25000, 15000, 40000, 2000, 150000),
        P("opex_per_charger", "Opex per charger per year", "EUR", 2500, 1500, 4000, 0, 20000),
        P("fixed_cost", "Fixed cost per year", "EUR", 50000, 20000, 100000, 0, 2000000),
    ],
    "tariff_bundle": [
        P("units_per_year", "New customers per year", "units", 5000, 2000, 10000, 100, 100000),
        P("margin_per_customer", "Supply margin per customer per year", "EUR", 55, 25, 90, 0, 300),
        P("device_subsidy", "Device subsidy per customer (one-off)", "EUR", 60, 20, 200, 0, 1500),
        P("cac", "Customer acquisition cost", "EUR", 50, 25, 100, 0, 500),
        P("service_cost", "Service cost per customer per year", "EUR", 10, 5, 20, 0, 200),
        P("churn", "Annual churn", "share", 0.15, 0.08, 0.25, 0.0, 0.6),
        P("saving_per_customer", "Customer saving per year", "EUR", 120, 40, 250, 0, 1500),
        P("fixed_cost", "Fixed cost per year", "EUR", 150000, 80000, 300000, 0, 5000000),
    ],
}
PARAMS["submetering"] = PARAMS["hardware_saas"]
SIMULATABLE = set(PARAMS)

STAKEHOLDER_LABELS = {
    "hardware_saas": ("Provider", "Customer", "None"),
    "rental_leasing": ("Provider", "Customer", "None"),
    "shared_savings": ("Provider", "Customer", "None"),
    "guaranteed_savings": ("Provider", "Customer", "None"),
    "partner_commission": ("Provider", "Customer", "Partner"),
    "flexibility_revenue_share": ("Aggregator", "Asset owner", "Trading partner"),
    "tenant_energy": ("Provider or landlord", "Tenants", "None"),
    "ev_charging": ("Operator", "None", "Site host"),
    "tariff_bundle": ("Supplier", "Customer", "None"),
}


def specs(archetype):
    if archetype not in PARAMS:
        raise ValueError(f"No simulation for archetype {archetype}")
    return COMMON + PARAMS[archetype]


def defaults(archetype):
    return {s["key"]: s["default"] for s in specs(archetype)}


def _cohort_base(new_per_year, churn, years):
    """Installed base at each year t=1..years for cohorts added at start of each year."""
    base = []
    for t in range(1, years + 1):
        total = 0.0
        for c in range(1, t + 1):
            total += new_per_year * (1 - churn) ** (t - c)
        base.append(total)
    return base


def _simulate_raw(archetype, p):
    n = int(round(p["years"]))
    prov = [0.0] * (n + 1)
    cust = [0.0] * (n + 1)
    part = [0.0] * (n + 1)

    if archetype in ("hardware_saas", "submetering"):
        u = p["units"]
        prov[0] = u * (p["hw_price"] - p["hw_cost"] - p["install_cost"] * (1 - p["install_charged_share"]))
        cust[0] = -u * (p["hw_price"] + p["install_cost"] * p["install_charged_share"])
        for t in range(1, n + 1):
            alive = u * (1 - p["churn"]) ** (t - 1)
            prov[t] = alive * (p["saas_fee"] - p["support_cost"]) - p["fixed_cost"]
            cust[t] = alive * (p["saving_per_unit"] - p["saas_fee"])

    elif archetype == "rental_leasing":
        u = p["units"]
        prov[0] = -u * (p["hw_cost"] + p["install_cost"])
        for t in range(1, n + 1):
            alive = u * (1 - p["churn"]) ** (t - 1)
            rent = p["monthly_rent"] * 12
            prov[t] = alive * (rent - p["service_cost"]) - p["fixed_cost"]
            cust[t] = alive * (p["saving_per_unit"] - rent)

    elif archetype == "shared_savings":
        u = p["units"]
        gross = p["baseline_cost"] * p["saving_pct"]
        recognised = gross * (1 - p["measurement_haircut"])
        prov[0] = -u * (p["hw_cost"] + p["install_cost"])
        for t in range(1, n + 1):
            fee = u * recognised * p["provider_share"]
            prov[t] = fee - u * p["monitoring_cost"] - p["fixed_cost"]
            cust[t] = u * gross - fee

    elif archetype == "guaranteed_savings":
        u = p["units"]
        price = (p["hw_cost"] + p["install_cost"]) * (1 + p["project_margin"])
        prov[0] = u * (price - p["hw_cost"] - p["install_cost"])
        cust[0] = -u * price
        guaranteed = p["baseline_cost"] * p["guaranteed_pct"]
        actual = p["baseline_cost"] * p["actual_pct"]
        for t in range(1, n + 1):
            if actual >= guaranteed:
                comp, excess = 0.0, (actual - guaranteed) * p["excess_share"]
            else:
                comp, excess = guaranteed - actual, 0.0
            prov[t] = u * (p["service_fee"] - p["service_cost"] + excess - comp) - p["fixed_cost"]
            cust[t] = u * (actual + comp - excess - p["service_fee"])

    elif archetype == "partner_commission":
        base = _cohort_base(p["units_per_year"], p["churn"], n)
        prov[0] = -p["onboarding_cost"]
        for t in range(1, n + 1):
            new = p["units_per_year"]
            installed = base[t - 1]
            prov[t] = new * (p["unit_price"] - p["unit_cost"] - p["commission"]) + installed * (p["saas_fee"] - p["support_cost"]) - p["fixed_cost"]
            part[t] = new * p["commission"]
            cust[t] = installed * p["saving_per_unit"] - installed * p["saas_fee"] - new * p["unit_price"]

    elif archetype == "flexibility_revenue_share":
        u = p["units"]
        prov[0] = -u * p["hw_subsidy"]
        for t in range(1, n + 1):
            alive = u * (1 - p["churn"]) ** (t - 1)
            gross = alive * p["revenue_per_asset"]
            fee = gross * p["market_fee_share"]
            owner = (gross - fee) * p["owner_share"]
            prov[t] = gross - fee - owner - alive * p["platform_cost"] - p["fixed_cost"]
            cust[t] = owner
            part[t] = fee

    elif archetype == "tenant_energy":
        b = p["units"]
        pv_kwh = p["pv_kwp"] * p["yield_kwh"]
        tenant_kwh = pv_kwh * p["tenant_use_share"] * p["participation"]
        surplus = pv_kwh - tenant_kwh
        price = p["grid_price"] * (1 - p["tenant_discount"])
        prov[0] = -b * p["pv_kwp"] * p["capex_per_kwp"]
        for t in range(1, n + 1):
            prov[t] = b * (tenant_kwh * (price + p["surcharge"]) + surplus * p["feed_in"] - p["pv_kwp"] * p["opex_per_kwp"] - p["admin_cost"])
            cust[t] = b * tenant_kwh * (p["grid_price"] - price)

    elif archetype == "ev_charging":
        u = p["units"]
        prov[0] = -u * p["capex_per_charger"]
        margin_year = p["kwh_per_day"] * 365 * p["margin_per_kwh"]
        for t in range(1, n + 1):
            prov[t] = u * (margin_year * (1 - p["host_share"]) - p["opex_per_charger"]) - p["fixed_cost"]
            part[t] = u * margin_year * p["host_share"]

    elif archetype == "tariff_bundle":
        base = _cohort_base(p["units_per_year"], p["churn"], n)
        for t in range(1, n + 1):
            new = p["units_per_year"]
            installed = base[t - 1]
            prov[t] = installed * (p["margin_per_customer"] - p["service_cost"]) - new * (p["device_subsidy"] + p["cac"]) - p["fixed_cost"]
            cust[t] = installed * p["saving_per_customer"]
    else:
        raise ValueError(f"No simulation for archetype {archetype}")
    return prov, cust, part


def npv(flows, rate):
    return sum(f / (1 + rate) ** t for t, f in enumerate(flows))


def payback_year(flows):
    cum = 0.0
    for t, f in enumerate(flows):
        prev = cum
        cum += f
        if t > 0 and prev < 0 <= cum and f > 0:
            return t - 1 + (-prev / f)
        if t == 0 and cum >= 0 and len(flows) > 1 and all(x >= 0 for x in flows):
            return 0.0
    return None


def simulate(archetype, params=None):
    p = defaults(archetype)
    p.update(params or {})
    prov, cust, part = _simulate_raw(archetype, p)
    r = p["discount_rate"]
    cum, c = [], 0.0
    for f in prov:
        c += f
        cum.append(c)
    labels = STAKEHOLDER_LABELS.get(archetype, ("Provider", "Customer", "Partner"))
    return {
        "archetype": archetype, "params": p, "labels": labels,
        "provider_cf": prov, "customer_cf": cust, "partner_cf": part, "provider_cum": cum,
        "npv_provider": npv(prov, r), "npv_customer": npv(cust, r), "npv_partner": npv(part, r),
        "payback_years": payback_year(prov), "peak_funding": min(cum),
        "total_provider": sum(prov),
    }


def tornado(archetype, params=None):
    base = simulate(archetype, params)
    rows = []
    for s in specs(archetype):
        k = s["key"]
        if k == "discount_rate":
            continue
        lo = simulate(archetype, {**base["params"], k: s["low"]})["npv_provider"]
        hi = simulate(archetype, {**base["params"], k: s["high"]})["npv_provider"]
        rows.append({"key": k, "label": s["label"], "low_input": s["low"], "high_input": s["high"],
                     "npv_low": min(lo, hi), "npv_high": max(lo, hi), "impact": abs(hi - lo)})
    rows.sort(key=lambda r: r["impact"], reverse=True)
    return rows, base["npv_provider"]


def break_evens(archetype, params=None):
    """For each parameter, find the value at which provider NPV crosses zero within its allowed range."""
    base = simulate(archetype, params)
    out = []
    for s in specs(archetype):
        k = s["key"]
        if k in ("discount_rate", "years"):
            continue
        lo, hi = s["min"], s["max"]
        f = lambda v: simulate(archetype, {**base["params"], k: v})["npv_provider"]
        f_lo, f_hi = f(lo), f(hi)
        if f_lo == f_hi or (f_lo > 0) == (f_hi > 0):
            continue
        a, b = lo, hi
        for _ in range(60):
            mid = (a + b) / 2
            if (f(mid) > 0) == (f_hi > 0):
                b = mid
            else:
                a = mid
        value = (a + b) / 2
        out.append({"key": k, "label": s["label"], "unit": s["unit"], "value": value,
                    "needs": "at least" if f_hi > 0 else "at most", "current": base["params"][k]})
    out.sort(key=lambda r: abs(r["value"] - r["current"]) / (abs(r["current"]) + 1e-9))
    return out
