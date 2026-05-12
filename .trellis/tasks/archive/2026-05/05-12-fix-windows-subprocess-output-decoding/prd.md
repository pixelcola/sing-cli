# Fix Windows Subprocess Output Decoding

## Goal

Fix `sing start <name>` and `sing stop` on Windows so NSSM subprocess output does not crash background reader threads when the system locale is GBK and the child process emits bytes that are not valid GBK.

## Requirements

- Decode NSSM subprocess stdout and stderr with a deterministic encoding instead of the Windows locale default.
- Keep NSSM failures explicit: non-zero exit codes must still raise `ExternalCommandError` with stderr or stdout content.
- Do not introduce shell command strings, retries, mock success paths, or silent command degradation.
- Cover the default runner behavior with tests.

## Acceptance Criteria

- [ ] `default_runner()` calls `subprocess.run()` with explicit `encoding`.
- [ ] `default_runner()` handles undecodable bytes without raising `UnicodeDecodeError` from subprocess reader threads.
- [ ] Existing NSSM command construction and error propagation tests still pass.
- [ ] Ruff, ty, and pytest pass for the changed code.

## Definition of Done

- Tests added or updated for the decoding behavior.
- Lint, type check, and tests are green.
- No documentation changes are needed unless command behavior changes.

## Technical Approach

Use explicit UTF-8 decoding for captured subprocess output and configure decode errors to replace invalid byte sequences. NSSM output is only used for status checks and human-readable error summaries, so replacement exposes problematic bytes without crashing the CLI.

## Decision (ADR-lite)

Context: `subprocess.run(..., text=True)` uses the platform default encoding when no `encoding` is provided. On Windows with a GBK locale, NSSM or service output can include bytes that are not valid GBK, causing `UnicodeDecodeError` in subprocess reader threads.

Decision: Set `encoding="utf-8"` and `errors="replace"` in the shared `default_runner()`.

Consequences: Captured output remains text for existing service logic, invalid byte sequences are visible as replacement characters, and command failures continue to surface through the existing error path.

## Out of Scope

- Changing NSSM command arguments or service semantics.
- Adding retries or service state recovery.
- Adding a logging framework.

## Technical Notes

- Relevant files: `src/sing_cli/service.py`, `tests/test_service.py`.
- Relevant specs: `.trellis/spec/backend/error-handling.md`, `.trellis/spec/backend/quality-guidelines.md`, `.trellis/spec/backend/logging-guidelines.md`.
