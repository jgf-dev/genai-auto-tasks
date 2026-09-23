from unittest.mock import MagicMock

from src.market import MarketResearcher
from src.models import CoinGrade, CoinIdentity


def test_search_recent_sales(mock_genai_client, mock_ddgs):
    """Test search logic, including melt value search trigger."""
    # Setup
    market = MarketResearcher(api_key="fake_key")
    market.client = mock_genai_client
    market.ddgs = mock_ddgs

    # Setup inputs
    identity = CoinIdentity(
        year=1950,
        country="Canada",
        denomination="50 Cents",
        composition="80% Silver",
        variety="Design in 0",
    )
    grade = CoinGrade(
        sheldon_scale=45, adjectival_grade="XF", visual_description="Looks okay."
    )

    # Mock DDGS response
    mock_ddgs.text.side_effect = [
        [{"title": "Coin 1", "href": "http://1"}],  # Main query
        [{"title": "Melt Value", "href": "http://melt"}],  # Melt query
        [{"title": "Spot Price", "href": "http://spot"}],  # Spot query
    ]

    # Execute
    results = market.search_recent_sales(identity, grade)

    # Verify
    assert len(results) == 3
    # Verify that melt query was called because composition contains "Silver"
    assert mock_ddgs.text.call_count == 3

    # Check calls
    calls = mock_ddgs.text.call_args_list
    assert "melt value" in calls[1][0][0]


def test_analyze_market_data(mock_genai_client):
    """Test summarization logic."""
    market = MarketResearcher(api_key="fake_key")
    market.client = mock_genai_client

    mock_response = MagicMock()
    mock_response.text = "Market is bullish. Melt is $10."
    mock_genai_client.models.generate_content.return_value = mock_response

    summary = market.analyze_market_data(
        [{"title": "Test"}],
        CoinIdentity(year=1950, country="Canada", denomination="50c"),
        CoinGrade(sheldon_scale=45, adjectival_grade="XF"),
    )

    assert "bullish" in summary

    prompt = mock_genai_client.models.generate_content.call_args.kwargs["contents"]
    assert "1950" in prompt
    assert "Canada" in prompt
    assert "XF" in prompt
    assert "45" in prompt
    assert "Melt Value" in prompt
    assert "Details" in prompt
    assert "Cleaned" in prompt


def test_search_recent_sales_includes_mint_mark_and_variety(
    mock_genai_client, mock_ddgs
):
    market = MarketResearcher(api_key="fake_key")
    market.client = mock_genai_client
    market.ddgs = mock_ddgs

    identity = CoinIdentity(
        year=1921,
        country="USA",
        denomination="Morgan Dollar",
        mint_mark="S",
        variety="Double Die",
        composition="Copper",
    )
    mock_ddgs.text.return_value = [{"title": "Sale", "href": "http://s"}]

    market.search_recent_sales(identity, CoinGrade(adjectival_grade="AU"))

    query = mock_ddgs.text.call_args[0][0]
    assert query == "1921 USA Morgan Dollar S Double Die coin value sold"
    assert mock_ddgs.text.call_count == 1


def test_search_recent_sales_broader_fallback_then_melt_for_silver(
    mock_genai_client, mock_ddgs
):
    market = MarketResearcher(api_key="fake_key")
    market.client = mock_genai_client
    market.ddgs = mock_ddgs

    identity = CoinIdentity(
        year=1950,
        country="Canada",
        denomination="50 Cents",
        composition="80% Silver",
    )
    mock_ddgs.text.side_effect = [
        [],
        [{"title": "Broad", "href": "http://b"}],
        [{"title": "Melt", "href": "http://m"}],
        [{"title": "Spot", "href": "http://s"}],
    ]

    results = market.search_recent_sales(identity, CoinGrade(adjectival_grade="VF"))

    assert results == [
        {"title": "Broad", "href": "http://b"},
        {"title": "Melt", "href": "http://m"},
        {"title": "Spot", "href": "http://s"},
    ]
    assert mock_ddgs.text.call_count == 4
    calls = [call[0][0] for call in mock_ddgs.text.call_args_list]
    assert "coin price" in calls[1]
    assert "melt value" in calls[2]
    assert "spot price" in calls[3]
