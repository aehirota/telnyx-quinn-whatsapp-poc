# Diagrams

Excalidraw scene files for the architecture and LangChain internals of this POC.

## Contents

| File | What it shows |
|------|---------------|
| [`presentation-canvas.excalidraw`](presentation-canvas.excalidraw) | **All three diagrams stacked on one canvas** — built for live screen-share. Open this one during the demo and pan/zoom between sections instead of switching files. |
| [`architecture-overview.mmd`](architecture-overview.mmd) | **Mermaid source** of the architecture overview — embedded inline in the main [`../README.md`](../README.md) so GitHub renders it without a click |
| [`architecture-overview.excalidraw`](architecture-overview.excalidraw) | **Excalidraw version** of the same architecture overview — standalone, useful if you want just the overview in another context |
| [`qualification-engine-internals.excalidraw`](qualification-engine-internals.excalidraw) | Standalone: inside `tools/qualification_engine.py` — the LCEL chain, the `ChatAnthropic` config, and the full `Qualification` Pydantic schema |
| [`response-generator-internals.excalidraw`](response-generator-internals.excalidraw) | Standalone: inside `tools/response_generator.py` — the simpler `prompt | llm` chain, plus a real example reply |

**Why three Excalidraw layouts?**
- `presentation-canvas.excalidraw` — the live-demo file, all three sections stacked vertically with arrow callouts (`↓ Zoom into qualification_engine ↓`). Open this once, pan as you talk.
- The three standalone files — useful if you want to embed just one section as a single image in a slide, README, LinkedIn post, etc.

**Why architecture overview also has a Mermaid version?**
- **Mermaid** renders inline on GitHub READMEs — lowest friction for a casual reader scanning the repo
- **Excalidraw** has visual personality and supports rich annotations — better for slide decks and embedded screenshots

The two internals diagrams are Excalidraw-only because they include Pydantic schema boxes and quoted example replies — content that doesn't fit cleanly in a Mermaid node label.

## How to view or edit

**Easiest:** drag any `.excalidraw` file onto [excalidraw.com](https://excalidraw.com) — it opens in the editor, fully editable.

**Alternative:** open the file in any tool that speaks Excalidraw scene JSON (the official `excalidraw` desktop app, the `excalidraw` VS Code extension, etc.).

## Live shareable URLs (point-in-time snapshots)

These were uploaded once and render that snapshot. They do **not** auto-update when the local `.excalidraw` files change. The local files in this folder are always the source of truth.

- ⚠️ Architecture overview: ~~`https://excalidraw.com/#json=zip1EnsMy76ihfJgo78-c,V3dm1qy-TSNi2CLA1aAT_w`~~ **(stale — predates the Streamlit UI being added as a parallel trigger; drag-drop `architecture-overview.excalidraw` for the current version)**
- `qualification_engine` internals: https://excalidraw.com/#json=hjTOG3vUO_1vvLYGhPcv-,KXkVtamPcJFTVtoGeRfUMg
- `response_generator` internals: https://excalidraw.com/#json=A5-8c8ZkI738X-blQVPpX,vWG2kd-fEeDeSbNCTaOUIw

To get a fresh shareable URL: open excalidraw.com, drag-drop the `.excalidraw` file, then use the "Share" button (top right) → "Shareable link" to generate a new one.
