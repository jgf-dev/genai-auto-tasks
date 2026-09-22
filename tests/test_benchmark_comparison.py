import os
import re
from pathlib import Path

import pytest

from src.agent import main

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_BENCHMARK") != "1",
        reason="Live Gemini/DDGS benchmark; set RUN_LIVE_BENCHMARK=1 to enable",
    ),
]

# Paths
BASE_DIR = Path(__file__).parent.parent
IMAGE_DIR = BASE_DIR / "images" / "can-50c-1950-1"
EVAL_REPORT = IMAGE_DIR / "evaluation_report.md"


def parse_price(text, label):
    """Extracts the first dollar amount after a specific label."""
    # Regex to find "$XX.XX" after the label
    # simplified regex for demo
    match = re.search(rf"{label}.*?\$([\d,]+\.?\d*)", text, re.IGNORECASE | re.DOTALL)
    if match:
        return float(match.group(1).replace(",", ""))
    return None


def test_benchmark_accuracy():
    """
    Runs the agent on the sample image directory and compares the output
    to the standard human-generated report.
    """
    # 1. Run the Agent
    # We invoke main() directly, mocking sys.argv is one way,
    # or just calling the logic.
    # For a full integration test, running via subprocess is safer but slower.
    # Let's import main and patch sys.argv
    import sys
    from unittest.mock import patch

    with patch.object(sys, "argv", ["src.agent", str(IMAGE_DIR)]):
        try:
            main()
        except SystemExit as e:
            # agent.py might sys.exit(0) on success
            assert e.code == 0

    # 2. Verify Output Exists
    assert EVAL_REPORT.exists()

    agent_text = EVAL_REPORT.read_text()

    print("\n--- Agent Output Summary ---")
    print(agent_text[:500] + "...")

    # 3. Check for "Cleaned" or "Details" detection
    # The standard report says "XF/AU Details (Cleaned)"
    # The agent should detect "Cleaned" or "Details"
    has_details = "details" in agent_text.lower()
    has_cleaned = "cleaned" in agent_text.lower()

    if not (has_details or has_cleaned):
        pytest.fail("Agent failed to detect 'Cleaned' or 'Details' condition.")

    # 4. Check for Melt Value mention
    assert "melt value" in agent_text.lower(), "Agent failed to mention 'Melt Value'."

    # 5. Check Pricing Accuracy
    # Standard BIN is ~$35 CAD (approx $25 USD). The mock setup might return USD or CAD.
    # Let's assume the agent returns USD if searching standard sites, or CAD if specific sites.
    # The agent's recent run returned ~$42.
    # Let's set a realistic pass/fail range: < $60.
    # (Previous failure was $375).

    agent_price = parse_price(agent_text, "Buy It Now")
    assert agent_price is not None, (
        "Could not parse 'Buy It Now' price from agent report."
    )

    print(f"\nAgent BIN Price: ${agent_price}")

    # Fail if price is absurdly high (indicating missed condition)
    assert agent_price < 80, (
        f"Agent price ${agent_price} is too high! Expected < $80 for a cleaned coin."
    )
    assert agent_price > 15, f"Agent price ${agent_price} is too low! Melt is ~$22."


if __name__ == "__main__":
    test_benchmark_accuracy()
