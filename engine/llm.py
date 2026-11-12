"""LLM provider switch with strict JSON output, one retry, and offline fallback.

The app must never crash because of a missing key, slow network, or bad
JSON from the model. Every public function here returns a (result, used_fallback)
tuple so callers can show an "offline example" tag when needed.
"""

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

TIMEOUT_SECONDS = 10
BASE_DIR = Path(__file__).parent


def _provider():
    return os.getenv("LLM_PROVIDER", "anthropic").strip().lower()


def _extract_json(text: str) -> dict:
    """Pull a JSON object out of model output, tolerating stray code fences."""
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output")
    return json.loads(match.group(0))


def _call_anthropic(system_prompt: str, user_message: str) -> str:
    from anthropic import Anthropic

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), timeout=TIMEOUT_SECONDS)
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
    response = client.messages.create(
        model=model,
        max_tokens=1500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def _call_openai(system_prompt: str, user_message: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=TIMEOUT_SECONDS)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


def _call_cohere(system_prompt: str, user_message: str) -> str:
    import requests

    model = os.getenv("COHERE_MODEL", "command-a-plus-05-2026")
    response = requests.post(
        "https://api.cohere.com/v2/chat",
        headers={
            "Authorization": f"Bearer {os.getenv('COHERE_API_KEY')}",
            "Content-Type": "application/json",
        },
        json={
            "stream": False,
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        },
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    blocks = response.json()["message"]["content"]
    text_block = next(b for b in blocks if b.get("type") == "text")
    return text_block["text"]


_PROVIDER_CALLS = {
    "anthropic": _call_anthropic,
    "openai": _call_openai,
    "cohere": _call_cohere,
}
_PROVIDER_KEY_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "cohere": "COHERE_API_KEY",
}


def _call_llm_json(system_prompt: str, user_message: str) -> dict:
    """Call the configured provider and parse JSON, retrying once on failure."""
    provider = _provider()
    key_env = _PROVIDER_KEY_ENV.get(provider)
    if key_env and not os.getenv(key_env):
        raise RuntimeError(f"Missing {key_env}")

    call = _PROVIDER_CALLS.get(provider, _call_anthropic)

    last_error = None
    for _ in range(2):
        try:
            raw_text = call(system_prompt, user_message)
            return _extract_json(raw_text)
        except Exception as exc:  # noqa: BLE001 - any failure should trigger fallback
            last_error = exc
    raise RuntimeError(f"LLM call failed after retry: {last_error}")


def _closest_fallback(idea_text: str) -> dict:
    """Pick the fallback intake example whose keywords best match the idea text."""
    with open(BASE_DIR / "data" / "fallback_intake.json") as f:
        examples = json.load(f)

    idea_lower = idea_text.lower()
    best_match, best_score = None, -1
    for example in examples:
        keywords = example["keywords"]
        if keywords == ["default"]:
            continue
        score = sum(1 for kw in keywords if kw in idea_lower)
        if score > best_score:
            best_score, best_match = score, example

    if best_match is None or best_score <= 0:
        best_match = next(e for e in examples if e["keywords"] == ["default"])

    return best_match["result"]


def structure_idea(idea_text: str) -> tuple:
    """Structure a plain-English idea into the intake JSON schema.

    Returns (result_dict, used_fallback: bool).
    """
    system_prompt = (BASE_DIR / "prompts" / "intake.txt").read_text()
    try:
        result = _call_llm_json(system_prompt, idea_text)
        required = {
            "title", "problem", "target_customer", "existing_asset_used",
            "revenue_model", "key_hypothesis", "what_would_disprove_it",
            "first_validation_step", "main_risks", "suggested_scores",
        }
        if not required.issubset(result.keys()):
            raise ValueError("Model response missing required fields")
        return result, False
    except Exception:
        return _closest_fallback(idea_text), True


def _template_summary(opportunity: dict, business_case: dict) -> dict:
    """Deterministic fallback executive summary built from the opportunity data."""
    revenue = business_case.get("annual_revenue_EUR", 0)
    return {
        "recommendation": opportunity.get("stage", "Explore"),
        "why": (
            f"Based on current scoring and stage ({opportunity.get('stage', 'Explore')}), "
            f"this opportunity is being carried forward as-is pending further validation evidence."
        ),
        "business_case_one_line": (
            f"Estimated annual revenue of EUR {revenue:,.0f} under current assumptions."
        ),
        "key_hypothesis": opportunity.get("key_hypothesis", ""),
        "stop_criteria": opportunity.get("stop_criteria", "Not yet defined."),
        "next_30_days": [
            opportunity.get("first_validation_step", "Define the first validation step."),
            "Review assumptions behind the business case with the commercial team.",
            "Revisit score and stage at the next portfolio review.",
        ],
    }


def generate_summary(opportunity: dict, business_case: dict) -> tuple:
    """Generate a one-page executive summary for an opportunity.

    Returns (result_dict, used_fallback: bool).
    """
    system_prompt = (BASE_DIR / "prompts" / "summary.txt").read_text()
    user_message = json.dumps(
        {"opportunity": opportunity, "business_case": business_case}, default=str
    )
    try:
        result = _call_llm_json(system_prompt, user_message)
        required = {
            "recommendation", "why", "business_case_one_line",
            "key_hypothesis", "stop_criteria", "next_30_days",
        }
        if not required.issubset(result.keys()):
            raise ValueError("Model response missing required fields")
        return result, False
    except Exception:
        return _template_summary(opportunity, business_case), True
