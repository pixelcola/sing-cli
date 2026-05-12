from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

import httpx

from .errors import SingCliError


class HttpClient(Protocol):
    def get(self, url: str) -> httpx.Response: ...


def download_profile(url: str, destination: Path, client: HttpClient | None = None) -> None:
    if client is None:
        with httpx.Client(timeout=30.0, follow_redirects=True) as http_client:
            _download_profile(url, destination, http_client)
        return

    _download_profile(url, destination, client)


def _download_profile(url: str, destination: Path, http_client: HttpClient) -> None:
    try:
        response = http_client.get(url)
        response.raise_for_status()
        json.loads(response.text)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(response.text, encoding="utf-8")
    except httpx.HTTPError as error:
        raise SingCliError(f"Unable to download profile: {error}") from error
    except json.JSONDecodeError as error:
        raise SingCliError("Downloaded profile is not valid JSON.") from error
    except OSError as error:
        raise SingCliError(f"Unable to write profile file: {destination}") from error
