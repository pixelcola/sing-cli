# uv tool commands

## Finding

`uv tool` installs tools with `uv tool install`, upgrades installed tools with `uv tool upgrade`, and removes tools with `uv tool uninstall`.

## Sources

* Official uv guide, "Using tools": https://docs.astral.sh/uv/guides/tools/
* Official uv CLI reference: https://docs.astral.sh/uv/reference/cli/

## Impact on README

Use `uv tool upgrade sing-cli` for the update action. `uv tool update sing-cli` is not a documented `uv tool` command in the official uv CLI reference and is not present in local `uv tool --help`.
