# Optimize Python code

## Goal

Review the project Python code and apply focused readability and maintainability improvements using `friendly-python` and `piglet` guidance, while preserving existing CLI behavior.

## What I already know

- The project is a Typer-based Python CLI under `src/sing_cli/`.
- The current branch is `main` and the working tree was clean before this task.
- Current backend specs require explicit CLI errors, predictable stdout/stderr, and tests for CLI behavior changes.
- `friendly-python` emphasizes clear boundaries, maintainability, and review against naming, error handling, API shape, and change isolation.
- `piglet` emphasizes single-responsibility functions, stable return types, narrow exception handling, clear naming, and explicit behavior.

## Observed Optimization Candidates

- `src/sing_cli/cli.py` repeats `try/except SingCliError` around most command handlers.
- `src/sing_cli/cli.py` owns timestamp parsing/formatting for list output, which may be a reusable formatting concern rather than command flow.
- Command functions mix command orchestration, state mutation, and user output; small extraction may improve readability without changing behavior.
- Existing service/profile/state modules are already small and should not be broadly rewritten without a concrete payoff.
- The user selected full project code review scope across `src/sing_cli/`.

## Requirements

- Preserve all existing command names, outputs, errors, state format, and tests unless a specific behavior change is explicitly approved.
- Review `src/sing_cli/cli.py`, `src/sing_cli/state.py`, `src/sing_cli/service.py`, and `src/sing_cli/profile.py`.
- Prefer focused readability improvements over broad architecture churn.
- Keep exception scopes narrow and preserve error context.
- Keep public command entry points obvious.
- Add or update tests only when behavior is intentionally touched or a refactor needs regression coverage.

## Acceptance Criteria

- [x] The chosen optimization scope is explicit.
- [x] Code changes are localized and improve readability or change isolation.
- [x] Ruff, ty, and pytest pass.
- [x] No backward-incompatible CLI behavior changes are introduced.

## Out of Scope

- Performance tuning without measured bottlenecks.
- Replacing Typer or changing the command set.
- Adding new features.
- Large rewrites across all modules.

## Technical Notes

- Relevant specs: `.trellis/spec/backend/index.md`, `.trellis/spec/backend/quality-guidelines.md`, `.trellis/spec/backend/error-handling.md`, `.trellis/spec/backend/logging-guidelines.md`.
- Likely files: `src/sing_cli/cli.py`, possibly small helpers in `src/sing_cli/state.py` or a narrow new module if justified.
