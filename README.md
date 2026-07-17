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

### Option A: Local Development (Separate Ports)

1. **Backend Server (Port 8000)**
   ```bash
   cd backend
   cp .env.example .env       # fill in your Testnet API key + secret
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
   *Swagger docs available at: http://127.0.0.1:8000/docs*

2. **Frontend Dev Server (Port 5173)**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   *Access frontend locally at: http://localhost:5173*

---

### Option B: Unified Production Server & Public Link (Ngrok)

You can serve both the React frontend and FastAPI backend on the same port (`8000`), allowing you to expose the entire app publicly with a single ngrok tunnel.

1. **Build the React UI**
   ```bash
   cd frontend
   npm install
   npm run build
   ```
   *This compiles the React assets into `frontend/dist`.*

2. **Start the Unified Server**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --port 8000 --host 0.0.0.0 --reload
   ```
   *FastAPI will now serve the compiled UI at `http://localhost:8000/` and API endpoints at `http://localhost:8000/ping`.*

3. **Expose Publicly via Ngrok**
   ```bash
   ngrok http 8000
   ```
   *Use the generated public URL (e.g. `https://xxxx.ngrok-free.app`) to access the full application from any device.*

---

### Get Testnet API Keys

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
