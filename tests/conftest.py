from unittest.mock import MagicMock

import pytest
from google import genai
from google.genai import types


@pytest.fixture
def mock_genai_client():
    mock_client = MagicMock(spec=genai.Client)
    # Mock models.generate_content
    mock_client.models = MagicMock()
    mock_client.models.generate_content = MagicMock()
    return mock_client


@pytest.fixture
def mock_ddgs():
    return MagicMock()
