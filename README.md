# DaVinci Resolve AI Keywording Agent

Python agent for reading and writing keyword metadata on clips in DaVinci Resolve, with an AI-assisted pipeline planned for later iterations.

## Current Status

- `v0.3` is the current release.
- Browser-based UI (`app.py`) for reading and editing keywords on the selected clip.

## Requirements

- Python 3.10+
- DaVinci Resolve installed and running
- External scripting enabled in Resolve (`Preferences → System → General`)
- Flask:

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Then open `http://localhost:5000` in your browser.

## What It Does

- Connects to an open DaVinci Resolve instance through the official scripting API.
- Finds the selected clip from the current timeline video item, falling back to the Media Pool selection.
- Displays the clip name and its keywords in the browser.
- **Refresh** fetches live data from Resolve without reloading the page.
- Each keyword tag has a × button; clicking it opens an inline confirmation modal.
- **Remove** deletes the keyword from the list; a **Save** button then appears.
- **Save** writes the updated keyword list back to Resolve, with a brief "Saved" confirmation on success.

## API

`GET /api/clip` — returns the selected clip name and keywords:

```json
{"clip": "A001_C003_0215AB", "keywords": ["interview", "city", "night"]}
```

`POST /api/clip/keywords` — writes an updated keyword list to the selected clip:

```json
{"keywords": ["interview", "city"]}
```

## Tests

```bash
python3 -m unittest test_resolve_api -v
```

## Target Final Version (v1 Vision)

The intended end-state is an AI-assisted keywording workflow that:

- Pulls clip context from Resolve and project metadata.
- Generates suggested keywords using an LLM pipeline.
- Applies decision logic and confidence thresholds before write-back.
- Writes metadata safely with traceable logs and configurable behavior.
- Supports both single-clip and batch processing modes.
- Uses a clear configuration model for providers, prompts, and policies.

## Changelog

Project history and planned milestones are tracked in [`CHANGELOG.md`](CHANGELOG.md).
