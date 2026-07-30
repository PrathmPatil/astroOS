"""Load classical knowledge packs and YAML rules from repo root."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


def _resolve_root() -> Path:
    """Repo root containing ``knowledge/`` and ``rules/`` (local or Fly/Docker)."""
    if env := os.environ.get("ASTROOS_ROOT"):
        return Path(env)
    here = Path(__file__).resolve()
    candidates = [
        here.parents[3],
        here.parents[2],
        Path("/app"),
    ]
    for candidate in candidates:
        if (candidate / "rules").is_dir() and (candidate / "knowledge").is_dir():
            return candidate
    return here.parents[3]


ROOT = _resolve_root()
KNOWLEDGE = ROOT / "knowledge"
RULES = ROOT / "rules"


@lru_cache
def load_all_slokas() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not KNOWLEDGE.exists():
        return out
    for path in KNOWLEDGE.glob("*/index.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        for sloka in data.get("slokas", []):
            out[sloka["id"]] = {
                **sloka,
                "text_id": data.get("id"),
                "text_title": data.get("title"),
                "text_short": data.get("short"),
            }
    return out


@lru_cache
def load_all_rules() -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []
    if not RULES.exists():
        return rules
    for path in RULES.glob("**/*.yaml"):
        chunk = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        if isinstance(chunk, list):
            for rule in chunk:
                rule["_file"] = str(path.relative_to(ROOT))
                rules.append(rule)
    return rules


def get_sloka(sloka_id: str | None) -> dict[str, Any] | None:
    if not sloka_id:
        return None
    return load_all_slokas().get(sloka_id)


def rules_by_category(category: str | None = None) -> list[dict[str, Any]]:
    rules = load_all_rules()
    if not category:
        return rules
    return [r for r in rules if r.get("category") == category]
