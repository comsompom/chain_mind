# ChainMind – Demo One-Pager (HashKey Chain Horizon Hackathon)

## Problem
- **Manual payments** and **information overload** in DeFi: users lose time on repetitive transfers and miss optimal timing.
- No single place to see portfolio, AI-driven trading cues, and automated payment rules on HashKey Chain.

## Solution
**ChainMind** combines:
1. **AI-powered intelligent trading** – Signals (trend, volatility, risk) and short text suggestions (e.g. “Consider DCA”, “High volatility – reduce size”).
2. **AI-driven automatic payment** – User-defined rules (e.g. “When balance > X, send Y to address Z”); AI suggests timing/amount; execution path is **HSP-ready** (PayFi track).
3. **Unified dashboard** – Balance, recent txs, AI insights, and links to the HashKey Chain ecosystem.

## Architecture (ChainMind + HashKey Chain + HSP)

```
┌─────────────────────────────────────────────────────────────────┐
│                     Flask Web UI (Dashboard • Trading • Payments) │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP
┌────────────────────────────▼────────────────────────────────────┐
│                  Python Backend (API + Services)                  │
│  • AI service (signals, payment logic)  • HSP client (PayFi)     │
│  • HashKey Chain adapter (balance, txs)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
   HashKey Chain         HSP (PayFi)         AI (signals + rules)
   (read/write)          (payment flow)      (trading + payment logic)
```

## Demo flow (for judges)
1. **Dashboard** – Show balance (or demo data), recent txs, AI insights.
2. **Trading** – Show signals (trend, volatility, risk) and 1–2 sentence AI insights.
3. **Payments** – Create a payment rule (e.g. “When balance above 1 ETH, send 0.1 to 0x…”); show AI suggestion; show payment history and HSP-ready flow.
4. **Run:** `pip install -r requirements.txt` then `python run.py` or `flask --app backend.app run` → open http://127.0.0.1:5000

## Tracks alignment
- **AI:** Automatic payment + intelligent trading ✅  
- **PayFi (HSP):** Payment requests, confirmations, status sync (stub in place; real integration when API spec is available) ✅  
- **DeFi:** Transparency, efficiency, dashboard and chain integration ✅  

**Technology Empowers Finance, Innovation Reconstructs Ecosystem.**
