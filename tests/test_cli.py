from pathlib import Path

import pytest
from typer.testing import CliRunner

from sing_cli import cli
from sing_cli.errors import SingCliError
from sing_cli.state import ProfileEntry, State, load_state, save_state


def write_state(tmp_path: Path, state: State) -> None:
    save_state(tmp_path / "state.json", state)


def test_install_registers_service_and_saves_bin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    bin_path = tmp_path / "sing-box.exe"
    service_calls: list[Path] = []
    bin_path.write_text("exe", encoding="utf-8")
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)
    monkeypatch.setattr(cli, "resolve_bin", lambda value: bin_path)
    monkeypatch.setattr(cli, "install_service", lambda value: service_calls.append(value))

    result = runner.invoke(cli.app, ["install", "--bin", str(bin_path)])

    assert result.exit_code == 0
    assert result.stdout == f"Installed {bin_path}\n"
    assert service_calls == [bin_path]
    assert load_state(tmp_path / "state.json").bin == str(bin_path)


def test_install_failure_does_not_save_bin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bin_path = tmp_path / "sing-box.exe"
    bin_path.write_text("exe", encoding="utf-8")
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)
    monkeypatch.setattr(cli, "resolve_bin", lambda value: bin_path)

    def install_service(value: Path) -> None:
        raise SingCliError("install failed")

    monkeypatch.setattr(cli, "install_service", install_service)

    result = CliRunner().invoke(cli.app, ["install", "--bin", str(bin_path)])

    assert result.exit_code == 1
    assert result.stderr == "Error: install failed\n"
    assert not (tmp_path / "state.json").exists()


def test_uninstall_reports_success(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(cli, "uninstall_service", lambda: calls.append("uninstall"))

    result = CliRunner().invoke(cli.app, ["uninstall"])

    assert result.exit_code == 0
    assert result.stdout == "Uninstalled sing-box service\n"
    assert calls == ["uninstall"]


def test_uninstall_reports_service_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def uninstall_service() -> None:
        raise SingCliError("remove failed")

    monkeypatch.setattr(cli, "uninstall_service", uninstall_service)

    result = CliRunner().invoke(cli.app, ["uninstall"])

    assert result.exit_code == 1
    assert result.stderr == "Error: remove failed\n"


def test_start_configures_service_and_saves_active(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str | None, str | None]] = []
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
    monkeypatch.setattr(cli, "service_is_running", lambda: False)
    monkeypatch.setattr(
        cli,
        "configure_service",
        lambda bin_path, profile_path: calls.append(("configure", bin_path, profile_path)),
    )
    monkeypatch.setattr(cli, "start_service", lambda: calls.append(("start", None, None)))

    result = CliRunner().invoke(cli.app, ["start", "home"])

    assert result.exit_code == 0
    assert result.stdout == "Started home\n"
    assert calls == [
        ("configure", "C:/tools/sing-box.exe", "C:/profiles/home.json"),
        ("start", None, None),
    ]
    assert load_state(tmp_path / "state.json").active == "home"


