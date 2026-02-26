# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

## [0.4.0] - 2026-02-26

### Added

- Clip thumbnail displayed in the web UI above the clip name, served as
  PNG from `GET /api/clip/thumbnail`. Refreshes alongside clip data.
  Uses the proxy file (`Proxy Media Path`) when available, otherwise
  falls back to the original (`File Path`). A mid-point frame is
  extracted via `ffmpeg`. Shows "No thumbnail available" placeholder
  when no file path is available or ffmpeg fails.
- `thumbnail_from_file_path()` added to `resolve_api.py`; uses ffmpeg
  to extract a frame with no Resolve IPC involved.
- `GET /api/clip/thumbnail` fetched via `fetch()` in JS rather than a
  direct `<img src>`, so a `204 No Content` response reliably shows the
  placeholder instead of leaving the image in a broken loading state.

### Fixed

- Resolve scripting API is not thread-safe: all IPC calls are now
  serialised through a single `threading.Lock` in `app.py`, with one
  cached `resolve` object reused across requests.
- `_get_resolve()` was acquiring the lock inside itself while all
  callers already held it — a re-entrant deadlock that hung every
  request. Fixed by making `_get_resolve()` lock-free and requiring
  callers to hold the lock.
- Flask runs with `threaded=True` so the thumbnail route (which runs
  ffmpeg outside the lock) cannot block `/api/clip`.

## [0.3.3] - 2026-02-26

### Removed

- `main.py` — CLI entry point deleted; the web UI (`app.py`) is the only entry point.
- `format_output()` and `_error()` removed from `resolve_api.py` (CLI-only helpers with no remaining callers).
- `test_main.py` replaced by `test_resolve_api.py`; CLI test class (`TestMain`) and `TestFormatOutput` removed.

## [0.3.2] - 2026-02-26

### Changed

- Extracted Resolve scripting API functions into `resolve_api.py`; `main.py` is now CLI-only.
- `app.py` now imports from `resolve_api` directly.

## [0.3.1] - 2026-02-26

### Fixed

- × button on keyword tags did not fire — inline `onclick` with `JSON.stringify` produced unescaped quotes in the HTML attribute, which the browser silently rejected. Replaced `innerHTML` string-building with DOM element construction and `addEventListener`.

## [0.3.0] - 2026-02-26

### Added

- `POST /api/clip/keywords` — writes an updated keyword list back to the selected clip in Resolve.
- Keyword tags in the UI now show a × button; clicking it opens an inline confirmation modal.
- Inline confirmation modal shows the keyword name with Cancel / Remove actions.
- Save button (hidden until a keyword is removed) posts the current keyword list to Resolve and shows a brief "Saved" confirmation.
- `renderKeywords()` extracted so both `refresh()` and the modal confirm path redraw just the keyword list.

## [0.2.1] - 2026-02-26

### Fixed

- "Current Status" section now correctly reflects v0.2 as the current release.
- No-clip-selected error example corrected to match actual stderr output (`ERROR: ...`).
- v0.2 requirements section is now self-contained instead of referencing v0.

## [0.2.0] - 2026-02-26

### Added

- `app.py` — Flask web server with two routes:
  - `GET /` — serves the browser UI.
  - `GET /api/clip` — returns the selected clip name and keywords as JSON.
- `templates/index.html` — minimal browser UI with a Refresh button, loading state, keyword tag list, and error display; no external dependencies.
- `requirements.txt` — pins `flask>=3.0`.

## [0.1.0] - 2026-02-26

### Added

- CLI argument support via `argparse`:
  - `--set "k1,k2"` — replace all keywords on the selected clip.
  - `--replace` — alias for `--set`.
  - `--append "k1"` — add keywords to existing ones.
  - `--dry-run` — preview the result without writing to Resolve.
  - `--json` — machine-readable JSON output for all modes.
- `set_keywords()` — writes keyword metadata back to Resolve via `SetMetadata`.
- `merge_keywords()` — deterministic merge with append/set/replace modes.
- `_dedupe_preserve_order()` — case-insensitive deduplication, first occurrence wins.
- `format_output()` — unified human-readable and JSON output formatting.
- `test_main.py` — 39 unit tests covering all functions and CLI paths using mocked Resolve objects.

### Changed

- `main()` rewritten to wire CLI args, merge logic, write-back, and error handling.
- Error messages now go to stderr and respect `--json` format.
- `README.md` updated with CLI usage examples and keyword policy documentation.

## [0.0.1] - 2026-02-26

### Added

- `main.py` v0 implementation that:
  - connects to DaVinci Resolve,
  - resolves selected clip from timeline or Media Pool,
  - reads keywords metadata,
  - prints clip name and keywords in terminal.
- Initial project `README.md` with usage and scope.
