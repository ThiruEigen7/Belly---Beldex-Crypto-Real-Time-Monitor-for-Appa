# BELLY 🚀 - Beldex Crypto Monitor

Real-time cryptocurrency monitoring system for Beldex (BDX) with historical analysis, statistics, and ML-powered predictions.

## 📁 Project Structure

```
BELLY/
├── belly.py                    # Main Reflex app
├── rxconfig.py                 # Reflex configuration
├── requirements.txt            # Python dependencies
├── yoo/
│   └── components/
│       ├── __init__.py
│       ├── calculator.py       # Price calculator component
│       ├── chart.py           # 5-day price chart
│       ├── prediction.py      # ML prediction panel
│       └── stats_panel.py     # Market statistics
└── .web/                      # Auto-generated (Reflex build)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Reflex

```bash
reflex init
```

### 3. Run Development Server

```bash
reflex run
```

The app will be available at `http://localhost:3000`

## 🎨 Features

### ✅ Implemented (Mock Data)
- **Current Price Display**: Real-time BDX price in INR and USD
- **5-Day Chart**: Historical price visualization
- **Market Stats**: 24h high, low, average, and volatility
- **Price Calculator**: Calculate total value for any quantity
- **Predictions**: 24h and 7-day forecasts with trend indicators
- **Auto-refresh**: Button to reload all data
- **Dark Theme**: Modern UI with green accent

### 🔜 To Be Connected
- FastAPI backend integration
- Real API calls (currently using mock data)
- WebSocket support for real-time updates
- Auto-refresh every 10 minutes

## 🔌 Connecting to Backend

Once your FastAPI backend is deployed on Railway:

1. Update `rxconfig.py`:
```python
api_url="https://your-railway-app.railway.app"
```

2. Update `belly.py` State class:
```python
api_base_url: str = "https://your-railway-app.railway.app"
```

3. Replace mock data with actual API calls using `httpx`:

```python
import httpx

async def load_current_price(self):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{self.api_base_url}/current-price")
        data = response.json()
        self.current_price_inr = data["price_inr"]
        self.current_price_usd = data["price_usd"]
        self.last_updated = data["timestamp"]
```

## 🌐 Deployment

### Deploy to Reflex Cloud

```bash
reflex deploy
```

Follow the prompts to deploy to Reflex Cloud.

### Alternative: Vercel/Netlify

Export static build:
```bash
reflex export
```

Deploy the `.web/_static` directory.

## 🎯 Next Steps

1. **Build FastAPI Backend** ✅ (Next priority)
   - `/current-price` endpoint
   - `/history?days=5` endpoint
   - `/stats` endpoint
   - `/predict` endpoint

2. **Set up Kafka Streaming**
   - Producer (price fetcher)
   - Consumer (Redis + Supabase writer)

3. **Configure Storage**
   - Redis (Upstash) for hot data
   - Supabase for historical data

4. **Build Airflow DAGs**
   - Stats computation
   - ML prediction pipeline

## 📊 Architecture

```
Reflex UI → FastAPI → Redis/Supabase
              ↑
         Kafka Consumer
              ↑
         Kafka Producer
              ↑
        Beldex API
```

## 🛠️ Tech Stack

- **Frontend**: Reflex (Python-based React)
- **Backend**: FastAPI (coming next)
- **Streaming**: Kafka/Redpanda
- **Cache**: Redis (Upstash)
- **Database**: PostgreSQL (Supabase)
- **Orchestration**: Apache Airflow
- **ML**: Prophet/ARIMA (predictions)

## 📝 Notes

- Mock data is currently hardcoded for UI development
- Real-time updates will use 10-minute intervals
- All services will be free-tier friendly
- Perfect for portfolio demonstration

---

**Status**: UI Complete ✅ | Backend In Progress 🔄