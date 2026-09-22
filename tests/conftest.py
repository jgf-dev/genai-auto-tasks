from unittest.mock import MagicMock

import pytest
from google import genai


@pytest.fixture(autouse=True)
def isolate_api_keys(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("VERTEX_API_KEY", raising=False)


@pytest.fixture
def mock_genai_client():
    mock_client = MagicMock(spec=genai.Client)
    mock_client.models = MagicMock()
    mock_client.models.generate_content = MagicMock()
    return mock_client


@pytest.fixture
def mock_ddgs():
    return MagicMock()
