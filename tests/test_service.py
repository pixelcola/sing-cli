import subprocess
import sys
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
    monkeypatch.setattr(service.shutil, "which", lambda executable: f"C:/tools/{executable}")


def test_default_runner_replaces_invalid_utf8_output() -> None:
    result = service.default_runner(
        [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'valid' + bytes([0x82]) + b'output')"]
    )

    assert result.returncode == 0
    assert result.stdout == "valid\ufffdoutput"


def test_configure_service_uses_argument_list(monkeypatch: pytest.MonkeyPatch) -> None:
    enable_windows(monkeypatch)
    commands: list[list[str]] = []

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return completed_process(command)

    service.configure_service("C:/Program Files/sing-box/sing-box.exe", "C:/Users/me/AppData/profiles/home", runner)

    assert commands == [
        [
            "C:/tools/nssm.exe",
            "set",
            "sing-box",
            "Application",
            "C:/Program Files/sing-box/sing-box.exe",
        ],
        [
            "C:/tools/nssm.exe",
            "set",
            "sing-box",
            "AppParameters",
            'run -c "C:/Users/me/AppData/profiles/home"',
        ],
    ]


def test_install_service_registers_autostart(monkeypatch: pytest.MonkeyPatch) -> None:
    enable_windows(monkeypatch)
    commands: list[list[str]] = []

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return completed_process(command)

    service.install_service(Path("C:/tools/sing-box.exe"), runner)

    assert commands == [
        ["C:/tools/nssm.exe", "install", "sing-box", "C:/tools/sing-box.exe"],
        ["C:/tools/nssm.exe", "set", "sing-box", "Start", "SERVICE_AUTO_START"],
    ]


def test_run_nssm_surfaces_external_command_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    enable_windows(monkeypatch)

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        return completed_process(command, stderr="Access is denied.", returncode=5)

    with pytest.raises(ExternalCommandError, match="Access is denied"):
        service.run_nssm(["start", "sing-box"], runner)


def test_resolve_nssm_reports_missing_executable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(service.shutil, "which", lambda executable: None)

    with pytest.raises(service.SingCliError, match="nssm.exe was not found"):
        service.resolve_nssm()


def test_service_is_running_reads_nssm_status(monkeypatch: pytest.MonkeyPatch) -> None:
    enable_windows(monkeypatch)

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        return completed_process(command, stdout="SERVICE_RUNNING")

    assert service.service_is_running(runner)
