from google import genai

from .models import CoinAnalysis


class Reporter:
    def __init__(self, api_key: str):
        self.client = genai.Client(
            api_key=api_key, http_options={"api_version": "v1beta"}
        )

    def generate_listing(
        self, analysis: CoinAnalysis, market_summary: str, search_results: list
    ) -> str:
        # Format search results for the prompt
        sales_list = "\n".join(
            [f"- {r.get('title', 'N/A')}: {r.get('href', '#')}" for r in search_results]
        )

        prompt = f"""
        Create a professional resale listing for this coin.

        Coin Details:
        {analysis.identity.model_dump_json()}

        Condition:
        {analysis.grade.model_dump_json()}

        Market Context:
        {market_summary}

        Recent Search Results (Reference):
        {sales_list}

        Generate the following:
        1. An attention-grabbing Title (max 80 chars) optimized for eBay/sales platforms.
        2. A detailed Description highlighting key features, condition, and rarity.
           - Be honest about any "Cleaned" or "Details" grade.
        3. A section titled "Recent Comparable Market Data".
           - List specific search results (Title/Link).
           - Mention the Metal/Melt value if applicable.
             - If a direct melt value is not found, CALCULATE it using the Silver Spot Price and the coin's weight/purity (e.g. 0.3 oz * Spot).
             - Use the date "February 2026" for context.
        4. A Recommended Listing Price.
           - **Buy It Now**: Set a competitive price. If "Cleaned" or "Details", heavily discount from MS book value.
           - **Auction Starting Price**: Set this near the Melt Value (intrinsic floor) to encourage bidding.
        5. "Pricing Justification": Explain the logic. Reference the Melt Value as the floor.

        Output in Markdown format.
        """

        response = self.client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return response.text
