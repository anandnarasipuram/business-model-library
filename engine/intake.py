"""Turn a plain-text use case into a profile. Uses the LLM when a key is set,
otherwise a keyword fallback. Always returns (profile, used_fallback)."""
import re
from pathlib import Path

from engine.match import DEFAULT_PROFILE

PROMPT = Path(__file__).resolve().parent.parent / "prompts" / "intake.txt"

SEGMENT_WORDS = [
    ("mfh", r"apartment|multi-?family|landlord|housing|tenant|mfh|wohnung|mehrfamilien"),
    ("industrial", r"factory|industrial|plant|manufactur"),
    ("public", r"municipal|school|public|city|hospital"),
    ("commercial", r"office|retail|hotel|commercial|shop|warehouse"),
    ("sfh", r"single-?family|homeowner|household|one-family|einfamilien|\bhome\b|\bhouse\b"),
]


DOMAIN_WORDS = [
    ("mobility", r"ev charging|charger|wallbox|electric vehicle|\bev\b"),
    ("flexibility", r"battery|storage|flexib|virtual power|vpp|aggregat"),
    ("heating", r"heat|boiler|radiator|thermostat|hydraulic"),
    ("electricity", r"electricity|solar|pv|tariff|power supply|mieterstrom"),
]


def keyword_profile(text: str) -> dict:
    t = text.lower()
    profile = dict(DEFAULT_PROFILE)
    assumed = set(DEFAULT_PROFILE)
    for seg, pattern in SEGMENT_WORDS:
        if re.search(pattern, t):
            profile["segment"] = seg
            assumed.discard("segment")
            break
    for dom, pattern in DOMAIN_WORDS:
        if re.search(pattern, t):
            profile["domain"] = dom
            assumed.discard("domain")
            break
    if re.search(r"no upfront|zero upfront|no capex|without upfront|no investment", t):
        profile["max_customer_capex"] = "none"
        assumed.discard("max_customer_capex")
    elif re.search(r"small upfront|low upfront|low capex", t):
        profile["max_customer_capex"] = "low"
        assumed.discard("max_customer_capex")
    elif re.search(r"customer (pays|funds|buys)|can afford|capex budget", t):
        profile["max_customer_capex"] = "high"
        assumed.discard("max_customer_capex")
    if re.search(r"cannot finance|can't finance|no financing|no balance sheet", t):
        profile["provider_can_finance"] = False
        assumed.discard("provider_can_finance")
    elif re.search(r"we finance|can finance|own financing|balance sheet", t):
        profile["provider_can_finance"] = True
        assumed.discard("provider_can_finance")
    if re.search(r"no installer|without installer", t):
        profile["has_installer_network"] = False
        assumed.discard("has_installer_network")
    elif re.search(r"installer", t):
        profile["has_installer_network"] = True
        assumed.discard("has_installer_network")
    if re.search(r"no smart meter|without smart meter", t):
        profile["smart_meter_available"] = False
        assumed.discard("smart_meter_available")
    elif re.search(r"smart meter", t):
        profile["smart_meter_available"] = True
        assumed.discard("smart_meter_available")
    profile["summary"] = text.strip()[:200]
    profile["assumed_fields"] = sorted(assumed)
    return profile


def profile_from_text(text: str):
    try:
        from engine.llm import _call_llm_json

        result = _call_llm_json(PROMPT.read_text(encoding="utf-8"), text)
        profile = dict(DEFAULT_PROFILE)
        for key in DEFAULT_PROFILE:
            if key in result:
                profile[key] = result[key]
        profile["summary"] = result.get("summary", text[:200])
        profile["assumed_fields"] = result.get("assumed_fields", [])
        return profile, False
    except Exception:
        return keyword_profile(text), True
