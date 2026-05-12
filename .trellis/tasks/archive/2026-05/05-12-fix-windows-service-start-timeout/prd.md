# Fix Windows Service Start Timeout

## Goal

Fix `sing start <name>` failing with Windows `StartService` error 1053 by using NSSM as the Windows service host while preserving the intended command model: `sing install` installs the Windows service and enables autostart, and `sing start <name>` starts `sing-box` with the selected configuration.

## What I Already Know

* User observed `sing start config.json` failing with `sc.exe failed: [SC] StartService failed 1053`.
* Current service registration and reconfiguration live in `src/sing_cli/service.py`.
* `install_service()` registers `sing-box` with `binPath= "<sing-box.exe> run"`.
* `configure_service()` rewrites the service to `binPath= "<sing-box.exe> run -c "<profile-path>""`.
* `sing-box run` is a normal foreground command and does not implement the Windows service control dispatcher expected by the Windows Service Control Manager.
* `sc.exe` operations are tested in `tests/test_service.py`.
* `sing install` is intended to install the Windows service and set it to autostart.
* `sing start <name>` is intended to use a saved configuration to start `sing-box`.
* NSSM supports command-line service installation with `nssm install <servicename> <program> [<arguments>]`.
* NSSM service parameters can be updated with `nssm set <servicename> <parameter> <value>`, including `Application`, `AppDirectory`, `AppParameters`, and `Start`.
* NSSM supports `nssm start <servicename>`, `nssm stop <servicename>`, and `nssm remove <servicename> confirm`.

## Assumptions

* The CLI should keep the existing command surface: `sing install`, `sing start <name>`, `sing stop`, and `sing restart <name>`.
* The fix should preserve the fixed Windows service name `sing-box`.
* The service should run the installed `sing-box.exe` with the selected profile path.
* Autostart should use the last configuration applied by `sing start <name>` or `sing restart <name>`.
* No backward compatibility with the old direct `sc.exe binPath` format is required.
* `nssm.exe` is available on `PATH` when Windows service commands are used.

## Requirements

* Register the `sing-box` Windows service through NSSM.
* Keep `sing install` focused on service installation and autostart setup.
* Make `sing start <name>` configure the selected profile and start the Windows service without triggering SCM error 1053.
* Make `sing restart <name>` stop, reconfigure, and start through the same service host.
* Ensure NSSM starts the configured `sing-box.exe run -c <profile>` command.
* Keep external command failures visible as explicit CLI errors.
* Add or update tests for the service command construction and configuration behavior.

## Acceptance Criteria

* [ ] `sing install --bin <path>` calls NSSM to install the `sing-box` service.
* [ ] `sing install --bin <path>` sets NSSM `Start` to `SERVICE_AUTO_START`.
* [ ] `sing start <name>` sets NSSM `Application` and `AppParameters` so NSSM runs `<bin> run -c <profile>`.
* [ ] `sing start <name>` starts the service through NSSM.
* [ ] Unit tests cover the updated install/configure/start command behavior.
* [ ] Ruff, ty, and pytest pass.

## Definition of Done

* Tests added or updated where behavior changes.
* Lint, type check, and tests pass.
* Documentation is updated if the public command behavior changes.
* Windows-specific behavior remains testable on non-Windows through injected command runners.

## Out of Scope

* Downloading or upgrading `sing-box.exe`.
* Supporting multiple Windows service instances.
* Silent fallback to foreground process execution when service startup fails.
* Adding compatibility for the old `binPath= "<sing-box.exe> run"` service format.
* Downloading or bundling `nssm.exe`.

## Technical Notes

* Relevant files: `src/sing_cli/service.py`, `src/sing_cli/cli.py`, `tests/test_service.py`, `README.md`.
* Project spec index: `.trellis/spec/backend/index.md`.
* The current implementation uses `sc.exe` with argument lists; NSSM should also be called with argument lists and no shell string.
* NSSM command reference: `https://www.nssm.cc/commands`.
* NSSM usage reference: `https://nssm.cc/usage`.
