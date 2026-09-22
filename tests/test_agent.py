import sys
from unittest.mock import MagicMock, patch

import pytest

from src.agent import main
from src.models import CoinAnalysis, CoinGrade, CoinIdentity


def _analysis():
    return CoinAnalysis(
        identity=CoinIdentity(year=1950, country="Canada", denomination="50 Cents"),
        grade=CoinGrade(sheldon_scale=45, adjectival_grade="XF Details (Cleaned)"),
    )


def test_main_exits_when_api_key_missing(tmp_path):
    with patch.object(sys, "argv", ["src.agent", str(tmp_path)]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 1


def test_main_exits_when_no_image_files(tmp_path, monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake_key")
    (tmp_path / "notes.md").write_text("not an image")
    (tmp_path / "readme.txt").write_text("also not an image")

    with (
        patch("src.agent.CoinAnalyzer"),
        patch("src.agent.MarketResearcher"),
        patch("src.agent.Reporter"),
        patch.object(sys, "argv", ["src.agent", str(tmp_path)]),
    ):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 1


def test_main_filters_non_image_files_and_writes_report(tmp_path, monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake_key")
    (tmp_path / "obverse.JPG").write_bytes(b"fake")
    (tmp_path / "reverse.webp").write_bytes(b"fake")
    (tmp_path / "notes.md").write_text("ignore me")

    listing = "## 1950 Canada 50 Cents\nBuy It Now: $35"
    mock_analyzer = MagicMock()
    mock_analyzer.analyze_images.return_value = _analysis()
    mock_market = MagicMock()
    mock_market.search_recent_sales.return_value = [
        {"title": "Sale", "href": "http://s"}
    ]
    mock_market.analyze_market_data.return_value = "Melt is $22."
    mock_reporter = MagicMock()
    mock_reporter.generate_listing.return_value = listing

    with (
        patch("src.agent.CoinAnalyzer", return_value=mock_analyzer),
        patch("src.agent.MarketResearcher", return_value=mock_market),
        patch("src.agent.Reporter", return_value=mock_reporter),
        patch.object(sys, "argv", ["src.agent", str(tmp_path)]),
    ):
        main()

    image_paths = mock_analyzer.analyze_images.call_args[0][0]
    assert len(image_paths) == 2
    assert any(path.endswith("obverse.JPG") for path in image_paths)
    assert any(path.endswith("reverse.webp") for path in image_paths)
    assert not any(path.endswith(".md") for path in image_paths)

    report = tmp_path / "evaluation_report.md"
    assert report.exists()
    text = report.read_text()
    assert text.startswith("# Coin Evaluation Report")
    assert listing in text
