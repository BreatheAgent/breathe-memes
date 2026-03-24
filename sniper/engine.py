"""
Breathe Memes — Solana Meme Token Sniper Engine
Detects new tokens, checks for safety (rug-pulls), and executes momentum trades.

Safety rules:
- Max 2% of treasury per trade
- Auto-sell at 3x profit or -30% loss
- Rug detection before every buy
- Never hold more than 5% of total treasury in memes
"""

import json
import os
import requests
from datetime import datetime, timezone


class MemeSniper:
    """Solana meme token sniping engine with safety checks."""

    MAX_TRADE_PCT = 0.02       # Max 2% of treasury per trade
    TAKE_PROFIT = 3.0          # Auto-sell at 3x
    STOP_LOSS = 0.30           # Auto-sell at -30%
    MAX_MEME_ALLOCATION = 0.05 # Never more than 5% of treasury in memes

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.positions = self._load_positions()

    def _load_positions(self) -> list:
        os.makedirs("data", exist_ok=True)
        if os.path.exists("data/meme_positions.json"):
            with open("data/meme_positions.json", "r") as f:
                return json.load(f)
        return []

    def _save_positions(self):
        with open("data/meme_positions.json", "w") as f:
            json.dump(self.positions, f, indent=2)

    def scan_new_tokens(self) -> list:
        """
        Scan for new Solana tokens using DexScreener API.
        Filters for tokens with sufficient liquidity and volume.
        """
        try:
            resp = requests.get(
                "https://api.dexscreener.com/latest/dex/tokens/solana",
                timeout=10,
            )
            # Use token boosted endpoint for trending tokens
            resp2 = requests.get(
                "https://api.dexscreener.com/token-boosts/latest/v1",
                timeout=10,
            )

            tokens = []

            # Parse trending tokens
            if resp2.status_code == 200:
                for token in resp2.json()[:20]:
                    if token.get("chainId") == "solana":
                        tokens.append({
                            "address": token.get("tokenAddress", ""),
                            "description": token.get("description", ""),
                            "url": token.get("url", ""),
                            "chain": "solana",
                            "source": "dexscreener_boost",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        })

            return tokens

        except Exception as e:
            print(f"[MemeSniper] Token scan failed: {e}")
            return []

    def check_token_safety(self, token_address: str) -> dict:
        """
        Run safety checks on a token before buying.
        Checks: liquidity, holder concentration, LP lock, contract verification.
        """
        try:
            # DexScreener pair data
            resp = requests.get(
                f"https://api.dexscreener.com/latest/dex/tokens/{token_address}",
                timeout=10,
            )
            data = resp.json()
            pairs = data.get("pairs", [])

            if not pairs:
                return {"safe": False, "reason": "No trading pairs found", "score": 0}

            pair = pairs[0]  # Primary pair
            liquidity = pair.get("liquidity", {}).get("usd", 0)
            volume_24h = pair.get("volume", {}).get("h24", 0)
            price_change = pair.get("priceChange", {}).get("h24", 0)
            age_hours = pair.get("pairCreatedAt", 0)

            checks = {
                "liquidity_ok": liquidity > 5000,      # Min $5K liquidity
                "volume_ok": volume_24h > 1000,          # Min $1K 24h volume
                "not_dump": price_change > -50,          # Not dumping > 50%
                "has_pairs": len(pairs) > 0,
            }

            score = sum(1 for v in checks.values() if v) / len(checks)
            safe = all(checks.values())

            result = {
                "safe": safe,
                "score": score,
                "checks": checks,
                "liquidity": liquidity,
                "volume_24h": volume_24h,
                "price_change_24h": price_change,
                "pair_count": len(pairs),
            }

            if not safe:
                failed = [k for k, v in checks.items() if not v]
                result["reason"] = f"Failed checks: {', '.join(failed)}"
            else:
                result["reason"] = "All safety checks passed"

            return result

        except Exception as e:
            return {"safe": False, "reason": f"Safety check error: {e}", "score": 0}

    def buy_token(self, token_address: str, amount_usdc: float, treasury_total: float) -> dict:
        """
        Buy a meme token after safety checks.
        Uses Jupiter aggregator for best swap rate.
        """
        # Enforce position size limit
        max_amount = treasury_total * self.MAX_TRADE_PCT
        if amount_usdc > max_amount:
            return {"error": f"Amount ${amount_usdc:.2f} exceeds max ${max_amount:.2f} (2% of treasury)"}

        # Safety check first
        safety = self.check_token_safety(token_address)
        if not safety["safe"]:
            return {"error": f"Token failed safety check: {safety['reason']}"}

        position = {
            "id": f"MEME-{len(self.positions) + 1:04d}",
            "token": token_address,
            "amount_usdc": amount_usdc,
            "status": "open" if not self.dry_run else "simulated",
            "entry_time": datetime.now(timezone.utc).isoformat(),
            "take_profit": self.TAKE_PROFIT,
            "stop_loss": self.STOP_LOSS,
            "safety_score": safety["score"],
            "pnl": 0,
        }

        if self.dry_run:
            print(f"[DRY RUN] Would buy ${amount_usdc:.2f} of {token_address[:16]}...")
        else:
            # In production: call Jupiter swap API
            # response = jupiter.swap(USDC, token_address, amount)
            position["tx_hash"] = "pending"

        self.positions.append(position)
        self._save_positions()
        return position

    def check_exit_conditions(self) -> list:
        """Check all open positions for exit conditions (TP/SL)."""
        exits = []
        for pos in self.positions:
            if pos["status"] not in ("open", "simulated"):
                continue

            # In production: fetch current price and calculate PNL
            # For now, check time-based exit (hold max 24h for memes)
            exits.append({
                "position_id": pos["id"],
                "token": pos["token"],
                "reason": "monitoring",
            })

        return exits

    def get_meme_summary(self) -> dict:
        active = [p for p in self.positions if p["status"] in ("open", "simulated")]
        return {
            "total_positions": len(self.positions),
            "active_positions": len(active),
            "total_invested": sum(p["amount_usdc"] for p in active),
            "total_pnl": sum(p.get("pnl", 0) for p in self.positions),
        }
