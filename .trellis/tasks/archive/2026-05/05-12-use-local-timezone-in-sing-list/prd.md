# Use local timezone in sing list

## Goal

`sing list` prints each profile update time in the computer's local timezone, while preserving the existing UTC storage format in `state.json`.

## What I already know

- `src/sing_cli/state.py` stores `updated_at` with `now_utc()` as an ISO UTC string ending in `Z`.
- `src/sing_cli/cli.py` prints `entry.updated_at` directly in `list_profiles()`.
- Existing list output tests live in `tests/test_cli.py`.
- The task branch is `fix/list-local-timezone`.

## Requirements

- Keep `add` and `update` writing UTC timestamps to state.
- Convert stored profile timestamps to the computer's local timezone when `sing list` prints them.
- Preserve the existing list columns and active-profile marker.
- Surface invalid stored timestamps as explicit CLI errors.

## Acceptance Criteria

- [x] `sing list` converts a UTC `Z` timestamp to the local timezone before printing.
- [x] Existing state persistence tests still pass without format migration.
- [x] CLI tests cover local-timezone rendering.
- [x] Ruff, ty, and pytest pass for the affected project.

## Out of Scope

- Changing the state file timestamp format.
- Adding user-configurable timezone flags.
- Changing the command table layout.

## Technical Notes

- Relevant specs: `.trellis/spec/backend/index.md`, `.trellis/spec/backend/quality-guidelines.md`, `.trellis/spec/backend/logging-guidelines.md`.
- Relevant files: `src/sing_cli/cli.py`, `src/sing_cli/state.py`, `tests/test_cli.py`.
