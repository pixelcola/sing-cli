from pathlib import Path

import pytest

from sing_cli.errors import SingCliError
from sing_cli.state import ProfileEntry, State, load_state, require_profile, save_state, validate_profile_name


def test_validate_profile_name_accepts_safe_filename_characters() -> None:
    validate_profile_name("home-1.prod")


def test_validate_profile_name_rejects_path_separators() -> None:
    with pytest.raises(SingCliError, match="Profile name"):
        validate_profile_name("../home")


def test_state_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    state = State(
        bin="C:/tools/sing-box.exe",
        active="home",
        profiles={
            "home": ProfileEntry(
                url="https://example.com/profile.json",
                path="C:/profiles/home",
                updated_at="2026-05-12T00:00:00Z",
            )
        },
    )

    save_state(path, state)

    assert load_state(path) == state


def test_require_profile_reports_missing_name() -> None:
    with pytest.raises(SingCliError, match="Profile does not exist"):
        require_profile(State(), "missing")


def test_load_state_rejects_non_object_root(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(SingCliError, match="must contain a JSON object"):
        load_state(path)


def test_load_state_rejects_non_object_profiles(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text('{"profiles": []}', encoding="utf-8")

    with pytest.raises(SingCliError, match="profiles"):
        load_state(path)


def test_load_state_rejects_invalid_profile_entry(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text('{"profiles": {"home": {"url": 1, "path": "p", "updated_at": "t"}}}', encoding="utf-8")

    with pytest.raises(SingCliError, match="invalid profile entry"):
        load_state(path)


def test_load_state_rejects_non_string_optional_fields(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text('{"bin": 1, "active": null, "profiles": {}}', encoding="utf-8")

    with pytest.raises(SingCliError, match="State field 'bin'"):
        load_state(path)
