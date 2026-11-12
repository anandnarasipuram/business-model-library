"""Business Model Library: advisor and simulator (Streamlit).

Run:  streamlit run app.py
Set BML_PRIVATE=1 to include private entries (local use only).
"""
import plotly.graph_objects as go
import streamlit as st

from engine import sim
from engine.catalog import load_entries
from engine.intake import profile_from_text
from engine.match import CAPEX_LABELS, DEFAULT_PROFILE, DOMAINS, SEGMENTS, rank

st.set_page_config(page_title="Business Model Library", layout="wide")


@st.cache_data
def entries():
    return load_entries()


def by_id():
    return {e["id"]: e for e in entries()}


def eur(x):
    return f"EUR {x:,.0f}"


def page_advisor():
    st.header("Advisor")
    st.caption("Describe a use case or set the profile directly. Models are filtered, then ranked. "
               "Scores reflect fit, evidence and known outcomes, not a forecast.")
    text = st.text_area("Use case in plain words", height=90,
                        placeholder="Housing company with 40 apartment buildings wants lower heating cost, no upfront investment, we have an installer network")
    if st.button("Read use case") and text.strip():
        profile, fallback = profile_from_text(text)
        st.session_state.profile = profile
        st.session_state.intake_fallback = fallback
    profile = st.session_state.get("profile", dict(DEFAULT_PROFILE))
    if st.session_state.get("intake_fallback"):
        st.info("Read with simple keyword rules (no AI key set or AI unavailable). Check the profile below.")
    if profile.get("assumed_fields"):
        st.warning("Assumed, not stated: " + ", ".join(profile["assumed_fields"]))

    c1, c2, c3 = st.columns(3)
    profile["domain"] = c1.selectbox("Topic", list(DOMAINS), index=list(DOMAINS).index(profile["domain"]), format_func=DOMAINS.get)
    profile["segment"] = c2.selectbox("Customer segment", list(SEGMENTS), index=list(SEGMENTS).index(profile["segment"]), format_func=SEGMENTS.get)
    profile["max_customer_capex"] = c3.selectbox("Upfront payment customer accepts", list(CAPEX_LABELS), index=list(CAPEX_LABELS).index(profile["max_customer_capex"]), format_func=CAPEX_LABELS.get)
    d1, d2, d3, d4 = st.columns(4)
    profile["provider_can_finance"] = d1.checkbox("We can finance equipment", profile["provider_can_finance"])
    profile["savings_measurable"] = d2.checkbox("Savings can be measured", profile["savings_measurable"])
    profile["has_installer_network"] = d3.checkbox("We have installers", profile["has_installer_network"])
    profile["has_own_hardware"] = d4.checkbox("We have our own hardware", profile["has_own_hardware"])
    profile["smart_meter_available"] = st.checkbox("Smart metering available", profile["smart_meter_available"])
    st.session_state.profile = profile

    result = rank(profile, entries())
    st.subheader(f"Ranked models ({len(result['ranked'])})")
    if not result["ranked"]:
        st.write("Not covered yet. No model in the library fits this profile.")
    for r in result["ranked"]:
        with st.expander(f"{r['score']}  {r['name']}  ({r['outcome']}, {r['evidence']})"):
            if r["penalties"]:
                st.write("Score reduced by: " + "; ".join(f"{n} (-{p})" for n, p in r["penalties"]))
            st.markdown("**Known risks and failures**")
            for w in r["warnings"]:
                st.write("- " + w)
            if st.button("Simulate this model", key=f"sim_{r['id']}"):
                st.session_state.sim_id = r["id"]
                st.session_state.goto = "Simulator"
                st.rerun()
    with st.expander(f"Excluded models ({len(result['excluded'])})"):
        for x in result["excluded"]:
            st.write(f"**{x['name']}**: " + "; ".join(x["reasons"]))


