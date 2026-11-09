"""Shared test configuration.

Environment variables are set BEFORE the app modules are imported, because
`config.Settings` is read once at import time.
"""
import os

os.environ.setdefault("GROQ_API_KEY", "test-key")
os.environ.setdefault("API_KEY", "")  # auth off by default in tests
os.environ.setdefault("RATE_LIMIT", "1000/minute")

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client():
    with TestClient(main.app) as c:
        yield c
