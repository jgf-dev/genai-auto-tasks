import pytest
from pydantic import ValidationError

from src.models import CoinAnalysis, CoinGrade, CoinIdentity


def test_coin_identity_requires_country_and_denomination():
    with pytest.raises(ValidationError):
        CoinIdentity()


def test_coin_identity_optional_fields_default_to_none():
    identity = CoinIdentity(country="Canada", denomination="50 Cents")
    assert identity.year is None
    assert identity.mint_mark is None
    assert identity.variety is None
    assert identity.composition is None


def test_coin_grade_requires_adjectival_grade():
    with pytest.raises(ValidationError):
        CoinGrade()


def test_coin_grade_defaults_visual_description():
    grade = CoinGrade(adjectival_grade="XF")
    assert grade.sheldon_scale is None
    assert grade.visual_description == "No visual description provided."


def test_coin_analysis_roundtrips_json():
    analysis = CoinAnalysis(
        identity=CoinIdentity(
            year=1950,
            country="Canada",
            denomination="50 Cents",
            composition="80% Silver",
        ),
        grade=CoinGrade(sheldon_scale=45, adjectival_grade="XF Details (Cleaned)"),
    )
    parsed = CoinAnalysis.model_validate_json(analysis.model_dump_json())
    assert parsed.identity.year == 1950
    assert parsed.grade.adjectival_grade == "XF Details (Cleaned)"
    assert parsed.raw_response is None


def test_coin_analysis_rejects_missing_identity():
    with pytest.raises(ValidationError):
        CoinAnalysis.model_validate_json(
            '{"grade": {"adjectival_grade": "XF", "visual_description": "worn"}}'
        )
