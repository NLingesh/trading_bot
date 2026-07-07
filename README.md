# Binance Futures Testnet Trading Bot

Full-stack trading dashboard — **FastAPI** backend + **React/Vite** frontend.

## Project Structure

```
trading_bot/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI routes + CORS
│   │   ├── client.py        # Raw requests REST client
│   │   ├── orders.py        # Binance service functions
│   │   ├── auth.py          # HMAC-SHA256 signing
│   │   ├── models.py        # Pydantic models
│   │   ├── validators.py    # Input validation
│   │   ├── utils.py         # Helpers
│   │   ├── logging_config.py
│   │   └── exceptions.py
│   ├── logs/bot.log
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/binance.js   # Axios service layer
│   │   ├── components/      # All page components
│   │   ├── pages/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css        # Dark theme styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Quick Start

### 1. Backend

```bash
cd backend
cp .env.example .env       # fill in your Testnet API key + secret
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend: http://127.0.0.1:8000  
Swagger: http://127.0.0.1:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

### 3. Get Testnet API Keys

Visit → https://testnet.binancefuture.com  
Login with GitHub → API Key section → Generate Key

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ping` | Test connectivity |
| GET | `/server-time` | Binance server time |
| GET | `/exchange-info` | Trading rules |
| GET | `/account` | Wallet + balances |
| GET | `/positions` | Open positions |
| GET | `/open-orders` | Active orders |
| GET | `/order-status/{symbol}/{id}` | Single order status |
| POST | `/order/market` | Place market order |
| POST | `/order/limit` | Place limit order |
| DELETE | `/cancel/{symbol}/{id}` | Cancel an order |

## Authentication

All signed requests use manual HMAC-SHA256 (no SDK):
1. Build query string from params + timestamp
2. Sign with `HMAC-SHA256(secret, query_string)`
3. Send `X-MBX-APIKEY` header
