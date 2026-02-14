import json
import os
import warnings
from typing import List, Optional

from google import genai
from google.genai import types
from PIL import Image

from .models import CoinAnalysis, CoinGrade, CoinIdentity

# Suppress the FutureWarnings from google.generativeai
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")


class CoinAnalyzer:
    def __init__(self, api_key: str):
        self.client = genai.Client(
            api_key=api_key, http_options={"api_version": "v1beta"}
        )

    def analyze_images(self, image_paths: List[str]) -> CoinAnalysis:
        images = []
        for path in image_paths:
            try:
                img = Image.open(path)
                images.append(img)
            except Exception as e:
                print(f"Error loading image {path}: {e}")

        if not images:
            raise ValueError("No valid images provided for analysis.")

        prompt = """
        You are an expert professional Numismatist. Your job is to accurately identify and grade coins.

        CRITICAL ACCURACY INSTRUCTIONS:
        1. **Detect Cleaning/Damage**: You MUST strictly examine the fields and high points for "hairlines", "parallel scratches", or "unnatural washout" which indicate cleaning.
           - If found, you MUST penalize the grade to "Details" (e.g., "XF Details (Cleaned)" or "AU Details (Cleaned)").
           - Do NOT grade a cleaned coin as straight MS (Mint State).
        2. **Conservative Grading**: Be conservative. Most raw vintage coins found in the wild are NOT Top Pop Mint State. Default to AU/XF if uncertain.
        3. **Identification**: Identify the Year, Country, Denomination, Mint Mark, and Composition (Metal Content).

        Analyze the attached coin images and return a JSON object matching this schema:
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
                "visual_description": "Sharp details but evident parallel hairlines on cheek indicating cleaning."
            }
        }
        """

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, *images],
            config=types.GenerateContentConfig(
                response_mime_type="application/json", response_schema=CoinAnalysis
            ),
        )

        try:
            # The new SDK with response_schema should return a parsed object if using valid python types,
            # or strictly typed JSON text.
            # If using response_schema=CoinAnalysis (Pydantic), it might nicely return the object or text.
            # Let's assume it returns text that validates.
            # actually checking the SDK docs, response.text is the JSON string.
            if not response.text:
                raise ValueError("Empty response from Gemini")

            # Since we passed the Pydantic model to response_schema, the output should be strictly that schema.
            return CoinAnalysis.model_validate_json(response.text)

        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            print(f"Raw response: {response.text}")
            # Fallback/Empty
            raise e
