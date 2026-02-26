# DaVinci Resolve AI Keywording Agent

## v0

This v0 connects to DaVinci Resolve, reads the currently selected clip, retrieves its keywords metadata, and prints the result in the terminal.

## What It Does

- Connects to an open DaVinci Resolve instance through the official scripting API.
- Finds the selected clip from the current timeline video item first.
- Falls back to the Media Pool selection if needed.
- Reads keyword metadata from the clip.
- Prints the clip name.
- Prints the keyword list, or `(none)` if empty.

## Requirements

- Python 3.10+
- DaVinci Resolve installed
- DaVinci Resolve running
- External scripting enabled in Resolve

## Run

From this project folder:

```bash
python3 main.py
```

## Example Output

```text
Clip: A001_C003_0215AB
Keywords:
- interview
- city
- night
```

If no keywords are set:

```text
Clip: A001_C003_0215AB
Keywords: (none)
```

If no clip is selected:

```text
No selected clip found.
Select a clip in the timeline (or media pool) and run again.
```

## Current Scope

This is intentionally minimal v0 behavior:

- Read-only
- Single selected clip
- Terminal output only

No AI tagging, keyword generation, or write-back to Resolve is implemented yet.
