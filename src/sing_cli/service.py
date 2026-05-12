from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from .errors import ExternalCommandError, SingCliError

SERVICE_NAME = "sing-box"
NSSM_EXE = "nssm.exe"

Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]


def default_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, check=False, text=True)


def ensure_windows() -> None:
    if sys.platform != "win32":
        raise SingCliError("Windows service operations are only supported on Windows.")


def resolve_bin(bin_path: Path | None) -> Path:
    if bin_path is None:
        found = shutil.which("sing-box.exe")
        if found is None:
            raise SingCliError("sing-box.exe was not found in PATH. Use 'sing install --bin <path>'.")
        resolved = Path(found)
    else:
        resolved = bin_path

    if not resolved.exists() or not resolved.is_file():
        raise SingCliError(f"sing-box.exe path does not exist or is not a file: {resolved}")
    return resolved


def resolve_nssm() -> str:
    found = shutil.which(NSSM_EXE)
    if found is None:
        raise SingCliError("nssm.exe was not found in PATH. Install NSSM and make nssm.exe available in PATH.")
    return found


def run_nssm(arguments: list[str], runner: Runner = default_runner) -> subprocess.CompletedProcess[str]:
    ensure_windows()
    command = [resolve_nssm(), *arguments]
    result = runner(command)
    if result.returncode != 0:
        output = result.stderr.strip() or result.stdout.strip()
        raise ExternalCommandError(command, result.returncode, output)
    return result


def install_service(bin_path: Path, runner: Runner = default_runner) -> None:
    run_nssm(create_service_arguments(bin_path), runner)
    run_nssm(["set", SERVICE_NAME, "Start", "SERVICE_AUTO_START"], runner)


def uninstall_service(runner: Runner = default_runner) -> None:
    run_nssm(["remove", SERVICE_NAME, "confirm"], runner)


def service_is_running(runner: Runner = default_runner) -> bool:
    result = run_nssm(["status", SERVICE_NAME], runner)
    return "SERVICE_RUNNING" in result.stdout


def configure_service(bin_path: str, profile_path: str, runner: Runner = default_runner) -> None:
    for arguments in configure_service_arguments(bin_path, profile_path):
        run_nssm(arguments, runner)


def create_service_arguments(bin_path: Path) -> list[str]:
    return ["install", SERVICE_NAME, str(bin_path)]


def configure_service_arguments(bin_path: str, profile_path: str) -> list[list[str]]:
    return [
        ["set", SERVICE_NAME, "Application", bin_path],
        ["set", SERVICE_NAME, "AppParameters", f'run -c "{profile_path}"'],
    ]


def start_service(runner: Runner = default_runner) -> None:
    run_nssm(["start", SERVICE_NAME], runner)


def stop_service(runner: Runner = default_runner) -> None:
    run_nssm(["stop", SERVICE_NAME], runner)
