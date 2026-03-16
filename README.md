# ChainMind

**AI-powered intelligent trading and automatic payment orchestration for HashKey Chain DeFi.**

Built for the **HashKey Chain On-Chain Horizon Hackathon** (AI + PayFi + DeFi tracks).

---

## Why ChainMind

| Hackathon requirement | How ChainMind delivers |
|-----------------------|-------------------------|
| **Theme:** Technology Empowers Finance, Innovation Reconstructs Ecosystem | AI empowers user financial decisions and automates payment flows on-chain. |
| **AI track:** AI-based automatic payment + AI-powered intelligent trading | (1) Smart payment rules with AI timing/amount suggestions, (2) Trading signals and strategy suggestions. |
| **PayFi (HSP):** One-stop payment & settlement | Integration point for HSP: payment requests, confirmations, status sync (HSP-ready when API spec is available). |
| **DeFi:** Transparency, efficiency, RWA-friendly | Dashboard and APIs for positions, yields, and risk views on HashKey Chain. |

---

## Quick Start

### 1. Clone and install

```bash
cd chain_mind
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

### 2. Configure environment

```bash
copy .env.example .env
# Edit .env: set WALLET_ADDRESS to your wallet to see HSK balance on the dashboard (read-only; no private key).
# Get testnet HSK: https://faucet.hsk.xyz/faucet
```

**Hackathon:** Using your real wallet address in `WALLET_ADDRESS` is fine and recommended. The app only reads balance from HashKey Chain Testnet (no private key in env); this fits the DeFi track (applications based on HashKey Chain).

### 3. Run the app

```bash
# From project root (chain_mind)
set FLASK_APP=backend.app
flask run
# Or: python -m flask --app backend.app run
```

Open **http://127.0.0.1:5000** → Dashboard, Trading, Payments.

---

## Project structure

```
chain_mind/
├── config/
│   └── settings.py         # Env and constants
├── backend/
│   ├── app.py              # Flask app
│   ├── api/
│   │   ├── dashboard.py    # Balance, txs, summary
│   │   ├── trading.py      # Signals, insights
│   │   └── payments.py     # Rules, payments, execute
│   ├── services/
│   │   ├── chain.py        # HashKey Chain RPC
│   │   ├── ai_signals.py   # Trading signals
│   │   ├── ai_payments.py  # Payment rules + AI suggestions
│   │   └── hsp_client.py   # PayFi / HSP (stub → real when spec ready)
│   └── tasks.py            # Scheduled rule evaluation
├── templates/              # Jinja2 (dashboard, trading, payments)
├── static/
├── tests/
├── details.md              # Hackathon brief
├── PROJECT_PROPOSAL.md     # Full proposal
├── requirements.txt
└── .env.example
```

---

## Features (MVP)

1. **AI Trading Assistant** – On-chain/API data → trend, volatility, risk regime → short text suggestions (e.g. “Consider DCA”, “High volatility – reduce size”). Exposed via `/api/signals` and `/api/insights`; UI: Dashboard + Trading tab.

2. **AI-Driven Automatic Payment** – User-defined rules: “When X (balance > Y, time, event), send Z to address W with amount A.” AI suggests timing/amount; backend evaluates rules and creates payment requests; **HSP** can be plugged in for request/confirmation/status (PayFi track). UI: Payment rules form + Payment history.

3. **Unified Dashboard** – Portfolio/balance, recent txs, AI insights, links to HashKey Chain ecosystem.

4. **Integration points**  
   - **HashKey Chain:** RPC read (balance, txs); optional write for demo.  
   - **HSP (PayFi):** Stub client for create/confirm/status; document “HSP-ready” in pitch.  
   - **AI:** Local Python (e.g. sklearn, rules) so basic demo works without external API keys.

---

## Demo script (for judges)

1. **Dashboard** – Show balance (or demo data), recent txs, AI insights.
2. **Trading** – Show signals (trend, volatility, risk) and 1–2 sentence AI insights.
3. **Payments** – Create a payment rule (e.g. “When balance above 1 ETH, send 0.1 to 0x…”); show AI suggestion; show payment history and HSP-ready flow.
4. **One-pager** – Problem → Solution → Architecture (ChainMind + HashKey Chain + HSP).

---

## Tech stack

- **Backend:** Python 3.10+, Flask  
- **API:** REST (Flask blueprints)  
- **UI:** Jinja2 + Bootstrap 5 + minimal JS  
- **AI:** Python (sklearn, numpy, rule-based)  
- **Tasks:** APScheduler (scheduled payments, periodic signals)  
- **Chain:** web3.py (HashKey Chain RPC)  
- **PayFi:** HTTP client for HSP (stub until API spec)

---

## Links

- [HashKey Chain Developer Community](https://hashfans.io/)
- [Developer Group](https://t.me/HashKeyChainHSK/95285)
