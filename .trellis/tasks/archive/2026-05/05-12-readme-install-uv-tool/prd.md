# docs: update README installation instructions

## Goal

Update `README.md` so users can install, update, and uninstall `sing-cli` with `uv tool`, and install runtime executables with Scoop.

## What I already know

* The user requested README documentation for:
  * `uv tool install sing-cli`
  * `uv tool upgrade sing-cli`
  * `uv tool uninstall sing-cli`
  * `scoop install sing-box nssm`
* `README.md` currently documents runtime requirements and command usage, but not CLI installation.
* The project exposes the CLI command through `pyproject.toml` as `sing = "sing_cli.main:main"`.

## Assumptions

* The README should keep the existing concise structure.
* Scoop is documented as the recommended way to install `sing-box.exe` and `nssm.exe` on Windows.

## Requirements

* Add a README section for installing, updating, and uninstalling `sing-cli` with `uv tool`.
* Add a README example showing `scoop install sing-box nssm` for runtime dependencies.
* Preserve existing command behavior documentation.
* Keep published docs free of editor notes, migration commentary, and one-off explanatory footnotes.

## Acceptance Criteria

* [x] `README.md` includes `uv tool install sing-cli`.
* [x] `README.md` includes `uv tool upgrade sing-cli`.
* [x] `README.md` includes `uv tool uninstall sing-cli`.
* [x] `README.md` includes `scoop install sing-box nssm`.
* [x] The README remains visually consistent with the existing concise style.

## Definition of Done

* Documentation updated.
* Diff reviewed for scope.
* No code tests are required because this is a README-only change.

## Out of Scope

* Changing CLI behavior.
* Adding package publishing automation.
* Adding installation logic to the CLI.

## Technical Notes

* Relevant files inspected:
  * `README.md`
  * `.trellis/spec/backend/index.md`
  * `uv tool --help`
  * `.trellis/tasks/05-12-readme-install-uv-tool/research/uv-tool-commands.md`
