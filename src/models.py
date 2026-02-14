from typing import Optional

from pydantic import BaseModel, Field


class CoinIdentity(BaseModel):
    year: Optional[int] = Field(
        default=None, description="The year minted on the coin."
    )
    country: str = Field(description="The country of origin.")
    denomination: str = Field(
        description="The face value of the coin (e.g., '50 Cents', '1 Dollar')."
    )
    mint_mark: Optional[str] = Field(
        default=None, description="The mint mark, if present (e.g., 'D', 'S', 'W')."
    )
    variety: Optional[str] = Field(
        default=None,
        description="Any specific variety or error (e.g., 'Full Bell Lines', 'Double Die').",
    )
    composition: Optional[str] = Field(
        default=None,
        description="The metal composition (e.g., '90% Silver', 'Copper').",
    )


class CoinGrade(BaseModel):
    sheldon_scale: Optional[int] = Field(
        default=None, description="Estimated numeric grade on the Sheldon Scale (0-70)."
    )
    adjectival_grade: str = Field(
        description="Adjectival grade (e.g., 'Good', 'Fine', 'Mint State')."
    )
    visual_description: str = Field(
        default="No visual description provided.",
        description="Detailed visual description of the coin's condition, noting wear, scratches, or toning.",
    )


class CoinAnalysis(BaseModel):
    identity: CoinIdentity
    grade: CoinGrade
    raw_response: Optional[str] = Field(
        default=None, description="The raw text response from the model for debugging."
    )
