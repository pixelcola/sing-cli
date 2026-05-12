# sing-cli

Windows CLI for installing and controlling the `sing-box` Windows service.

## Requirements

`sing-box.exe` and `nssm.exe` must be available in `PATH`. `sing install --bin <path>` can use a custom `sing-box.exe` path.

## Commands

| Command | Description |
|---|---|
| `sing install [--bin <path>]` | Register the `sing-box` Windows service through NSSM and enable autostart. |
| `sing uninstall` | Delete the `sing-box` Windows service. |
| `sing start <name>` | Start the service with a saved profile. |
| `sing stop` | Stop the service. |
| `sing restart <name>` | Stop, reconfigure, and start the service with a saved profile. |
| `sing add <name> <url>` | Download a complete `sing-box` JSON profile and save it under a name. |
| `sing remove <name>` | Remove a saved non-active profile. |
| `sing update <name>` | Redownload a saved profile from its URL. |
| `sing list` | List saved profiles and mark the active profile. |

`sing install` uses `sing-box.exe` from `PATH` unless `--bin` is provided. The CLI does not download or upgrade `sing-box.exe` or `nssm.exe`.
