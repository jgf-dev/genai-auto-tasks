import argparse
import os
import sys

from dotenv import load_dotenv
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .analyzer import CoinAnalyzer
from .market import MarketResearcher
from .reporter import Reporter

# Load environment variables
load_dotenv()


def main():
    console = Console()

    parser = argparse.ArgumentParser(description="Vintage Coin Evaluator Agent")
    parser.add_argument("images_dir", help="Directory containing images of the coin")
    args = parser.parse_args()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        console.print(
            "[red]Error: GOOGLE_API_KEY not found in environment variables.[/red]"
        )
        sys.exit(1)

    # Initialize modules
    analyzer = CoinAnalyzer(api_key)
    market = MarketResearcher(api_key)
    reporter = Reporter(api_key)

    # 1. Image Analysis
    image_files = [
        os.path.join(args.images_dir, f)
        for f in os.listdir(args.images_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]

    if not image_files:
        console.print(f"[red]No image files found in {args.images_dir}[/red]")
        sys.exit(1)

    with console.status("[bold green]Analyzing coin images..."):
        analysis = analyzer.analyze_images(image_files)

    console.print(
        Panel(
            f"[bold]Identification:[/bold] {analysis.identity.year} {analysis.identity.country} {analysis.identity.denomination}\n"
            f"[bold]Grade:[/bold] {analysis.grade.adjectival_grade} (Sheldon: {analysis.grade.sheldon_scale})",
            title="Coin Analysis Result",
            border_style="blue",
        )
    )

    # 2. Market Research
    with console.status("[bold green]Searching market data..."):
        search_results = market.search_recent_sales(analysis.identity, analysis.grade)
        market_summary = market.analyze_market_data(
            search_results, analysis.identity, analysis.grade
        )

    console.print(Panel(market_summary, title="Market Analysis", border_style="yellow"))

    # 3. Report Generation
    with console.status("[bold green]Generating listing..."):
        listing = reporter.generate_listing(analysis, market_summary, search_results)

    console.print("\n[bold]Generated Listing:[/bold]")
    console.print(listing)

    # Save report
    output_path = os.path.join(args.images_dir, "evaluation_report.md")
    with open(output_path, "w") as f:
        f.write("# Coin Evaluation Report\n\n")
        f.write(listing)
    console.print(f"\n[green]Report saved to {output_path}[/green]")


if __name__ == "__main__":
    main()
