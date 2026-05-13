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
            download_profile_with_client(url, destination, http_client)
        return

    download_profile_with_client(url, destination, client)


def download_profile_with_client(url: str, destination: Path, http_client: HttpClient) -> None:
    profile_text = fetch_profile_text(url, http_client)
    validate_profile_json(profile_text)
    write_profile(destination, profile_text)


def fetch_profile_text(url: str, http_client: HttpClient) -> str:
    try:
        response = http_client.get(url)
        response.raise_for_status()
    except httpx.HTTPError as error:
        raise SingCliError(f"Unable to download profile: {error}") from error

    return response.text


def validate_profile_json(profile_text: str) -> None:
    try:
        json.loads(profile_text)
    except json.JSONDecodeError as error:
        raise SingCliError("Downloaded profile is not valid JSON.") from error


def write_profile(destination: Path, profile_text: str) -> None:
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(profile_text, encoding="utf-8")
    except OSError as error:
        raise SingCliError(f"Unable to write profile file: {destination}") from error
