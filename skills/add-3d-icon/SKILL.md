---
name: add-3d-icon
description: Add a free 3D icon from Icon Index to a website, app, slide or video, in the colour the user wants.
---

# Add a 3D icon from Icon Index

1. **Find it.** Call `icon_search` with what the icon should mean ("security", "payments", "launch"). Pick the closest one. If two fit, show both.
2. **Show it.** Call `icon_get` with the id and the colour the user asked for (default orange). Then write its `show_in_chat` line as its own paragraph, e.g. `::icon-index{id="rocket" color="3b82f6"}`. In Hermes Desktop it becomes a spinning 3D card the user can drag.
3. **Pick a colour.** The 8 presets are orange, blue, purple, green, pink, red, teal and yellow. They have real files. Match the brand's main colour to the nearest preset. Any other hex works only through the viewer iframe. To get files in that colour, the user opens the icon in the Icon Index pane, picks the colour and presses **Download GLB**.
4. **Add it to the project.**
   - **Website, from files (best):** call `icon_save` with a folder the site serves, e.g. `public/icons`. Then use the `<model-viewer>` snippet from `icon_get` with the local path. Add the model-viewer script once per page.
   - **Quick embed, or a site builder (Framer, Webflow, Notion):** use the `iframe` snippet.
   - **Slides, docs or thumbnails:** save the `png`.
   - **Videos and reels:** save the `mp4` (orange) or the PNG in the chosen colour.
   - **three.js or React Three Fiber:** use the `threejs` snippet. The web GLB is meshopt-compressed, so it needs `MeshoptDecoder`.
   - **Blender, Unity or Unreal:** save `glb_full`.
5. **Keep it light.** The web GLB is about 300 KB. On a landing page, use 1–3 spinning icons and plain PNGs for the rest.
6. **License.** Tell the user what `license` in the `icon_get` result says. Don't claim anything beyond it.
