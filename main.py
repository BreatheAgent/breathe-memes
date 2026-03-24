#!/usr/bin/env python3
"""
🎰 Breathe Memes — Solana Meme Token Sniper

Usage:
    python main.py --scan           # Scan for trending tokens
    python main.py --analyze TOKEN  # Full analysis of a token
    python main.py --status         # Show open positions
"""

import argparse
import json
from sniper.engine import MemeSniper
from dex.jupiter import JupiterSwap
from analysis.token_analyzer import TokenAnalyzer


def main():
    parser = argparse.ArgumentParser(description="🎰 Breathe Meme Sniper")
    parser.add_argument("--scan", action="store_true", help="Scan trending tokens")
    parser.add_argument("--analyze", type=str, help="Analyze a token address")
    parser.add_argument("--status", action="store_true", help="Position status")
    parser.add_argument("--dry-run", action="store_true", default=True)
    args = parser.parse_args()

    if args.scan:
        sniper = MemeSniper(dry_run=args.dry_run)
        print("🔍 Scanning for trending Solana tokens...\n")
        tokens = sniper.scan_new_tokens()
        for t in tokens[:10]:
            print(f"  {t['address'][:20]}... | Source: {t['source']}")
        if not tokens:
            print("  No trending tokens found")

    elif args.analyze:
        analyzer = TokenAnalyzer()
        print(f"🔬 Analyzing token: {args.analyze}\n")
        result = analyzer.full_analysis(args.analyze)
        print(json.dumps(result, indent=2))

    elif args.status:
        sniper = MemeSniper(dry_run=args.dry_run)
        summary = sniper.get_meme_summary()
        print(json.dumps(summary, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
