"""Read-only access to the bundled icon list (data/icons.json) and the URLs of each icon's files."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ICONS_FILE = Path(__file__).parent / "data" / "icons.json"
_REQUIRED = ("id", "title", "category", "description")
_WEIGHTS = {"title": 5, "tags": 3, "category": 2, "description": 1}
_WORD = re.compile(r"[a-z0-9]+")
_ID = re.compile(r"^[a-z0-9-]{1,40}$")

# What each downloadable file is, keyed by the name used in tools and URLs.
FILES = {
    "glb": ("model.glb", "Web-ready 3D model (GLB, compressed, ~300 KB) for websites, three.js, model-viewer, React."),
    "glb_full": ("model-full.glb", "Full-quality 3D model (GLB, uncompressed) for Blender, Unity, Unreal, Figma plugins."),
    "png": ("icon.png", "Transparent 1024x1024 PNG render for slides, docs, thumbnails."),
    "mp4": ("turntable.mp4", "4-second seamless spinning loop (512x512 MP4) for videos and reels."),
}


# Ready-made accent colours (files exist for these). The pack's own accent is orange.
COLORS = {
    "orange": "ff6200", "blue": "3b82f6", "purple": "8b5cf6", "green": "22c55e",
    "pink": "ec4899", "red": "ef4444", "teal": "14b8a6", "yellow": "facc15",
}
COLOR_FILES = ("glb", "png")
_HEX = re.compile(r"^#?([0-9a-fA-F]{6})$")


def parse_color(value: str) -> tuple[str, str] | None:
    """Return (preset name or '', hex) for a colour name or hex, or None if unreadable."""
    text = (value or "orange").strip().lower()
    if text in COLORS:
        return text, COLORS[text]
    match = _HEX.match(text)
    if not match:
        return None
    hex_value = match.group(1).lower()
    preset = next((name for name, code in COLORS.items() if code == hex_value), "")
    return preset, hex_value


class CatalogError(RuntimeError):
    """The bundled icon list is missing or malformed."""


def _valid(entry: object) -> bool:
    if not isinstance(entry, dict) or not _ID.match(str(entry.get("id", ""))):
        return False
    if not isinstance(entry.get("tags", []), list):
        return False
    return all(isinstance(entry.get(key), str) and entry[key].strip() for key in _REQUIRED)


@lru_cache(maxsize=1)
def data() -> dict:
    try:
        raw = json.loads(ICONS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise CatalogError(f"Could not read the icon list: {exc}") from exc
    if not isinstance(raw, dict) or not all(str(raw.get(k, "")).startswith("https://") for k in ("asset_base", "viewer_url")):
        raise CatalogError("The icon list needs https asset_base and viewer_url.")
    return raw


@lru_cache(maxsize=1)
def load() -> tuple[dict, ...]:
    entries = tuple(entry for entry in data().get("icons", []) if _valid(entry))
    if not entries:
        raise CatalogError("The icon list has no icons.")
    return entries


def license_info() -> dict:
    return dict(data().get("license", {}))


def categories() -> list[str]:
    seen: list[str] = []
    for entry in load():
        if entry["category"] not in seen:
            seen.append(entry["category"])
    return seen


def find(icon_id: str) -> dict | None:
    wanted = (icon_id or "").strip().lower()
    return next((entry for entry in load() if entry["id"] == wanted), None)


def file_url(entry: dict, kind: str, color: str = "orange") -> str:
    """URL of one file; a non-orange preset colour is available for the GLB and PNG."""
    folder = f"{data()['asset_base']}/icons/{entry['id']}"
    if color != "orange" and kind in COLOR_FILES:
        folder = f"{folder}/colors/{color}"
    return f"{folder}/{FILES[kind][0]}"


def urls(entry: dict, color: str = "orange") -> dict:
    kinds = FILES if color == "orange" else COLOR_FILES
    return {kind: file_url(entry, kind, color) for kind in kinds}


def viewer_url(entry: dict, hex_value: str = "ff6200") -> str:
    tint = "" if hex_value == COLORS["orange"] else f"&color={hex_value}"
    return f"{data()['viewer_url']}#id={entry['id']}{tint}"


def summary(entry: dict) -> dict:
    return {
        "id": entry["id"],
        "title": entry["title"],
        "category": entry["category"],
        "description": entry["description"],
        "png": file_url(entry, "png"),
    }


def _score(entry: dict, words: list[str]) -> int:
    fields = {**entry, "tags": " ".join(entry.get("tags", []))}
    score = 0
    for field, weight in _WEIGHTS.items():
        tokens = set(_WORD.findall(str(fields.get(field, "")).lower()))
        score += weight * sum(1 for word in words if word in tokens or any(t.startswith(word) for t in tokens))
    return score


def search(query: str = "", category: str = "", limit: int = 8) -> list[dict]:
    """Rank icons by keyword overlap with title, tags, category and description."""
    pool = [e for e in load() if not category or e["category"].lower() == category.strip().lower()]
    words = [w for w in _WORD.findall((query or "").lower()) if len(w) > 1]
    if not words:
        return pool[:limit]
    scored = [(_score(e, words), i, e) for i, e in enumerate(pool)]
    scored = [item for item in scored if item[0] > 0]
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [entry for _, _, entry in scored[:limit]]
