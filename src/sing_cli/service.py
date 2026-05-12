from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from .errors import ExternalCommandError, SingCliError

SERVICE_NAME = "sing-box"

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


def run_sc(arguments: list[str], runner: Runner = default_runner) -> subprocess.CompletedProcess[str]:
    ensure_windows()
    command = ["sc.exe", *arguments]
    result = runner(command)
    if result.returncode != 0:
        output = result.stderr.strip() or result.stdout.strip()
        raise ExternalCommandError(command, result.returncode, output)
    return result


def install_service(bin_path: Path, runner: Runner = default_runner) -> None:
    run_sc(create_service_arguments(bin_path), runner)


def uninstall_service(runner: Runner = default_runner) -> None:
    run_sc(["delete", SERVICE_NAME], runner)


def service_is_running(runner: Runner = default_runner) -> bool:
    result = run_sc(["query", SERVICE_NAME], runner)
    return "RUNNING" in result.stdout


def configure_service(bin_path: str, profile_path: str, runner: Runner = default_runner) -> None:
    run_sc(configure_service_arguments(bin_path, profile_path), runner)


def create_service_arguments(bin_path: Path) -> list[str]:
    return ["create", SERVICE_NAME, "binPath=", f'"{bin_path}" run', "start=", "auto"]


def configure_service_arguments(bin_path: str, profile_path: str) -> list[str]:
    return ["config", SERVICE_NAME, "binPath=", f'"{bin_path}" run -c "{profile_path}"']


def start_service(runner: Runner = default_runner) -> None:
    run_sc(["start", SERVICE_NAME], runner)


def stop_service(runner: Runner = default_runner) -> None:
    run_sc(["stop", SERVICE_NAME], runner)
