# Windows CLI for sing-box Control

## Goal

Build a Windows CLI application that installs, uninstalls, starts, stops, restarts, and configures the `sing-box` Windows service, while managing named `sing-box` JSON profiles.

## What I Already Know

* The user wants a Windows CLI application for controlling `sing-box`.
* The repository is a Python project requiring Python `>=3.13`.
* The build backend is `hatchling.build`.
* Versioning is generated from Git metadata via `uv-dynamic-versioning`.
* The current package lives under `src/sing_cli/`.
* The console script should be `sing = "sing_cli.main:main"`.
* The backend spec defines the intended implementation as a Windows Python CLI.
* The backend spec states the CLI framework should be `typer`, HTTP downloads should use `httpx`, and service management should call `sc.exe` without `pywin32`.
* The fixed Windows service name is `sing-box`.
* Local application state should use `typer.get_app_dir("sing-cli")`.

## Assumptions

* The first release targets Windows only.
* The CLI controls an already available `sing-box.exe`; it does not download or upgrade the binary.
* Profile URLs return complete `sing-box` JSON profile files.

## Open Questions

* None.

## Requirements

* Provide a command to install the `sing-box` Windows service.
* Provide a command to uninstall the `sing-box` Windows service.
* Provide commands to start, stop, and restart the service.
* Provide commands to add, remove, update, and list named profiles.
* Store profile source metadata and downloaded JSON profiles in local app data.
* Use `sc.exe` through argument lists, not shell string concatenation.
* Use the fixed Windows service name `sing-box`.
* Expose the public console command as `sing`.
* `add <name> <url>` must fail without saving metadata when the profile download fails.
* `update <name>` must preserve the previous local profile when the profile download fails.
* Keep the implementation and tests readable under `friendly-python` and `piglet` guidance: clear names, stable return types, localized error handling, shallow branching, and focused test helpers.

## Acceptance Criteria

* [ ] `install` registers the `sing-box` service and enables autostart.
* [ ] `install --bin <path>` registers a custom `sing-box.exe` path.
* [ ] `start <name>` updates the service `binPath` to run the selected profile and starts the service.
* [ ] `start <name>` fails when the service is already running and tells the user to use `restart <name>`.
* [ ] `restart <name>` stops the service, updates the service command line, and starts it again.
* [ ] `stop` stops the service without requiring a profile name.
* [ ] `add <name> <url>` stores the profile source and downloads the JSON profile.
* [ ] `add <name> <url>` leaves no saved source behind when download fails.
* [ ] `update <name>` redownloads the profile from the saved URL.
* [ ] `update <name>` preserves the previous local profile when download fails.
* [ ] `remove <name>` deletes the source metadata and local profile file.
* [ ] `list` shows all saved profiles and marks the active profile.
* [ ] Ruff and ty checks pass.
* [ ] Refactored implementation and tests preserve existing CLI behavior while improving readability and boundaries.
* [ ] The installed console command is `sing`.

## Definition of Done

* Tests added or updated where command behavior can be exercised without real Windows service mutation.
* Lint and type checks pass.
* Documentation updated if user-facing command behavior changes.
* Windows-only service operations fail clearly on non-Windows platforms.

## Out of Scope

* Downloading or upgrading `sing-box.exe`.
* Managing more than one Windows service instance.
* Subscription conversion or transformation.
* GUI or tray integration.
* Backward compatibility with previous command formats.

## Technical Notes

* Relevant files inspected: `pyproject.toml`, `src/sing_cli/__init__.py`, `README.md`, `.trellis/spec/backend/index.md`, `.trellis/spec/guides/index.md`.
* Current `README.md` is empty.
* The backend spec's command contract documents commands under `sing ...`, while `pyproject.toml` currently exposes `sing-cli`; this task should align the package entry point with the spec.
* `sing start <name>` and `sing restart <name>` must set:

```text
sc.exe config sing-box binPath= "<sing-box.exe> run -c <profile-path>"
```

* Windows autostart should reuse the last profile written by `start` or `restart`.
