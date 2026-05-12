import subprocess
from pathlib import Path

import pytest

from sing_cli.errors import ExternalCommandError
from sing_cli import service


def completed_process(
    command: list[str],
    stdout: str = "",
    stderr: str = "",
    returncode: int = 0,
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(command, returncode, stdout, stderr)


def enable_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(service.sys, "platform", "win32")


def test_configure_service_uses_argument_list(monkeypatch: pytest.MonkeyPatch) -> None:
    enable_windows(monkeypatch)
    commands: list[list[str]] = []

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return completed_process(command)

    service.configure_service("C:/Program Files/sing-box/sing-box.exe", "C:/Users/me/AppData/profiles/home", runner)

    assert commands == [
        [
            "sc.exe",
            "config",
            "sing-box",
            "binPath=",
            '"C:/Program Files/sing-box/sing-box.exe" run -c "C:/Users/me/AppData/profiles/home"',
        ]
    ]


def test_install_service_registers_autostart(monkeypatch: pytest.MonkeyPatch) -> None:
    enable_windows(monkeypatch)
    commands: list[list[str]] = []

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return completed_process(command)

    service.install_service(Path("C:/tools/sing-box.exe"), runner)

    assert commands == [
        ["sc.exe", "create", "sing-box", "binPath=", '"C:/tools/sing-box.exe" run', "start=", "auto"]
    ]


def test_run_sc_surfaces_external_command_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    enable_windows(monkeypatch)

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        return completed_process(command, stderr="Access is denied.", returncode=5)

    with pytest.raises(ExternalCommandError, match="Access is denied"):
        service.run_sc(["start", "sing-box"], runner)
