# Diagrams

Excalidraw scene files for the architecture and LangChain internals of this POC.

## Contents

| File | What it shows |
|------|---------------|
| [`architecture-overview.excalidraw`](architecture-overview.excalidraw) | End-to-end flow: `mock_data → main.py → Flask /webhook → 4 tools → salesforce_mock.json` |
| [`qualification-engine-internals.excalidraw`](qualification-engine-internals.excalidraw) | Inside `tools/qualification_engine.py` — the LCEL chain, the `ChatAnthropic` config, and the full `Qualification` Pydantic schema |
| [`response-generator-internals.excalidraw`](response-generator-internals.excalidraw) | Inside `tools/response_generator.py` — the simpler `prompt | llm` chain, plus a real example reply |

## How to view or edit

**Easiest:** drag any `.excalidraw` file onto [excalidraw.com](https://excalidraw.com) — it opens in the editor, fully editable.

**Alternative:** open the file in any tool that speaks Excalidraw scene JSON (the official `excalidraw` desktop app, the `excalidraw` VS Code extension, etc.).

## Live shareable URLs (snapshot at time of export)

These render the same diagrams without needing to download anything. Useful for embedding in slides/decks.

- Architecture overview: https://excalidraw.com/#json=zip1EnsMy76ihfJgo78-c,V3dm1qy-TSNi2CLA1aAT_w
- `qualification_engine` internals: https://excalidraw.com/#json=hjTOG3vUO_1vvLYGhPcv-,KXkVtamPcJFTVtoGeRfUMg
- `response_generator` internals: https://excalidraw.com/#json=A5-8c8ZkI738X-blQVPpX,vWG2kd-fEeDeSbNCTaOUIw

If a URL ever stops working (excalidraw.com URL format changes, etc.), regenerate by uploading the matching `.excalidraw` file to the editor.
