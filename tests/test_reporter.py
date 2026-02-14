from unittest.mock import MagicMock

import pytest

from src.models import CoinAnalysis, CoinGrade, CoinIdentity
from src.reporter import Reporter


def test_generate_listing(mock_genai_client):
    """Test report generation prompt construction."""
    # Setup
    reporter = Reporter(api_key="fake_key")
    reporter.client = mock_genai_client

    # Input Data
    analysis = CoinAnalysis(
        identity=CoinIdentity(
            year=1950, country="Canada", denomination="50 Cents", composition="Silver"
        ),
        grade=CoinGrade(sheldon_scale=45, adjectival_grade="XF Details (Cleaned)"),
    )
    market_summary = "Melt is $10."
    search_results = [{"title": "Sale 1", "href": "http://sale1"}]

    # Mock response
    mock_response = MagicMock()
    mock_response.text = "# Report\nBIN: $15"
    mock_genai_client.models.generate_content.return_value = mock_response

    # Execute
    report = reporter.generate_listing(analysis, market_summary, search_results)

    # Verify
    assert "BIN: $15" in report

    # Verify Prompt content
    args, kwargs = mock_genai_client.models.generate_content.call_args
    prompt = kwargs["contents"]
    assert "1950" in prompt
    assert "Cleaned" in prompt
    assert "February 2026" in prompt  # Ensure the specific date instruction is present
