"""Load entries from the entries/ folder."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_entries(include_private=None):
    if include_private is None:
        include_private = os.getenv("BML_PRIVATE") == "1"
    folders = [ROOT / "entries"] + ([ROOT / "private_entries"] if include_private else [])
    entries = []
    for folder in folders:
        for path in sorted(folder.glob("*.json")):
            entries.append(json.loads(path.read_text(encoding="utf-8")))
    return entries
