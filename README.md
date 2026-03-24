# 🎰 Breathe Memes — Solana Meme Token Sniper

Part of the [Breathe Ecosystem](https://github.com/BreatheAgent).

## What It Does

High-risk, high-reward meme token momentum trading on Solana.

### Features
- **Token Scanner** — Detects trending tokens via DexScreener
- **Safety Checker** — Rug-pull detection (liquidity, volume, dump alerts)
- **Jupiter Swaps** — Best-price execution via Jupiter aggregator
- **Auto Exit** — Take-profit at 3x, stop-loss at -30%

### Safety Limits (IMPORTANT)

| Control | Value |
|---------|-------|
| Max per trade | 2% of treasury |
| Total meme allocation | Max 5% of treasury |
| Take-profit | 3x (auto-sell) |
| Stop-loss | -30% (auto-sell) |
| Rug detection | Before every buy |

## Quick Start

```bash
pip install -r requirements.txt

# Scan trending tokens
python main.py --scan

# Analyze a specific token
python main.py --analyze TOKEN_ADDRESS

# Check positions
python main.py --status
```

## Architecture

- `sniper/engine.py` — Core sniper: scan, safety check, buy/sell, exit management
- `dex/jupiter.py` — Jupiter V6 aggregator for Solana swaps
- `analysis/token_analyzer.py` — Holder/liquidity/momentum analysis

## ⚠️ Warning

Meme tokens are extremely high-risk. This module is designed with strict safety limits, but losses are possible and expected. Never allocate more than you're willing to lose.

## Part of Breathe Ecosystem

| Repo | Purpose |
|------|---------|
| [breathe-core](https://github.com/BreatheAgent/breathe-core) | Central brain |
| [breathe-defi](https://github.com/BreatheAgent/breathe-defi) | DeFi yield |
| [breathe-trading](https://github.com/BreatheAgent/breathe-trading) | Perps + Polymarket |
| **breathe-memes** | Solana memes (you are here) |