def test_start_requires_installed_bin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_state(
        tmp_path,
        State(
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
    monkeypatch.setattr(cli, "service_is_running", lambda: False)

    result = CliRunner().invoke(cli.app, ["start", "home"])

    assert result.exit_code == 1
    assert result.stderr == "Error: sing-box.exe path is not installed. Run 'sing install' first.\n"


def test_start_configure_failure_does_not_start_or_save_active(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    state = State(
        bin="C:/tools/sing-box.exe",
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
    monkeypatch.setattr(cli, "service_is_running", lambda: False)

    def configure_service(bin_path: str, profile_path: str) -> None:
        calls.append("configure")
        raise SingCliError("configure failed")

    monkeypatch.setattr(cli, "configure_service", configure_service)
    monkeypatch.setattr(cli, "start_service", lambda: calls.append("start"))

    result = CliRunner().invoke(cli.app, ["start", "home"])

    assert result.exit_code == 1
    assert result.stderr == "Error: configure failed\n"
    assert calls == ["configure"]
    assert load_state(tmp_path / "state.json") == state


def test_start_service_failure_does_not_save_active(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    state = State(
        bin="C:/tools/sing-box.exe",
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
    monkeypatch.setattr(cli, "service_is_running", lambda: False)
    monkeypatch.setattr(cli, "configure_service", lambda bin_path, profile_path: None)

    def start_service() -> None:
        raise SingCliError("start failed")

    monkeypatch.setattr(cli, "start_service", start_service)

    result = CliRunner().invoke(cli.app, ["start", "home"])

    assert result.exit_code == 1
    assert result.stderr == "Error: start failed\n"
    assert load_state(tmp_path / "state.json") == state


def test_stop_reports_success(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(cli, "stop_service", lambda: calls.append("stop"))

    result = CliRunner().invoke(cli.app, ["stop"])

    assert result.exit_code == 0
    assert result.stdout == "Stopped sing-box service\n"
    assert calls == ["stop"]


def test_stop_reports_service_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def stop_service() -> None:
        raise SingCliError("stop failed")

    monkeypatch.setattr(cli, "stop_service", stop_service)

    result = CliRunner().invoke(cli.app, ["stop"])

    assert result.exit_code == 1
    assert result.stderr == "Error: stop failed\n"


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


def test_restart_stop_failure_does_not_reconfigure_or_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    write_state(
        tmp_path,
        State(
            bin="C:/tools/sing-box.exe",
            active="home",
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

    def stop_service() -> None:
        calls.append("stop")
        raise SingCliError("stop failed")

    monkeypatch.setattr(cli, "stop_service", stop_service)
    monkeypatch.setattr(cli, "configure_service", lambda bin_path, profile_path: calls.append("configure"))
    monkeypatch.setattr(cli, "start_service", lambda: calls.append("start"))

    result = CliRunner().invoke(cli.app, ["restart"])

    assert result.exit_code == 1
    assert result.stderr == "Error: stop failed\n"
    assert calls == ["stop"]


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


def test_add_downloads_profile_and_saves_entry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    downloads: list[tuple[str, Path]] = []
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)
    monkeypatch.setattr(cli, "now_utc", lambda: "2026-05-12T00:00:00Z")

    def download_profile(url: str, destination: Path) -> None:
        downloads.append((url, destination))
        destination.parent.mkdir(parents=True)
        destination.write_text('{"log":{"level":"info"}}', encoding="utf-8")

    monkeypatch.setattr(cli, "download_profile", download_profile)

    result = CliRunner().invoke(cli.app, ["add", "home", "https://example.com/home.json"])

    assert result.exit_code == 0
    assert result.stdout == "Added home\n"
    assert downloads == [("https://example.com/home.json", tmp_path / "profiles" / "home")]
    assert load_state(tmp_path / "state.json") == State(
        profiles={
            "home": ProfileEntry(
                url="https://example.com/home.json",
                path=str(tmp_path / "profiles" / "home"),
                updated_at="2026-05-12T00:00:00Z",
            )
        },
    )


def test_add_rejects_existing_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_state(
        tmp_path,
        State(
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

    result = CliRunner().invoke(cli.app, ["add", "home", "https://example.com/other.json"])

    assert result.exit_code == 1
    assert result.stderr == "Error: Profile already exists: home\n"


def test_add_rejects_invalid_profile_name_without_downloading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    downloads: list[str] = []
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)
    monkeypatch.setattr(cli, "download_profile", lambda url, destination: downloads.append(url))

    result = CliRunner().invoke(cli.app, ["add", "../home", "https://example.com/home.json"])

    assert result.exit_code == 1
    assert "Profile name may only contain" in result.stderr
    assert downloads == []
    assert not (tmp_path / "state.json").exists()


def test_add_download_failure_does_not_save_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)

    def download_profile(url: str, destination: Path) -> None:
        raise SingCliError("download failed")

    monkeypatch.setattr(cli, "download_profile", download_profile)

    result = CliRunner().invoke(cli.app, ["add", "home", "https://example.com/home.json"])

    assert result.exit_code == 1
    assert result.stderr == "Error: download failed\n"
    assert not (tmp_path / "state.json").exists()


def test_remove_deletes_non_active_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    profile_file = tmp_path / "profiles" / "home"
    profile_file.parent.mkdir()
    profile_file.write_text("{}", encoding="utf-8")
    write_state(
        tmp_path,
        State(
            profiles={
                "home": ProfileEntry(
                    url="https://example.com/home.json",
                    path=str(profile_file),
                    updated_at="2026-05-12T00:00:00Z",
                )
            },
        ),
    )
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)

    result = CliRunner().invoke(cli.app, ["remove", "home"])

    assert result.exit_code == 0
    assert result.stdout == "Removed home\n"
    assert not profile_file.exists()
    assert load_state(tmp_path / "state.json") == State()


def test_remove_rejects_active_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_state(
        tmp_path,
        State(
            active="home",
            profiles={
                "home": ProfileEntry(
                    url="https://example.com/home.json",
                    path=str(tmp_path / "profiles" / "home"),
                    updated_at="2026-05-12T00:00:00Z",
                )
            },
        ),
    )
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)

    result = CliRunner().invoke(cli.app, ["remove", "home"])

    assert result.exit_code == 1
    assert result.stderr == "Error: Cannot remove active profile: home\n"


def test_update_redownloads_profile_and_updates_timestamp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    profile_file = tmp_path / "profiles" / "home"
    downloads: list[tuple[str, Path]] = []
    write_state(
        tmp_path,
        State(
            profiles={
                "home": ProfileEntry(
                    url="https://example.com/home.json",
                    path=str(profile_file),
                    updated_at="2026-05-12T00:00:00Z",
                )
            },
        ),
    )
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)
    monkeypatch.setattr(cli, "now_utc", lambda: "2026-05-12T01:00:00Z")
    monkeypatch.setattr(cli, "download_profile", lambda url, destination: downloads.append((url, destination)))

    result = CliRunner().invoke(cli.app, ["update", "home"])

    assert result.exit_code == 0
    assert result.stdout == "Updated home\n"
    assert downloads == [("https://example.com/home.json", profile_file)]
    assert load_state(tmp_path / "state.json").profiles["home"].updated_at == "2026-05-12T01:00:00Z"


def test_update_download_failure_preserves_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    state = State(
        profiles={
            "home": ProfileEntry(
                url="https://example.com/home.json",
                path=str(tmp_path / "profiles" / "home"),
                updated_at="2026-05-12T00:00:00Z",
            )
        },
    )
    write_state(tmp_path, state)
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)

    def download_profile(url: str, destination: Path) -> None:
        raise SingCliError("download failed")

    monkeypatch.setattr(cli, "download_profile", download_profile)

    result = CliRunner().invoke(cli.app, ["update", "home"])

    assert result.exit_code == 1
    assert result.stderr == "Error: download failed\n"
    assert load_state(tmp_path / "state.json") == state


def test_update_requires_existing_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_state(tmp_path, State())
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)

    result = CliRunner().invoke(cli.app, ["update", "missing"])

    assert result.exit_code == 1
    assert result.stderr == "Error: Profile does not exist: missing\n"


def test_list_profiles_marks_active_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_state(
        tmp_path,
        State(
            active="work",
            profiles={
                "work": ProfileEntry(
                    url="https://example.com/work.json",
                    path="C:/profiles/work",
                    updated_at="2026-05-12T01:00:00Z",
                ),
                "home": ProfileEntry(
                    url="https://example.com/home.json",
                    path="C:/profiles/home",
                    updated_at="2026-05-12T00:00:00Z",
                ),
            },
        ),
    )
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)

    result = CliRunner().invoke(cli.app, ["list"])

    assert result.exit_code == 0
    assert result.stdout == (
        "  home\thttps://example.com/home.json\t2026-05-12T00:00:00Z\n"
        "* work\thttps://example.com/work.json\t2026-05-12T01:00:00Z\n"
    )


def test_list_profiles_reports_empty_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "app_dir", lambda: tmp_path)

    result = CliRunner().invoke(cli.app, ["list"])

    assert result.exit_code == 0
    assert result.stdout == "No profiles\n"
