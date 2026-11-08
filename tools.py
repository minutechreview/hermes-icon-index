"""Tool handlers. Each returns a JSON string and never raises."""

from __future__ import annotations

import difflib
import json
import os
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

from . import catalog

USER_AGENT = "hermes-icon-index/0.1.0"
MAX_BYTES = 40 * 1024 * 1024
MODEL_VIEWER = "https://cdn.jsdelivr.net/npm/@google/model-viewer@4.1.0/dist/model-viewer.min.js"
SAVE_NAMES = {"glb": "{id}.glb", "glb_full": "{id}-full.glb", "png": "{id}.png", "mp4": "{id}-turntable.mp4"}


def _ok(**payload) -> str:
    return json.dumps({"ok": True, **payload}, ensure_ascii=False)


def _err(message: str, **extra) -> str:
    return json.dumps({"ok": False, "error": message, **extra}, ensure_ascii=False)


def _unknown(icon_id: str) -> str:
    ids = [entry["id"] for entry in catalog.load()]
    near = difflib.get_close_matches((icon_id or "").lower(), ids, n=3, cutoff=0.6)
    near += [entry["id"] for entry in catalog.search(icon_id, limit=3) if entry["id"] not in near]
    return _err(f"No icon with id {icon_id!r}.", did_you_mean=near[:4])


def _limit(value, default: int, low: int, high: int) -> int:
    try:
        return max(low, min(high, int(value)))
    except (TypeError, ValueError):
        return default


def icon_search(args: dict, **kwargs) -> str:
    try:
        query = str(args.get("query") or "")
        category = str(args.get("category") or "")
        if category and category.lower() not in {c.lower() for c in catalog.categories()}:
            return _err(f"Unknown category {category!r}.", categories=catalog.categories())
        results = catalog.search(query, category, _limit(args.get("limit"), 8, 1, 40))
        return _ok(
            count=len(results),
            icons=[catalog.summary(entry) for entry in results],
            categories=catalog.categories(),
            hint="Call icon_get for embed code and downloads, or icon_save to put files in the project.",
        )
    except catalog.CatalogError as exc:
        return _err(str(exc))


def embed_code(entry: dict, color: str, hex_value: str) -> dict:
    """Ready-to-paste snippets. Preset colours point at real files; any other hex uses the viewer."""
    alt = f"3D {entry['title'].lower()} icon"
    viewer = catalog.viewer_url(entry, hex_value)
    code = {
        "iframe": (
            f'<iframe src="{viewer}" title="{alt}" width="320" height="320" '
            'style="border:0;background:transparent" loading="lazy"></iframe>'
        ),
    }
    if not color:
        return {**code, "note": "Custom colours exist only in the viewer; pick a preset colour for files."}
    glb, png = catalog.file_url(entry, "glb", color), catalog.file_url(entry, "png", color)
    tag = (
        f'<model-viewer src="{glb}" poster="{png}" alt="{alt}" auto-rotate camera-controls '
        'disable-zoom interaction-prompt="none" shadow-intensity="0" exposure="1.1" '
        'style="width:320px;height:320px;background:transparent"></model-viewer>'
    )
    name = "".join(word.title() for word in entry["id"].split("-"))
    react_tag = tag.replace(
        'style="width:320px;height:320px;background:transparent"', "style={{ width: 320, height: 320 }}"
    )
    script = f'<script type="module" src="{MODEL_VIEWER}"></script>'
    return {
        **code,
        "html": f"{script}\n{tag}",
        "react": f"// once, in index.html: {script}\nexport function {name}Icon() {{\n  return {react_tag}\n}}",
        "threejs": (
            "import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'\n"
            "import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js'\n"
            "const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder)\n"
            f"loader.load('{glb}', gltf => scene.add(gltf.scene))"
        ),
        "img": f'<img src="{png}" alt="{alt}" width="256" height="256">',
    }


def _color(args: dict) -> tuple[str, str] | None:
    return catalog.parse_color(str(args.get("color") or "orange"))


