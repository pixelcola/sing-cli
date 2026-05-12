from pathlib import Path

import httpx
import pytest

from sing_cli.errors import SingCliError
from sing_cli.profile import download_profile


class StubHttpClient:
    def __init__(self, response: httpx.Response) -> None:
        self.response = response

    def get(self, url: str) -> httpx.Response:
        return self.response


def response_with_text(text: str) -> httpx.Response:
    request = httpx.Request("GET", "https://example.com/profile.json")
    return httpx.Response(200, text=text, request=request)


def test_download_profile_writes_valid_json(tmp_path: Path) -> None:
    destination = tmp_path / "profile.json"

    download_profile(
        "https://example.com/profile.json",
        destination,
        StubHttpClient(response_with_text('{"log": {"level": "info"}}')),
    )

    assert destination.read_text(encoding="utf-8") == '{"log": {"level": "info"}}'


def test_download_profile_rejects_invalid_json(tmp_path: Path) -> None:
    destination = tmp_path / "profile.json"

    with pytest.raises(SingCliError, match="not valid JSON"):
        download_profile(
            "https://example.com/profile.json",
            destination,
            StubHttpClient(response_with_text("not json")),
        )

    assert not destination.exists()
