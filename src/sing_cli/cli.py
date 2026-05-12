from __future__ import annotations

from pathlib import Path

import typer

from .errors import SingCliError
from .profile import download_profile
from .service import (
    configure_service,
    install_service,
    resolve_bin,
    service_is_running,
    start_service,
    stop_service,
    uninstall_service,
)
from .state import (
    ProfileEntry,
    State,
    load_state,
    now_utc,
    require_profile,
    save_state,
    validate_profile_name,
)

APP_NAME = "sing-cli"

app = typer.Typer(no_args_is_help=True)


def app_dir() -> Path:
    return Path(typer.get_app_dir(APP_NAME))


def state_path() -> Path:
    return app_dir() / "state.json"


def profile_path(name: str) -> Path:
    return app_dir() / "profiles" / name


def load_cli_state() -> State:
    return load_state(state_path())


def save_cli_state(state: State) -> None:
    save_state(state_path(), state)


def require_installed_bin(state: State) -> str:
    if state.bin is None:
        raise SingCliError("sing-box.exe path is not installed. Run 'sing install' first.")
    return state.bin


def fail(error: SingCliError) -> None:
    typer.echo(f"Error: {error}", err=True)
    raise typer.Exit(1)


@app.command()
def install(bin: Path | None = typer.Option(None, "--bin", help="Path to sing-box.exe.")) -> None:
    try:
        resolved_bin = resolve_bin(bin)
        install_service(resolved_bin)
        state = load_cli_state()
        state.bin = str(resolved_bin)
        save_cli_state(state)
    except SingCliError as error:
        fail(error)
    typer.echo(f"Installed {resolved_bin}")


@app.command()
def uninstall() -> None:
    try:
        uninstall_service()
    except SingCliError as error:
        fail(error)
    typer.echo("Uninstalled sing-box service")


@app.command()
def start(name: str) -> None:
    try:
        state = load_cli_state()
        entry = require_profile(state, name)
        bin_path = require_installed_bin(state)
        if service_is_running():
            raise SingCliError("sing-box service is already running. Use 'sing restart'.")
        configure_service(bin_path, entry.path)
        start_service()
        state.active = name
        save_cli_state(state)
    except SingCliError as error:
        fail(error)
    typer.echo(f"Started {name}")


@app.command()
def stop() -> None:
    try:
        stop_service()
    except SingCliError as error:
        fail(error)
    typer.echo("Stopped sing-box service")


@app.command()
def restart() -> None:
    try:
        state = load_cli_state()
        if state.active is None:
            raise SingCliError("No active profile. Run 'sing start <name>' first.")
        entry = require_profile(state, state.active)
        bin_path = require_installed_bin(state)
        stop_service()
        configure_service(bin_path, entry.path)
        start_service()
    except SingCliError as error:
        fail(error)
    typer.echo(f"Restarted {state.active}")


@app.command()
def add(name: str, url: str) -> None:
    try:
        validate_profile_name(name)
        state = load_cli_state()
        if name in state.profiles:
            raise SingCliError(f"Profile already exists: {name}")
        destination = profile_path(name)
        download_profile(url, destination)
        state.profiles[name] = ProfileEntry(url=url, path=str(destination), updated_at=now_utc())
        save_cli_state(state)
    except SingCliError as error:
        fail(error)
    typer.echo(f"Added {name}")


@app.command()
def remove(name: str) -> None:
    try:
        state = load_cli_state()
        entry = require_profile(state, name)
        if state.active == name:
            raise SingCliError(f"Cannot remove active profile: {name}")
        Path(entry.path).unlink()
        del state.profiles[name]
        save_cli_state(state)
    except SingCliError as error:
        fail(error)
    typer.echo(f"Removed {name}")


@app.command()
def update(name: str) -> None:
    try:
        state = load_cli_state()
        entry = require_profile(state, name)
        download_profile(entry.url, Path(entry.path))
        state.profiles[name] = ProfileEntry(url=entry.url, path=entry.path, updated_at=now_utc())
        save_cli_state(state)
    except SingCliError as error:
        fail(error)
    typer.echo(f"Updated {name}")


@app.command(name="list")
def list_profiles() -> None:
    try:
        state = load_cli_state()
    except SingCliError as error:
        fail(error)

    if not state.profiles:
        typer.echo("No profiles")
        return

    for name, entry in sorted(state.profiles.items()):
        marker = "*" if state.active == name else " "
        typer.echo(f"{marker} {name}\t{entry.url}\t{entry.updated_at}")
