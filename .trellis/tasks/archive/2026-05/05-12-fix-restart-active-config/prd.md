# Fix restart active config behavior

## Goal

`sing restart` must restart the Windows service with the currently active profile and must not accept a profile name argument.

## What I already know

- User requirement: `sing restart` does not need parameters.
- User requirement: restart should use the current active configuration.
- Current implementation defines `restart(name: str)` and reconfigures the service with the provided profile.
- `README.md` and backend SPEC currently document `sing restart <name>`.
- Current tests cover service and state helpers but do not cover the Typer command-level restart argument contract.

## Requirements

- Change the CLI command contract from `sing restart <name>` to `sing restart`.
- `sing restart` must load the current state and require `state.active` to be set.
- `sing restart` must require the active profile to still exist.
- `sing restart` must require an installed `sing-box.exe` path.
- `sing restart` must stop the service, configure NSSM with the active profile path, start the service, and keep `state.active` unchanged.
- `sing start <name>` service-running error must point users to `sing restart`.
- Update tests for the no-argument restart behavior.
- Update README and SPEC command descriptions to match the corrected contract.

## Acceptance Criteria

- [x] `sing restart` succeeds with the current active profile.
- [x] `sing restart <name>` is rejected by Typer as an unexpected argument.
- [x] `sing restart` fails clearly when no active profile is recorded.
- [x] `sing restart` fails clearly when the active profile is missing.
- [x] Python lint, type-check, and tests pass.

## Definition of Done

- Tests added or updated for the command behavior.
- `uv run ruff check src` passes.
- `uv run ty check src` passes.
- `uv run pytest` passes.
- Docs and SPEC reflect the finished behavior without extra notes or process commentary.

## Out of Scope

- Backward compatibility for `sing restart <name>`.
- Selecting or switching profiles during restart.
- Changing `sing start`, `sing stop`, `sing update`, `sing remove`, or profile storage beyond the required help/error text updates.

## Technical Notes

- Relevant files inspected:
  - `src/sing_cli/cli.py`
  - `tests/test_service.py`
  - `tests/test_state.py`
  - `README.md`
  - `.trellis/spec/backend/index.md`
  - `.trellis/spec/backend/error-handling.md`
  - `.trellis/spec/backend/quality-guidelines.md`
  - `.trellis/spec/backend/logging-guidelines.md`
