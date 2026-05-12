from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .errors import SingCliError

PROFILE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


@dataclass(frozen=True)
class ProfileEntry:
    url: str
    path: str
    updated_at: str


@dataclass
class State:
    bin: str | None = None
    active: str | None = None
    profiles: dict[str, ProfileEntry] = field(default_factory=dict)


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate_profile_name(name: str) -> None:
    if not PROFILE_NAME_PATTERN.fullmatch(name):
        raise SingCliError("Profile name may only contain letters, numbers, underscores, hyphens, and dots.")


def load_state(path: Path) -> State:
    if not path.exists():
        return State()

    data = read_state_data(path)
    profiles = parse_profiles(path, data.get("profiles", {}))
    bin_path = optional_string_field(data, "bin")
    active = optional_string_field(data, "active")

    return State(bin=bin_path, active=active, profiles=profiles)


def read_state_data(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SingCliError(f"State file is not valid JSON: {path}") from error
    except OSError as error:
        raise SingCliError(f"Unable to read state file: {path}") from error

    if not isinstance(data, dict):
        raise SingCliError(f"State file must contain a JSON object: {path}")
    return data


def parse_profiles(path: Path, profiles_data: object) -> dict[str, ProfileEntry]:
    if not isinstance(profiles_data, dict):
        raise SingCliError(f"State field 'profiles' must be an object: {path}")

    profiles: dict[str, ProfileEntry] = {}
    for name, value in profiles_data.items():
        profile_name, entry = parse_profile_entry(path, name, value)
        profiles[profile_name] = entry
    return profiles


def parse_profile_entry(path: Path, name: object, value: object) -> tuple[str, ProfileEntry]:
    if not isinstance(name, str) or not isinstance(value, dict):
        raise SingCliError(f"State contains an invalid profile entry: {path}")

    entry_data: dict[Any, Any] = value
    url = entry_data.get("url")
    profile_path = entry_data.get("path")
    updated_at = entry_data.get("updated_at")
    if not isinstance(url, str) or not isinstance(profile_path, str) or not isinstance(updated_at, str):
        raise SingCliError(f"State contains an invalid profile entry: {name}")

    return name, ProfileEntry(url=url, path=profile_path, updated_at=updated_at)


def optional_string_field(data: dict[str, Any], field: str) -> str | None:
    value = data.get(field)
    if value is not None and not isinstance(value, str):
        raise SingCliError(f"State field '{field}' must be a string or null.")
    return value


def save_state(path: Path, state: State) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, Any] = {
        "bin": state.bin,
        "active": state.active,
        "profiles": {
            name: {"url": entry.url, "path": entry.path, "updated_at": entry.updated_at}
            for name, entry in sorted(state.profiles.items())
        },
    }
    try:
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as error:
        raise SingCliError(f"Unable to write state file: {path}") from error


def require_profile(state: State, name: str) -> ProfileEntry:
    try:
        return state.profiles[name]
    except KeyError as error:
        raise SingCliError(f"Profile does not exist: {name}") from error
