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
    assert "Details" in prompt
    assert "Cleaned" in prompt
    assert "Melt Value" in prompt


def test_search_recent_sales_falls_back_to_broader_query(mock_genai_client, mock_ddgs):
    market = MarketResearcher(api_key="fake_key")
    market.client = mock_genai_client
    market.ddgs = mock_ddgs

    identity = CoinIdentity(
        year=1950, country="Canada", denomination="50 Cents", composition="Copper"
    )
    grade = CoinGrade(adjectival_grade="VF")
    mock_ddgs.text.side_effect = [
        [],
        [{"title": "Broad result", "href": "http://broad"}],
    ]

    results = market.search_recent_sales(identity, grade)

    assert results == [{"title": "Broad result", "href": "http://broad"}]
    assert mock_ddgs.text.call_count == 2
    assert "coin price" in mock_ddgs.text.call_args_list[1][0][0]


def test_search_recent_sales_skips_melt_for_base_metal(mock_genai_client, mock_ddgs):
    market = MarketResearcher(api_key="fake_key")
    market.client = mock_genai_client
    market.ddgs = mock_ddgs

    identity = CoinIdentity(
        year=1965, country="USA", denomination="1 Cent", composition="Copper"
    )
    mock_ddgs.text.return_value = [{"title": "Penny", "href": "http://p"}]

    results = market.search_recent_sales(identity, CoinGrade(adjectival_grade="F"))

    assert len(results) == 1
    assert mock_ddgs.text.call_count == 1
    assert "melt" not in mock_ddgs.text.call_args[0][0].lower()


def test_search_recent_sales_includes_melt_for_gold(mock_genai_client, mock_ddgs):
    market = MarketResearcher(api_key="fake_key")
    market.client = mock_genai_client
    market.ddgs = mock_ddgs

    identity = CoinIdentity(
        year=1927, country="USA", denomination="20 Dollars", composition="Gold"
    )
    mock_ddgs.text.side_effect = [
        [{"title": "Sale", "href": "http://s"}],
        [{"title": "Melt", "href": "http://m"}],
        [{"title": "Spot", "href": "http://sp"}],
    ]

    results = market.search_recent_sales(identity, CoinGrade(adjectival_grade="AU"))

    assert len(results) == 3
    assert mock_ddgs.text.call_count == 3
    assert "melt value" in mock_ddgs.text.call_args_list[1][0][0]
    assert "spot price" in mock_ddgs.text.call_args_list[2][0][0]


def test_search_recent_sales_omits_empty_identity_fields(mock_genai_client, mock_ddgs):
    market = MarketResearcher(api_key="fake_key")
    market.client = mock_genai_client
    market.ddgs = mock_ddgs

    identity = CoinIdentity(
        year=1950,
        country="Canada",
        denomination="50 Cents",
        mint_mark=None,
        variety="",
        composition=None,
    )
    mock_ddgs.text.return_value = [{"title": "Hit", "href": "http://h"}]

    market.search_recent_sales(identity, CoinGrade(adjectival_grade="G"))

    query = mock_ddgs.text.call_args[0][0]
    assert query == "1950 Canada 50 Cents coin value sold"
    assert "None" not in query


def test_search_recent_sales_handles_missing_composition(mock_genai_client, mock_ddgs):
    market = MarketResearcher(api_key="fake_key")
    market.client = mock_genai_client
    market.ddgs = mock_ddgs

    identity = CoinIdentity(country="France", denomination="1 Franc")
    mock_ddgs.text.return_value = [{"title": "Franc", "href": "http://f"}]

    results = market.search_recent_sales(identity, CoinGrade(adjectival_grade="VG"))

    assert len(results) == 1
    assert mock_ddgs.text.call_count == 1