def icon_get(args: dict, **kwargs) -> str:
    try:
        icon_id = str(args.get("id") or "")
        entry = catalog.find(icon_id)
        if entry is None:
            return _unknown(icon_id)
        parsed = _color(args)
        if parsed is None:
            return _err("Colour must be a preset name or a hex like #3b82f6.", presets=list(catalog.COLORS))
        color, hex_value = parsed
        files = catalog.urls(entry, color) if color else {}
        tint = "" if hex_value == catalog.COLORS["orange"] else f' color="{hex_value}"'
        return _ok(
            **catalog.summary(entry),
            tags=entry.get("tags", []),
            color={"name": color or "custom", "hex": f"#{hex_value}"},
            files={kind: {"url": url, "what": catalog.FILES[kind][1]} for kind, url in files.items()},
            viewer_url=catalog.viewer_url(entry, hex_value),
            embed=embed_code(entry, color, hex_value),
            preset_colors=list(catalog.COLORS),
            license=catalog.license_info(),
            show_in_chat=f'::icon-index{{id="{entry["id"]}"{tint}}}',
        )
    except catalog.CatalogError as exc:
        return _err(str(exc))


def _download(url: str, dest: Path) -> int:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310 (fixed https asset host)
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise OSError(f"{url} is larger than expected")
    fd, tmp = tempfile.mkstemp(dir=dest.parent, prefix=".icon-index-")
    with os.fdopen(fd, "wb") as handle:
        handle.write(body)
    try:
        os.link(tmp, dest)  # fails if dest appeared meanwhile, so nothing is ever overwritten
    finally:
        os.unlink(tmp)
    return len(body)


def _save_one(entry: dict, kind: str, folder: Path, color: str) -> dict:
    stem = entry["id"] if color == "orange" else f"{entry['id']}-{color}"
    dest = folder / SAVE_NAMES[kind].format(id=stem)
    if dest.exists():
        return {"format": kind, "path": str(dest), "skipped": "already exists, left unchanged"}
    try:
        size = _download(catalog.file_url(entry, kind, color), dest)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"format": kind, "path": str(dest), "error": str(exc)}
    return {"format": kind, "path": str(dest), "bytes": size}


def icon_save(args: dict, **kwargs) -> str:
    try:
        icon_id = str(args.get("id") or "")
        entry = catalog.find(icon_id)
        if entry is None:
            return _unknown(icon_id)
        raw_folder = str(args.get("folder") or "").strip()
        if not raw_folder or "\x00" in raw_folder:
            return _err("Give a folder to save into, e.g. 'public/icons'.")
        formats = args.get("formats") or ["glb", "png"]
        if not isinstance(formats, list) or any(kind not in catalog.FILES for kind in formats):
            return _err("Unknown format.", formats=list(catalog.FILES))
        parsed = _color(args)
        if parsed is None or not parsed[0]:
            return _err(
                "Saved files come in the preset colours only. For another colour, the user can pick it in "
                "the Icon Index pane and press Download GLB there, or embed the viewer iframe from icon_get.",
                presets=list(catalog.COLORS),
            )
        color = parsed[0]
        if color != "orange" and any(kind not in catalog.COLOR_FILES for kind in formats):
            return _err(f"In {color}, only these formats exist: {', '.join(catalog.COLOR_FILES)}.")
        folder = Path(raw_folder).expanduser()
        folder = (folder if folder.is_absolute() else Path.cwd() / folder).resolve()
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return _err(f"Could not create {folder}: {exc}")
        saved = [_save_one(entry, kind, folder, color) for kind in dict.fromkeys(formats)]
        return _ok(
            id=entry["id"],
            color=color,
            folder=str(folder),
            files=saved,
            license=catalog.license_info(),
            hint="Reference the saved GLB with <model-viewer> (see icon_get embed code) using its local path.",
        )
    except catalog.CatalogError as exc:
        return _err(str(exc))


def icon_command(raw_args: str = "", **kwargs) -> str:
    """/icons [words]: list matching icons in chat."""
    try:
        results = catalog.search(raw_args or "", limit=12)
    except catalog.CatalogError as exc:
        return str(exc)
    if not results:
        return f"No icon matches {raw_args!r}. Try: {', '.join(catalog.categories())}."
    words = raw_args.strip()
    lines = [f"Icon Index: {f'icons for “{words}”' if words else 'all icons'}"]
    for entry in results:
        lines.append(f"• {entry['title']} (`{entry['id']}`, {entry['category']}): {entry['description']}")
    lines.append("Ask me to add one, e.g. “put the 3D rocket in my hero section”.")
    return "\n".join(lines)
