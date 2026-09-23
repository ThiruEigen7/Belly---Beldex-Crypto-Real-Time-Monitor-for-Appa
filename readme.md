# BELLY — Beldex Crypto Intelligence Dashboard

> A production-minded cryptocurrency monitoring platform for **Beldex (BDX)** that combines a responsive analytics dashboard with an event-driven data pipeline, historical market analysis, and ML-assisted price forecasting.

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Reflex](https://img.shields.io/badge/UI-Reflex-111827)](https://reflex.dev/)
[![Redis](https://img.shields.io/badge/Cache-Redis%2FUpstash-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%2FSupabase-336791?logo=postgresql&logoColor=white)](https://supabase.com/)
[![Kafka](https://img.shields.io/badge/Streaming-Kafka%2FRedpanda-231F20?logo=apachekafka&logoColor=white)](https://redpanda.com/)

## Executive Summary

BELLY is designed as a low-latency, cloud-ready market monitoring system. The dashboard presents the information an investor or analyst needs in one place:

- Current BDX price in INR and USD
- Historical price chart
- 24-hour market high, low, average, and volatility
- Quantity × price calculator
- 24-hour and 7-day prediction summaries
- Bullish, bearish, and neutral trend indicators
- Explicit loading and error states
- Manual refresh with an architecture ready for scheduled updates

The current repository contains the Reflex dashboard and integration contracts for the backend. The production architecture extends this UI with FastAPI services, Kafka/Redpanda streaming, Redis caching, Supabase persistence, and Airflow-managed analytics jobs.

> **Project status:** Dashboard and API-client flows are implemented. The external ingestion, persistence, and ML services are structured as the next production integration layer. Predictions shown in the UI should be treated as informational, not financial advice.

## Why This Project Is Interesting in an Interview

This project demonstrates more than a CRUD screen. It shows how to reason about a data product from source to user:

1. Acquire market data without coupling the UI to a third-party provider.
2. Stream and persist data so historical analysis is reproducible.
3. Serve hot data quickly through a cache while retaining durable history.
4. Separate user-facing reads from background computation.
5. Present uncertain ML output honestly with trend labels and timestamps.
6. Package the system for local development and cloud deployment.

## Product Capabilities

### Dashboard

- **Current price card:** INR/USD display and last-updated indicator.
- **Historical analysis:** Recharts line chart for recent price history.
- **Market statistics:** High, low, average, and volatility metrics.
- **Price calculator:** Immediate valuation for any BDX quantity.
- **Forecast panel:** Five-day visualization derived from short- and medium-term prediction targets.
- **Resilience:** Loading spinners, disabled refresh actions during requests, and visible API errors.
- **Responsive dark UI:** Reflex components with a green accent and consistent card-based layout.

### Planned production services

| Endpoint | Responsibility |
| --- | --- |
| `GET /health` | Service health and deployment checks |
| `GET /current-price` | Latest BDX price in INR and USD |
| `GET /history?days=7` | Historical observations for charting |
| `GET /stats?period=7d` | Aggregated market statistics |
| `GET /predict` | Prediction targets and trend classification |

## Architecture

```text
                         ┌──────────────────────────────┐
                         │          User Browser         │
                         │   BELLY Reflex Dashboard      │
                         └──────────────┬───────────────┘
                                        │ HTTPS / state events
                                        ▼
                         ┌──────────────────────────────┐
                         │       API / Application        │
                         │ FastAPI: price, history,      │
                         │ stats, predict, health         │
                         └──────────────┬───────────────┘
                                        │
                         ┌──────────────┴───────────────┐
                         │                              │
                         ▼                              ▼
              ┌────────────────────┐         ┌────────────────────┐
              │ Redis / Upstash    │         │ Supabase PostgreSQL │
              │ Hot/latest values  │         │ Durable time series │
              │ Short-lived cache  │         │ Stats and forecasts │
              └─────────▲──────────┘         └─────────▲──────────┘
                        │                              │
                        └──────────────┬───────────────┘
                                       │ consumer writes
                                       ▼
                         ┌──────────────────────────────┐
                         │       Kafka / Redpanda         │
                         │       belly-price topic        │
                         └──────────────▲───────────────┘
                                        │ publish
                                        │
                         ┌────────────┴───────────────┐
                         │ Price Producer              │
                         │ Beldex/market data source  │
                         │ Scheduled every ~10 minutes│
                         └────────────────────────────┘

                 Airflow DAGs run independently for statistics
                 computation and scheduled prediction generation.
```

### Design principles

- **Separation of concerns:** UI, API, ingestion, storage, and analytics can be deployed independently.
- **Cache-aside reads:** Read the latest values from Redis first; fall back to PostgreSQL when necessary, then repopulate the cache.
- **Event-driven ingestion:** Kafka provides buffering, decoupling, and the ability to replay price events.
- **Durable source of truth:** Supabase/PostgreSQL stores historical observations rather than relying on an in-memory cache.
- **Asynchronous I/O:** `httpx` and async-compatible clients keep network-bound operations from blocking the dashboard.
- **Configuration by environment:** Credentials and service URLs are injected through environment variables, never hardcoded.

## End-to-End Data Flow

### 1. Ingestion flow

```text
Market API
   │
   ▼
Producer fetches and validates price
   │
   ▼
Kafka/Redpanda: belly-price
   │
   ▼
Consumer acknowledges event
   ├──► Redis: latest price / hot data
   └──► Supabase: durable historical record
```

### 2. User request flow

```text
Browser mounts dashboard or user clicks Refresh
   │
   ▼
Reflex State.load_all_data()
   │
   ├──► /current-price
   ├──► /history?days=7
   ├──► /stats?period=7d
   └──► /predict
          │
          ▼
       API checks Redis → falls back to Supabase if needed
          │
          ▼
       JSON response → Reflex state → chart/cards re-render
```

The current state loader intentionally keeps each operation isolated: a failed request produces an error message without silently displaying fabricated values. A next optimization is to execute independent reads concurrently with `asyncio.gather()` and add per-request timeouts/retries.

### 3. Analytics flow

```text
Historical prices → Airflow scheduled DAG
                         ├── compute high/low/average/volatility
                         └── train/run forecasting model
                                      │
                                      ▼
                         Store versioned prediction result
                                      │
                                      ▼
                         /predict serves latest result to UI
```

## Key Engineering Challenges and Solutions

| Challenge | Solution | Interview takeaway |
| --- | --- | --- |
| Market data can be delayed, missing, or inconsistent | Validate incoming events, timestamp observations, and expose freshness in the UI | Real-time systems need data-quality rules, not only API calls |
| A third-party price API should not be called for every user | Use a producer and Kafka topic to collect data once, then serve many users from Redis/PostgreSQL | Decouple ingestion rate from read traffic |
| Low latency versus durable history | Redis stores hot/latest data; Supabase stores the historical source of truth | Choose storage based on access pattern and durability |
| Background calculations can slow user requests | Move statistics and predictions into Airflow jobs and serve precomputed results | Request paths should stay predictable and cheap |
| Forecasts are uncertain | Return explicit horizon values and a trend classification; label them as informational | ML output needs product context and responsible communication |
| Partial API failures can leave an inconsistent screen | Track loading/error state and make each endpoint failure visible | Resilience includes useful failure states, not just retries |
| Different environments need different service URLs and secrets | Use `.env.example`, platform variables, and runtime configuration | Twelve-factor configuration makes deployment repeatable |
| Many services are difficult to run locally | Provide Docker Compose services, health checks, persistent volumes, and restart policies | Operational ergonomics are part of application design |
| Reflex and backend dependency compatibility | Pin Reflex and key runtime versions in `requirements.txt`; isolate API integration behind HTTP contracts | Version constraints prevent avoidable deployment failures |

## Technology Stack

| Layer | Technology | Why it is used |
| --- | --- | --- |
| Frontend | Reflex, Python, Recharts | Build a reactive dashboard without a separate JavaScript application |
| API contract | FastAPI-compatible HTTP endpoints | Typed, testable boundary between UI and data services |
| HTTP client | `httpx` | Async calls from the Reflex state layer |
| Streaming | Kafka / Redpanda, `kafka-python` | Durable, decoupled price-event transport |
| Hot storage | Redis / Upstash | Fast access to current prices and short-lived results |
| Historical storage | PostgreSQL / Supabase, `asyncpg` | Durable time-series and analytical data |
| Orchestration | Apache Airflow | Scheduled statistics and prediction workflows |
| ML/data | pandas, Prophet, statsmodels, scikit-learn | Feature preparation, forecasting, and model experimentation |
| Packaging | Docker, Docker Compose | Reproducible local and production-like environments |
| Deployment | Railway, Vercel, or container platforms | Practical cloud deployment options with environment configuration |

## Repository Layout

```text
.
├── belly/
│   ├── belly.py                 # Reflex app, state, API calls, and UI components
│   ├── streaming/               # Producer/consumer integration (deployment topology)
│   └── airflow/                 # Scheduled analytics and prediction workflows
├── assets/                      # Static assets
├── requirements.txt             # Python dependencies
├── rxconfig.py                  # Reflex configuration and plugins
├── Dockerfile                   # Container image definition
├── docker-compose.prod.yml      # API, frontend, streaming, Redis, and Airflow topology
├── .env.example                 # Safe configuration template
├── deploy_cloud.sh              # Interactive deployment helper
├── CLOUD_ARCHITECTURE_DIAGRAM.md# Expanded cloud architecture reference
├── DEPLOYMENT_GUIDE.md          # Deployment and operational notes
└── SECURITY.md                  # Security checklist and credential guidance
```

## Run Locally

### Option A: Run the Reflex dashboard

```bash
git clone https://github.com/ThiruEigen7/Belly---Beldex-Crypto-Real-Time-Monitor-for-Appa.git
cd Belly---Beldex-Crypto-Real-Time-Monitor-for-Appa
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env.production # fill only the values you need
reflex init
reflex run
```

Open `http://localhost:3000`.

The dashboard currently expects the API base URL configured in the Reflex state. For a connected environment, set it to the deployed backend or local API service and keep credentials in environment variables.

### Option B: Run the container topology

```bash
cp .env.example .env.production
# Add credentials to .env.production; never commit this file.
docker compose --env-file .env.production -f docker-compose.prod.yml up -d

docker compose -f docker-compose.prod.yml logs -f
```

Typical local ports:

- Dashboard: `http://localhost:3000`
- API: `http://localhost:8000`
- Airflow: `http://localhost:8080`
- Redis: `localhost:6379`

> Compose is a production-oriented topology template. Confirm that all referenced service modules and API routes are present in the checkout before enabling every service.

## Configuration and Security

Start with `.env.example`. Important groups include:

- Supabase URL and key
- Redis URL and token
- Kafka/Redpanda brokers and credentials
- Airflow admin credentials
- Fetch interval and prediction model settings
- Backend and Reflex host/port settings

Never commit `.env`, `.env.production`, API keys, database passwords, or broker credentials. Before a public deployment:

- Rotate any credentials that may have appeared in logs or documentation.
- Use HTTPS and platform secret storage.
- Set a strong Airflow password.
- Restrict CORS and API access appropriately.
- Add rate limiting, structured logs, monitoring, and database backups.
- Validate and bound query parameters such as `days` and `period`.

## Deployment Strategy

### Recommended path: Railway + managed services

1. Push the repository to GitHub.
2. Create a Railway project from the repository.
3. Add variables from `.env.example` in the Railway dashboard.
4. Deploy the API and dashboard as separate services where appropriate.
5. Use managed Supabase, Upstash Redis, and Redpanda/Kafka services.
6. Verify health, current price, history, statistics, and prediction routes.
7. Enable HTTPS, logs, alerts, and credential rotation.

For a self-hosted or advanced setup, use `docker-compose.prod.yml` or deploy the services independently on AWS, GCP, or Azure.

## API Contract Example

The UI expects response shapes similar to these:

```json
{
  "price_inr": 0.0,
  "price_usd": 0.0,
  "timestamp": "2026-01-01T00:00:00Z"
}
```

```json
{
  "high": 0.0,
  "low": 0.0,
  "average": 0.0,
  "volatility": 0.0
}
```

```json
{
  "prediction_24h": 0.0,
  "prediction_7d": 0.0,
  "trend": "neutral"
}
```

In production, add a schema version, source timestamp, currency, data-quality metadata, and model metadata so clients can distinguish stale data from valid zero values.

## Trade-offs and Next Improvements

- **Polling versus WebSockets:** 10-minute polling is simpler and cost-effective for a portfolio monitor; WebSockets are appropriate when sub-minute updates become a real requirement.
- **Precomputed versus on-demand ML:** Precomputed forecasts make user requests fast and reproducible; on-demand inference is more flexible but increases latency and cost.
- **Single deployment versus distributed services:** A single container is easier to operate at low traffic; independent services improve scaling and fault isolation as usage grows.
- **Model accuracy versus explainability:** Start with a measurable baseline and compare Prophet/ARIMA against naïve forecasts before presenting predictions as a feature.

Recommended next steps:

1. Add automated tests for API schemas, calculator state, and error handling.
2. Centralize an `httpx.AsyncClient` with timeout, retry, and connection-pooling policies.
3. Run independent dashboard requests concurrently.
4. Add event validation, idempotency keys, dead-letter handling, and consumer lag monitoring.
5. Add model evaluation with MAE/MAPE, backtesting, and prediction confidence intervals.
6. Add CI for linting, tests, Docker builds, and dependency/security scanning.

## Interview Talking Points

A concise explanation of the project:

> “BELLY is a Beldex market-monitoring system. The Reflex frontend consumes a small, stable API for current price, history, statistics, and predictions. Behind that API, a scheduled producer publishes validated market events to Kafka. A consumer writes the latest values to Redis for low-latency reads and historical observations to Supabase for durable analysis. Airflow computes statistics and forecasts independently, so expensive work never blocks the user request path. The main design challenge was balancing freshness, latency, durability, and operational simplicity; the solution was an event-driven pipeline with cache-aside reads and precomputed analytics.”

## License

No license has been declared yet. Add a license file before distributing the project publicly.

---

Built as a portfolio project to demonstrate Python application design, streaming architecture, cloud deployment, and practical ML integration.
