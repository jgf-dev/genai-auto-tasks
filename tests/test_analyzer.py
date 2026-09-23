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
    with patch("PIL.Image.open"):
        result = analyzer.analyze_images(["dummy.jpg"])

    # Verify
    assert isinstance(result, CoinAnalysis)
    assert result.identity.year == 1950
    assert result.grade.sheldon_scale == 45
    assert "Cleaned" in result.grade.adjectival_grade

    # Verify call arguments
    _, kwargs = mock_genai_client.models.generate_content.call_args
    assert kwargs["model"] == "gemini-2.0-flash"
    config = kwargs["config"]
    assert config.response_mime_type == "application/json"
    assert config.response_schema is CoinAnalysis
    assert kwargs["contents"][0].strip().startswith("You are an expert")


def test_analyze_images_raises_when_image_list_empty(mock_genai_client):
    analyzer = CoinAnalyzer(api_key="fake_key")
    analyzer.client = mock_genai_client

    with pytest.raises(ValueError, match="No valid images"):
        analyzer.analyze_images([])

    mock_genai_client.models.generate_content.assert_not_called()


def test_analyze_images_skips_unreadable_files(mock_genai_client):
    analyzer = CoinAnalyzer(api_key="fake_key")
    analyzer.client = mock_genai_client

    mock_response = MagicMock()
    mock_response.text = """
    {
        "identity": {"country": "Canada", "denomination": "50 Cents"},
        "grade": {"adjectival_grade": "VF", "visual_description": "wear"}
    }
    """
    mock_genai_client.models.generate_content.return_value = mock_response

    def open_image(path):
        if path.endswith("bad.jpg"):
            raise OSError("cannot identify image")
        return MagicMock(name=path)

    with patch("PIL.Image.open", side_effect=open_image):
        result = analyzer.analyze_images(["bad.jpg", "good.jpg"])

    assert result.identity.country == "Canada"
    contents = mock_genai_client.models.generate_content.call_args.kwargs["contents"]
    assert len(contents) == 2


def test_analyze_images_raises_on_empty_gemini_response(mock_genai_client):
    analyzer = CoinAnalyzer(api_key="fake_key")
    analyzer.client = mock_genai_client
    mock_genai_client.models.generate_content.return_value = MagicMock(text="")

    with (
        patch("PIL.Image.open", return_value=MagicMock()),
        pytest.raises(ValueError, match="Empty response from Gemini"),
    ):
        analyzer.analyze_images(["coin.jpg"])
