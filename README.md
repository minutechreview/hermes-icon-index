# Icon Index for Hermes

40 free 3D icons in one matching style. Browse them spinning inside Hermes, recolour them, and let your agent drop them into a website, app, slide or video.

[Icon Index](https://motion.minutechbuilds.com/icons/) is a free library of 3D icons: rocket, robot, padlock, wallet, chart, chat bubble, trophy and more. The 3D models were made with Meshy from original concept art. They are CC0, so you can use them for anything, including commercial work, with no credit needed. This plugin brings the library into Hermes.

## What you get

**In Hermes Desktop: an Icon Index pane**
- Every icon spins in a live preview. Search them, or filter by category: Tech, Money, Social or Work.
- Open an icon to spin it yourself, and try any accent colour: 8 presets, or any colour from the picker.
- **Download GLB** saves the icon in the colour you picked.
- **Ask the agent to add this** puts a request in your chat. **Copy embed code** copies an iframe you can paste into any site.

**In chat: a 3D card**
- The agent can show an icon inline, as a card you can drag to spin, by writing `::icon-index{id="rocket" color="3b82f6"}`.

**For the agent: three tools**

| Tool | What it does |
|---|---|
| `icon_search` | Finds icons by meaning ("security", "payments", "launch"). Works offline. |
| `icon_get` | Returns one icon's download links, embed code (iframe, `<model-viewer>`, React, three.js, `<img>`) and license, in any of the 8 preset colours. A custom hex gives the iframe embed. |
| `icon_save` | Downloads an icon's files into a folder in your project, e.g. `public/icons`. It never overwrites a file. |

**In chat**
- `/icons [words]` lists matching icons.
- The bundled skill `icon-index:add-3d-icon` walks the agent from finding an icon to adding it to your project.

## Formats

| File | Use it for |
|---|---|
| `model.glb` | Websites, three.js and `<model-viewer>`. Compressed (meshopt + WebP), about 300 KB. |
| `model-full.glb` | Blender, Unity and Unreal. Uncompressed. |
| `icon.png` | Slides, docs and thumbnails. Transparent, 1024 px. |
| `turntable.mp4` | Videos and reels. A 4-second seamless spin, 512 px. |

Each of the 8 accent colours also has its own `model.glb` and `icon.png`.

## Install

```bash
hermes plugins install minutechreview/hermes-icon-index
hermes plugins enable icon-index
```

In Hermes Desktop, turn on **Icon Index** under **Capabilities → Plugins**. The pane opens on the right.

Then try:

> Add a 3D rocket in blue to the hero section of my landing page.

## What it touches (disclosure)

- **Network:**
  - The pane and the chat card load preview images, loops and models from `cdn.jsdelivr.net` (the public [3d-icons](https://github.com/minutechreview/3d-icons) repository, at a pinned commit).
  - The 3D viewer page loads from `motion.minutechbuilds.com/icons/viewer.html`. It runs inside a sandboxed frame with an opaque origin, and it loads three.js from `cdn.jsdelivr.net`.
  - `icon_save` downloads files from the same pinned CDN path.
  - Search, metadata and embed code come from `data/icons.json`, bundled with the plugin.
- **Files:** `icon_save` writes only into the folder you or the agent name, and never overwrites an existing file. Nothing else is read or written outside the plugin folder.
- **Background work:** none. No shell commands, credentials, telemetry or self-updating.

## License

The plugin code is MIT. The icons are [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). Made by [@minutechbuilds](https://instagram.com/minutechbuilds), also the maker of [Motion Index](https://motion.minutechbuilds.com).
