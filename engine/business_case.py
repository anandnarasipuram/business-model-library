"""Revenue estimation and sensitivity (tornado) analysis for the business case."""

INPUT_LABELS = {
    "sites": "Number of sites",
    "cooling_load_kW": "Cooling load per site (kW)",
    "utilisation": "Utilisation factor",
    "efficiency_gain": "Efficiency gain",
    "electricity_price_EUR_per_MWh": "Electricity price (EUR/MWh)",
    "value_capture_share": "Value capture share",
}

# Per-input sensitivity ranges for the tornado chart. "relative" multiplies the
# current input value (e.g. sites at 50-150% of base); "absolute" uses a fixed
# low/high regardless of the current value, since these are plausible real-world
# bounds rather than a swing around whatever the base happens to be.
INPUT_RANGES = {
    "sites": ("relative", 0.5, 1.5),
    "cooling_load_kW": ("relative", 0.75, 1.25),
    "utilisation": ("absolute", 0.6, 0.9),
    "efficiency_gain": ("absolute", 0.05, 0.15),
    "electricity_price_EUR_per_MWh": ("absolute", 80, 250),
    "value_capture_share": ("absolute", 0.10, 0.30),
}


def compute_revenue(inputs: dict) -> dict:
    """Compute annual cooling energy, customer savings, and annual revenue.

    annual_cooling_energy_MWh = sites * cooling_load_kW * 8760 * utilisation / 1000
    customer_savings_EUR = annual_cooling_energy_MWh * efficiency_gain * electricity_price
    annual_revenue_EUR = customer_savings_EUR * value_capture_share
    """
    annual_cooling_energy_MWh = (
        inputs["sites"] * inputs["cooling_load_kW"] * 8760 * inputs["utilisation"] / 1000
    )
    customer_savings_EUR = (
        annual_cooling_energy_MWh
        * inputs["efficiency_gain"]
        * inputs["electricity_price_EUR_per_MWh"]
    )
    annual_revenue_EUR = customer_savings_EUR * inputs["value_capture_share"]
    return {
        "annual_cooling_energy_MWh": annual_cooling_energy_MWh,
        "customer_savings_EUR": customer_savings_EUR,
        "annual_revenue_EUR": annual_revenue_EUR,
    }


def tornado_data(inputs: dict) -> tuple:
    """For each input, vary it across its INPUT_RANGES bound and measure the
    impact on annual revenue.

    Returns (rows, base_revenue) where rows is a list of dicts sorted by
    impact (absolute swing in revenue, descending), each with:
    key, label, low_revenue, high_revenue, impact (high - low).
    """
    base_revenue = compute_revenue(inputs)["annual_revenue_EUR"]
    rows = []
    for key, (range_type, low_bound, high_bound) in INPUT_RANGES.items():
        low_inputs = dict(inputs)
        high_inputs = dict(inputs)
        if range_type == "relative":
            low_inputs[key] = inputs[key] * low_bound
            high_inputs[key] = inputs[key] * high_bound
        else:
            low_inputs[key] = low_bound
            high_inputs[key] = high_bound
        low_revenue = compute_revenue(low_inputs)["annual_revenue_EUR"]
        high_revenue = compute_revenue(high_inputs)["annual_revenue_EUR"]
        rows.append(
            {
                "key": key,
                "label": INPUT_LABELS[key],
                "low_revenue": min(low_revenue, high_revenue),
                "high_revenue": max(low_revenue, high_revenue),
                "impact": abs(high_revenue - low_revenue),
            }
        )
    rows.sort(key=lambda r: r["impact"], reverse=True)
    return rows, base_revenue
