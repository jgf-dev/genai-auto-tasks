import json
from typing import Dict, List

from ddgs import DDGS
from google import genai

from .models import CoinGrade, CoinIdentity


class MarketResearcher:
    def __init__(self, api_key: str):
        self.ddgs = DDGS()
        self.client = genai.Client(
            api_key=api_key, http_options={"api_version": "v1beta"}
        )

    def search_recent_sales(
        self, identity: CoinIdentity, grade: CoinGrade
    ) -> List[Dict]:
        # Construct a cleaner query
        parts = [
            str(identity.year),
            identity.country,
            identity.denomination,
            identity.mint_mark,
            identity.variety,
            "coin value",
            "sold",
        ]
        query = " ".join([p for p in parts if p])
        print(f"Searching for: {query}")

        results = list(self.ddgs.text(query, max_results=10))

        # Broader search if needed
        if not results:
            print("No results found. Trying broader query...")
            simple_query = (
                f"{identity.year} {identity.country} {identity.denomination} coin price"
            )
            print(f"Searching for: {simple_query}")
            results = list(self.ddgs.text(simple_query, max_results=10))

        # ACCURACY UPDATE: Search for melt/bullion value logic
        # We append a specific search for melt value to ensure we get that data point
        if "Silver" in (identity.composition or "") or "Gold" in (
            identity.composition or ""
        ):
            melt_query = (
                f"{identity.year} {identity.country} {identity.denomination} melt value"
            )
            print(f"Searching for melt value: {melt_query}")
            melt_results = list(self.ddgs.text(melt_query, max_results=3))
            results.extend(melt_results)

            # 2. Search for general spot price to enable calculation if specific fail
            spot_query = f"current {identity.composition.split('%')[0] if '%' in identity.composition else 'silver'} spot price"
            print(f"Searching for spot price: {spot_query}")
            spot_results = list(self.ddgs.text(spot_query, max_results=2))
            results.extend(spot_results)

        return results

    def analyze_market_data(
        self, search_results: List[Dict], identity: CoinIdentity, grade: CoinGrade
    ) -> str:
        prompt = f"""
        You are a market analyst. Analyze the following search results for a coin.

        Coin: {identity.year} {identity.country} {identity.denomination}
        Grade: {grade.adjectival_grade} (Sheldon: {grade.sheldon_scale})

        Search Results:
        {search_results}

        Task:
        1. Determine the 'Melt Value' (intrinsic metal value) if applicable. Mention this explicitly as a price floor.
        2. Identify the fair market value range for this specific grade.
           - If the coin is 'Details' or 'Cleaned', heavily discount it compared to straight-grade examples.
           - Compare to similar 'sold' listings if available.
        3. Summarize the market trends.
        """

        response = self.client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return response.text
