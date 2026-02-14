from unittest.mock import MagicMock, patch

import pytest

from src.analyzer import CoinAnalyzer
from src.models import CoinAnalysis


def test_analyze_images_success(mock_genai_client):
    """Test successful image analysis with mocked Gemini response."""
    # Setup
    analyzer = CoinAnalyzer(api_key="fake_key")
    analyzer.client = mock_genai_client

    # Mock response
    mock_response = MagicMock()
    mock_response.text = """
    {
        "identity": {
            "year": 1950,
            "country": "Canada",
            "denomination": "50 Cents",
            "mint_mark": null,
            "variety": "Design in 0",
            "composition": "80% Silver"
        },
        "grade": {
            "sheldon_scale": 45,
            "adjectival_grade": "XF Details (Cleaned)",
            "visual_description": "Cleaned coin."
        }
    }
    """
    mock_genai_client.models.generate_content.return_value = mock_response

    # Execute
    # We mock Image.open to avoid needing real files
    with patch("PIL.Image.open") as mock_open:
        result = analyzer.analyze_images(["dummy.jpg"])

    # Verify
    assert isinstance(result, CoinAnalysis)
    assert result.identity.year == 1950
    assert result.grade.sheldon_scale == 45
    assert "Cleaned" in result.grade.adjectival_grade

    # Verify call arguments
    args, kwargs = mock_genai_client.models.generate_content.call_args
    assert kwargs["model"] == "gemini-2.0-flash"
