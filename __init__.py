"""Icon Index for Hermes: registration."""

from __future__ import annotations

from pathlib import Path

from . import schemas, tools

TOOLSET = "icon_index"
_TOOLS = (
    (schemas.ICON_SEARCH, tools.icon_search, "🧊"),
    (schemas.ICON_GET, tools.icon_get, "📦"),
    (schemas.ICON_SAVE, tools.icon_save, "💾"),
)


def register(ctx) -> None:
    for schema, handler, emoji in _TOOLS:
        ctx.register_tool(name=schema["name"], toolset=TOOLSET, schema=schema, handler=handler, emoji=emoji)
    ctx.register_command(
        "icons",
        tools.icon_command,
        description="List Icon Index 3D icons, optionally filtered by words",
        args_hint="[words]",
    )
    skills_dir = Path(__file__).parent / "skills"
    for child in sorted(skills_dir.iterdir()):
        if child.is_dir() and (child / "SKILL.md").exists():
            ctx.register_skill(child.name, child / "SKILL.md")
