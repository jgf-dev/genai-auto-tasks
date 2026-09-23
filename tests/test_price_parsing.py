from test_benchmark_comparison import parse_price


def test_parse_price_extracts_amount_after_label():
    text = "Buy It Now: $34.95\nAuction Starting Price: $22.00"
    assert parse_price(text, "Buy It Now") == 34.95
    assert parse_price(text, "Auction Starting Price") == 22.0


def test_parse_price_strips_thousands_separators():
    assert parse_price("Buy It Now: $1,250.00", "Buy It Now") == 1250.0


def test_parse_price_is_case_insensitive():
    text = "buy it now price is $18.50 USD"
    assert parse_price(text, "Buy It Now") == 18.5


def test_parse_price_returns_none_when_label_or_amount_missing():
    assert parse_price("No asking price listed", "Buy It Now") is None
    assert parse_price("Buy It Now: sold", "Buy It Now") is None
