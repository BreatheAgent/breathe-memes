"""
Breathe Memes — Jupiter Aggregator Integration
Routes Solana swaps through Jupiter for best price execution.
"""

import requests


JUPITER_V6_QUOTE = "https://quote-api.jup.ag/v6/quote"
JUPITER_V6_SWAP = "https://quote-api.jup.ag/v6/swap"
USDC_SOLANA = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"


class JupiterSwap:
    """Jupiter aggregator for Solana token swaps."""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    def get_quote(self, input_mint: str, output_mint: str, amount: int, slippage_bps: int = 50) -> dict:
        """
        Get a swap quote from Jupiter.

        Args:
            input_mint: Input token mint (e.g., USDC)
            output_mint: Output token mint (meme token)
            amount: Amount in smallest unit (e.g., 1 USDC = 1_000_000)
            slippage_bps: Max slippage in basis points (50 = 0.5%)
        """
        try:
            resp = requests.get(JUPITER_V6_QUOTE, params={
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": slippage_bps,
            }, timeout=10)

            if resp.status_code == 200:
                data = resp.json()
                return {
                    "status": "ok",
                    "in_amount": data.get("inAmount", "0"),
                    "out_amount": data.get("outAmount", "0"),
                    "price_impact_pct": data.get("priceImpactPct", "0"),
                    "route_plan": data.get("routePlan", []),
                }
            else:
                return {"status": "error", "message": resp.text}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def swap(self, input_mint: str, output_mint: str, amount_usdc: float) -> dict:
        """Execute a swap via Jupiter."""
        amount_raw = int(amount_usdc * 1_000_000)  # USDC has 6 decimals

        quote = self.get_quote(input_mint, output_mint, amount_raw)
        if quote.get("status") != "ok":
            return {"error": f"Quote failed: {quote.get('message', 'unknown')}"}

        if self.dry_run:
            return {
                "status": "dry_run",
                "in_amount": amount_usdc,
                "out_amount": quote["out_amount"],
                "price_impact": quote["price_impact_pct"],
            }

        # In production: build and send the swap transaction
        # swap_response = requests.post(JUPITER_V6_SWAP, json={...})
        return {"status": "pending", "quote": quote}

    def buy_meme(self, token_mint: str, amount_usdc: float) -> dict:
        """Buy a meme token with USDC."""
        return self.swap(USDC_SOLANA, token_mint, amount_usdc)

    def sell_meme(self, token_mint: str, amount: float) -> dict:
        """Sell a meme token for USDC."""
        return self.swap(token_mint, USDC_SOLANA, amount)
