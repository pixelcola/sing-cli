from pathlib import Path

import pytest
from typer.testing import CliRunner

from sing_cli import cli
from sing_cli.state import ProfileEntry, State, load_state, save_state


def write_state(tmp_path: Path, state: State) -> None:
    save_state(tmp_path / "state.json", state)


def test_restart_uses_active_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    calls: list[tuple[str, str | None, str | None]] = []
    state = State(
        bin="C:/tools/sing-box.exe",
        active="home",
        profiles={
            "home": ProfileEntry(
                url="https://example.com/home.json",
                path="C:/profiles/home.json",
                updated_at="2026-05-12T00:00:00Z",
            )
        },
    )
    write_state(tmp_path, state)
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)
    monkeypatch.setattr(cli, "stop_service", lambda: calls.append(("stop", None, None)))
    monkeypatch.setattr(
        cli,
        "configure_service",
        lambda bin_path, profile_path: calls.append(("configure", bin_path, profile_path)),
    )
    monkeypatch.setattr(cli, "start_service", lambda: calls.append(("start", None, None)))

    result = runner.invoke(cli.app, ["restart"])

    assert result.exit_code == 0
    assert result.stdout == "Restarted home\n"
    assert calls == [
        ("stop", None, None),
        ("configure", "C:/tools/sing-box.exe", "C:/profiles/home.json"),
        ("start", None, None),
    ]
    assert load_state(tmp_path / "state.json") == state


def test_restart_rejects_profile_argument() -> None:
    result = CliRunner().invoke(cli.app, ["restart", "home"])

    assert result.exit_code != 0
    assert "Got unexpected extra argument" in result.output


def test_restart_requires_active_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_state(tmp_path, State(bin="C:/tools/sing-box.exe"))
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)

    result = CliRunner().invoke(cli.app, ["restart"])

    assert result.exit_code == 1
    assert result.stderr == "Error: No active profile. Run 'sing start <name>' first.\n"


def test_restart_requires_existing_active_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_state(tmp_path, State(bin="C:/tools/sing-box.exe", active="missing"))
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)

    result = CliRunner().invoke(cli.app, ["restart"])

    assert result.exit_code == 1
    assert result.stderr == "Error: Profile does not exist: missing\n"


def test_start_running_service_mentions_restart_without_name(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_state(
        tmp_path,
        State(
            bin="C:/tools/sing-box.exe",
            profiles={
                "home": ProfileEntry(
                    url="https://example.com/home.json",
                    path="C:/profiles/home.json",
                    updated_at="2026-05-12T00:00:00Z",
                )
            },
        ),
    )
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)
    monkeypatch.setattr(cli, "service_is_running", lambda: True)

    result = CliRunner().invoke(cli.app, ["start", "home"])

    assert result.exit_code == 1
    assert result.stderr == "Error: sing-box service is already running. Use 'sing restart'.\n"
