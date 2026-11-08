"""Tool schemas: what the model reads to decide when to call each tool."""

CATEGORIES = ["Tech", "Money", "Social", "Work"]

ICON_SEARCH = {
    "name": "icon_search",
    "description": (
        "Search Icon Index, a free library of matching 3D icons (rocket, lock, wallet, chart, chat bubble, "
        "trophy and more) in one glossy style, orange by default and available in 8 accent colours. Use it when the user wants 3D icons, "
        "illustrations or hero objects for a website, landing page, app, slide deck or video. "
        "Returns ids and preview images; works offline."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "What the icon should show or mean, e.g. 'security', 'payments', 'launch'. Empty lists all.",
            },
            "category": {"type": "string", "enum": CATEGORIES, "description": "Optional category filter."},
            "limit": {"type": "integer", "minimum": 1, "maximum": 40, "description": "Max results (default 8)."},
        },
        "required": [],
    },
}

ICON_GET = {
    "name": "icon_get",
    "description": (
        "Get one Icon Index icon by id: download links for every format (web GLB, full GLB, transparent "
        "PNG, spinning MP4 loop) in the chosen colour, ready-to-paste embed code (iframe viewer, HTML with "
        "<model-viewer>, React, three.js) and the license. To show the icon to the user in chat, write the returned show_in_chat line as its own paragraph."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Icon id from icon_search, e.g. 'rocket'."},
            "color": {
                "type": "string",
                "description": "Accent colour: orange (default), blue, purple, green, pink, red, teal, yellow, or a hex like #0ea5e9 (hex works for the viewer embed only).",
            },
        },
        "required": ["id"],
    },
}

ICON_SAVE = {
    "name": "icon_save",
    "description": (
        "Download one Icon Index icon's files into a folder in the user's project (for example "
        "'public/icons'), so a site or app can use them offline. Never overwrites existing files. "
        "Use it when the user asks to add an icon to their project."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Icon id, e.g. 'rocket'."},
            "folder": {"type": "string", "description": "Folder to save into; created if missing. Absolute, or relative to the working directory."},
            "formats": {
                "type": "array",
                "items": {"type": "string", "enum": ["glb", "glb_full", "png", "mp4"]},
                "description": "Which files to save (default: glb and png). Non-orange colours have glb and png only.",
            },
            "color": {
                "type": "string",
                "description": "Preset accent colour: orange (default), blue, purple, green, pink, red, teal or yellow.",
            },
        },
        "required": ["id", "folder"],
    },
}
