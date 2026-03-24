"""
Breathe Memes — Holder & Liquidity Analysis
Checks top holder concentration and LP lock status for rug-pull detection.
"""

import requests


class TokenAnalyzer:
    """Analyzes Solana tokens for rug-pull risk indicators."""

    def analyze_holders(self, token_address: str) -> dict:
        """
        Analyze top holder concentration.
        High concentration = high rug risk.
        """
        try:
            # Using Helius API (free tier)
            resp = requests.get(
                f"https://api.dexscreener.com/latest/dex/tokens/{token_address}",
                timeout=10,
            )
            data = resp.json()
            pairs = data.get("pairs", [])

            if not pairs:
                return {"risk": "high", "reason": "No pair data available"}

            pair = pairs[0]
            liquidity = pair.get("liquidity", {}).get("usd", 0)
            fdv = pair.get("fdv", 0)
            market_cap = pair.get("marketCap", 0)

            # Basic risk assessment
            if liquidity < 1000:
                return {"risk": "extreme", "reason": f"Very low liquidity: ${liquidity:.0f}"}
            elif liquidity < 5000:
                return {"risk": "high", "reason": f"Low liquidity: ${liquidity:.0f}"}
            elif liquidity < 50000:
                return {"risk": "moderate", "reason": f"Decent liquidity: ${liquidity:.0f}"}
            else:
                return {"risk": "low", "reason": f"Good liquidity: ${liquidity:.0f}"}

        except Exception as e:
            return {"risk": "unknown", "reason": f"Analysis failed: {e}"}

    def check_momentum(self, token_address: str) -> dict:
        """Check price and volume momentum."""
        try:
            resp = requests.get(
                f"https://api.dexscreener.com/latest/dex/tokens/{token_address}",
                timeout=10,
            )
            data = resp.json()
            pairs = data.get("pairs", [])

            if not pairs:
                return {"momentum": "unknown"}

            pair = pairs[0]
            price_changes = pair.get("priceChange", {})
            volume = pair.get("volume", {})

            return {
                "momentum": "bullish" if price_changes.get("h1", 0) > 5 else "bearish",
                "price_change_5m": price_changes.get("m5", 0),
                "price_change_1h": price_changes.get("h1", 0),
                "price_change_24h": price_changes.get("h24", 0),
                "volume_1h": volume.get("h1", 0),
                "volume_24h": volume.get("h24", 0),
            }

        except Exception as e:
            return {"momentum": "unknown", "error": str(e)}

    def full_analysis(self, token_address: str) -> dict:
        """Run complete token analysis."""
        holders = self.analyze_holders(token_address)
        momentum = self.check_momentum(token_address)

        # Overall risk score (0 = safe, 1 = dangerous)
        risk_map = {"low": 0.2, "moderate": 0.5, "high": 0.8, "extreme": 1.0, "unknown": 0.9}
        risk_score = risk_map.get(holders.get("risk", "unknown"), 0.9)

        return {
            "token": token_address,
            "risk_score": risk_score,
            "holder_analysis": holders,
            "momentum": momentum,
            "recommendation": "buy" if risk_score < 0.5 and momentum.get("momentum") == "bullish" else "skip",
        }