def page_simulator():
    st.header("Simulator")
    lookup = by_id()
    ids = [e["id"] for e in entries() if e["archetype"] in sim.SIMULATABLE]
    current = st.session_state.get("sim_id", ids[0])
    entry_id = st.selectbox("Model", ids, index=ids.index(current) if current in ids else 0,
                            format_func=lambda i: lookup[i]["name"])
    st.session_state.sim_id = entry_id
    entry = lookup[entry_id]
    arch = entry["archetype"]
    st.caption("All input values are placeholders marked 'assumed' until you replace them. "
               "Change a slider and every result below updates.")

    values = {}
    cols = st.columns(2)
    for i, s in enumerate(sim.specs(arch)):
        with cols[i % 2]:
            lo, hi = s["min"], s["max"]
            step = (hi - lo) / 200 if isinstance(s["default"], float) else max(1, int((hi - lo) / 200))
            values[s["key"]] = st.slider(f"{s['label']} ({s['unit']})", float(lo) if isinstance(s["default"], float) else int(lo),
                                         float(hi) if isinstance(s["default"], float) else int(hi),
                                         s["default"], step=step if isinstance(s["default"], float) else step, key=f"{arch}_{s['key']}")
    res = sim.simulate(arch, values)
    plabel, clabel, partlabel = res["labels"]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(f"{plabel} NPV", eur(res["npv_provider"]))
    k2.metric("Payback", f"{res['payback_years']:.1f} years" if res["payback_years"] else "not within horizon")
    k3.metric("Peak funding need", eur(-res["peak_funding"]) if res["peak_funding"] < 0 else "none")
    k4.metric(f"{clabel} NPV", eur(res["npv_customer"]) if clabel != "None" else "n/a")

    years = list(range(len(res["provider_cf"])))
    fig = go.Figure()
    fig.add_bar(x=years, y=res["provider_cf"], name=f"{plabel} cash flow")
    fig.add_scatter(x=years, y=res["provider_cum"], name=f"{plabel} cumulative", mode="lines+markers")
    fig.update_layout(height=320, margin=dict(t=20, b=20), xaxis_title="Year", yaxis_title="EUR")
    st.plotly_chart(fig, width="stretch")

    st.subheader("Who gets what (discounted value over the horizon)")
    labels, vals = [], []
    for lab, v in ((plabel, res["npv_provider"]), (clabel, res["npv_customer"]), (partlabel, res["npv_partner"])):
        if lab != "None":
            labels.append(lab)
            vals.append(v)
    fig2 = go.Figure(go.Bar(x=vals, y=labels, orientation="h"))
    fig2.update_layout(height=200, margin=dict(t=10, b=10), xaxis_title="EUR")
    st.plotly_chart(fig2, width="stretch")
    if clabel != "None" and res["npv_customer"] < 0:
        st.warning(f"{clabel} lose money in this setup. Expect weak demand unless price or savings change.")

    left, right = st.columns(2)
    with left:
        st.subheader("What drives the result")
        rows, base = sim.tornado(arch, values)
        top = rows[:8][::-1]
        fig3 = go.Figure()
        fig3.add_bar(y=[r["label"] for r in top], x=[r["npv_low"] - base for r in top], base=[base] * len(top), orientation="h", name="low or high end")
        fig3.add_bar(y=[r["label"] for r in top], x=[r["npv_high"] - base for r in top], base=[base] * len(top), orientation="h", name="other end")
        fig3.update_layout(barmode="overlay", height=360, margin=dict(t=10, b=10), xaxis_title="Provider NPV (EUR)", showlegend=False)
        st.plotly_chart(fig3, width="stretch")
    with right:
        st.subheader("What must be true")
        be = sim.break_evens(arch, values)
        if res["npv_provider"] >= 0:
            st.write("The model is positive now. It turns negative if:")
        else:
            st.write("The model is negative now. It turns positive if:")
        for b in be[:6]:
            st.write(f"- **{b['label']}** is {b['needs']} {b['value']:,.2f} {b['unit']} (now {b['current']:,.2f})")
        if not be:
            st.write("No single input flips the result within its allowed range.")
        st.markdown("**From the library entry**")
        for w in entry["what_must_be_true"]:
            st.write("- " + w)


def page_library():
    st.header("Library")
    q = st.text_input("Search")
    for e in entries():
        if q and q.lower() not in str(e).lower():
            continue
        with st.expander(f"{e['name']}  ({e['archetype']}, {e['outcome']}, {e['evidence']})"):
            st.write(e["summary"])
            st.write("**How it makes money:** " + e["how_it_makes_money"])
            st.write("**Building blocks**")
            for k, v in e["building_blocks"].items():
                if v:
                    st.write(f"- {k.replace('_', ' ')}: " + "; ".join(v))
            st.write("**Sources**")
            for s in e["sources"]:
                st.write(f"- [{s['id']}] " + (f"[{s['title']}]({s['url']})" if s["url"] else s["title"]) + f" ({s['kind']})")


def main():
    pages = {"Advisor": page_advisor, "Simulator": page_simulator, "Library": page_library}
    st.sidebar.title("Business Model Library")
    if "goto" in st.session_state:
        st.session_state.nav = st.session_state.pop("goto")
    page = st.sidebar.radio("Page", list(pages), key="nav")
    if any(e["visibility"] == "private" for e in entries()):
        st.sidebar.warning("Private entries are loaded. Do not share screenshots.")
    pages[page]()


main()
