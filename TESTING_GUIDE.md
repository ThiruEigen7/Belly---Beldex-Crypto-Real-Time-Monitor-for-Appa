# Complete System Testing Guide

## Overview

This guide walks you through testing all layers of the Belly system:
1. **Streaming Layer** - Real-time price data ingestion
2. **Database Layer** - PostgreSQL/Supabase storage
3. **API Layer** - FastAPI endpoints
4. **Analytics Layer** - Statistics computation (Airflow)
5. **Prediction Layer** - ML forecasting (Airflow)
6. **Presentation Layer** - Reflex UI

---

## Prerequisites

Before testing, ensure all services are running:

```bash
# 1. Start Airflow
cd /home/thiru/belly/belly/airflow
docker-compose -f docker-compose.sqlite.yml up -d

# 2. Start API Server
cd /home/thiru/belly
chmod +x start_api.sh
./start_api.sh
```

---

## Quick Test (Automated)

Run the complete test suite:

```bash
cd /home/thiru/belly
chmod +x test_complete_system.sh
./test_complete_system.sh
```

This will automatically test:
- ✅ Infrastructure (Docker, Redis, Airflow)
- ✅ DAG detection and execution
- ✅ Database connectivity
- ✅ All API endpoints
- ✅ Beldex price fetching
- ✅ Analytics computation
- ✅ Prediction model

---

## Manual Testing

### 1. Test Beldex Price Fetch

#### Option A: Via CoinGecko API (Direct)
```bash
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=beldex&vs_currencies=inr,usd" | jq
```

Expected output:
```json
{
  "beldex": {
    "inr": 6.85,
    "usd": 0.082456
  }
}
```

#### Option B: Via Belly API
```bash
# Start API first, then:
curl http://localhost:8000/current-price | jq
```

Expected output:
```json
{
  "price_inr": 6.85,
  "price_usd": 0.082456,
  "timestamp": "2025-12-14T10:30:00.000Z",
  "source": "coingecko"
}
```

---

### 2. Test API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health | jq
```

Expected:
```json
{
  "status": "healthy",
  "message": "All systems operational",
  "timestamp": "2025-12-14T10:30:00.000Z",
  "services": {
    "redis": "up",
    "database": "up"
  }
}
```

#### Current Price
```bash
curl http://localhost:8000/current-price | jq
```

#### Price History (7 days)
```bash
curl "http://localhost:8000/history?days=7" | jq
```

#### Market Stats (24h)
```bash
curl "http://localhost:8000/stats?period=24h" | jq
```

Expected:
```json
{
  "period": "24h",
  "high": 7.12,
  "low": 6.45,
  "average": 6.78,
  "volatility": 3.5,
  "change_percent": 2.3,
  "computed_at": "2025-12-14T00:00:00.000Z"
}
```

#### Price Predictions
```bash
curl http://localhost:8000/predict | jq
```

Expected:
```json
{
  "prediction_24h": 6.92,
  "prediction_7d": 7.15,
  "trend": "bullish",
  "confidence": 75.5,
  "model_used": "prophet",
  "generated_at": "2025-12-14T00:00:00.000Z"
}
```

---

### 3. Test Analytics (Airflow DAGs)

#### Check DAGs Status
```bash
cd /home/thiru/belly/belly/airflow
docker exec belly-airflow-scheduler airflow dags list
```

Expected output:
```
dag_id                   | filepath          | owner      | paused
=========================+===================+============+=======
price_prediction_nightly | prediction_dag.py | belly-team | False 
stats_computation_24h    | stats_dag.py      | belly-team | False
```

#### Manually Trigger Stats DAG
```bash
docker exec belly-airflow-scheduler airflow dags trigger stats_computation_24h
```

#### Check DAG Run Status
```bash
docker exec belly-airflow-scheduler airflow dags list-runs -d stats_computation_24h --limit 5
```

#### View Task Logs
```bash
# Scheduler logs
docker logs belly-airflow-scheduler -f

# Or via UI
# Go to http://localhost:8080
# Click on DAG → Graph → Click task → View Logs
```

---

### 4. Test Predictions (ML Model)

#### Trigger Prediction DAG
```bash
docker exec belly-airflow-scheduler airflow dags trigger price_prediction_nightly
```

#### Check if Prophet is Working
```bash
docker exec belly-airflow-scheduler python3 -c "
import prophet
print('✅ Prophet installed successfully')
print(f'Version: {prophet.__version__}')
"
```

#### Test Prediction Task Directly
```bash
docker exec belly-airflow-scheduler airflow tasks test price_prediction_nightly train_prophet_model 2025-12-14
```

---

### 5. Test Database Layer

#### Check Supabase Connection
```bash
# If you have psql installed
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM price_history;"
```

#### Check via API
```bash
# Get latest prices
curl "http://localhost:8000/latest/10" | jq

# Get price range
curl "http://localhost:8000/price-range?start_date=2025-12-01&end_date=2025-12-14" | jq
```

---

### 6. Test Streaming Layer

If you have Redpanda/Kafka running:

#### Check Producer (Price Fetcher)
```bash
cd /home/thiru/belly/belly/streaming

# Run producer manually
python3 producer.py
```

#### Check Consumer (Database Writer)
```bash
cd /home/thiru/belly/belly/streaming

# Run consumer manually
python3 consumer.py
```

#### Check Kafka Topics
```bash
# If Redpanda is running
docker exec -it redpanda rpk topic list
docker exec -it redpanda rpk topic consume beldex-prices --num 5
```

---

### 7. Test Presentation Layer

#### Start Reflex UI
```bash
cd /home/thiru/belly
source env/bin/activate
reflex run
```

Then visit: http://localhost:3000

#### Test UI Components
1. **Dashboard** - Should show current price
2. **Chart** - Should display price history graph
3. **Stats Panel** - Should show 24h/7d/30d statistics
4. **Predictions** - Should show ML forecasts

---

## Integration Testing

### Full Pipeline Test

1. **Generate Test Data** (if no real data)
```bash
# Insert sample price data
curl -X POST http://localhost:8000/test/generate-data
```

2. **Trigger Analytics**
```bash
docker exec belly-airflow-scheduler airflow dags trigger stats_computation_24h
```

3. **Wait for Completion** (check logs)
```bash
docker logs belly-airflow-scheduler -f | grep "stats_computation_24h"
```

4. **Verify Results**
```bash
# Check stats endpoint
curl "http://localhost:8000/stats?period=24h" | jq

# Should return computed values, not zeros
```

5. **Trigger Predictions**
```bash
docker exec belly-airflow-scheduler airflow dags trigger price_prediction_nightly
```

6. **Verify Predictions**
```bash
curl http://localhost:8000/predict | jq

# Should return model predictions
```

---

## Performance Testing

### Load Test API
```bash
# Install hey (HTTP load testing tool)
# sudo apt install hey

# Test current price endpoint
hey -n 1000 -c 10 http://localhost:8000/current-price

# Test stats endpoint
hey -n 500 -c 5 "http://localhost:8000/stats?period=24h"
```

### Monitor Resource Usage
```bash
# Docker stats
docker stats

# Airflow scheduler CPU/Memory
docker stats belly-airflow-scheduler
```

---

## Troubleshooting

### Issue: API Returns 503 (Service Unavailable)

**Cause:** Database or Redis not connected

**Fix:**
```bash
# Check Redis
docker ps | grep redis
docker logs belly-redis

# Restart API
./start_api.sh
```

### Issue: No Price Data

**Cause:** CoinGecko API rate limited or network issue

**Fix:**
```bash
# Test CoinGecko directly
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=beldex&vs_currencies=inr,usd"

# If rate limited, wait 60 seconds
```

### Issue: DAGs Not Executing

**Cause:** Scheduler not running or DAG paused

**Fix:**
```bash
# Check scheduler
docker logs belly-airflow-scheduler -f

# Unpause DAG
docker exec belly-airflow-scheduler airflow dags unpause stats_computation_24h
```

### Issue: Predictions Return 0

**Cause:** Not enough historical data or Prophet failed

**Fix:**
```bash
# Check if Prophet is installed
docker exec belly-airflow-scheduler python3 -c "import prophet"

# Check prediction logs
docker logs belly-airflow-scheduler | grep "prophet\|prediction"

# View task logs in UI
# http://localhost:8080 → prediction_dag → train_prophet_model → Logs
```

---

## Expected Test Results

After running `./test_complete_system.sh`, you should see:

```
════════════════════════════════════════════════════════════
  TEST SUMMARY
════════════════════════════════════════════════════════════

Total Tests:  35
Passed:       35
Failed:       0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎉 ALL TESTS PASSED! 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Streaming Layer: Ready
✅ Database Layer: Connected
✅ API Layer: Functional
✅ Analytics: Working
✅ Predictions: Available
✅ Airflow: Orchestrating
```

---

## CI/CD Testing

Add to your CI pipeline:

```yaml
# .github/workflows/test.yml
name: Belly System Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start services
        run: |
          cd belly/airflow
          docker-compose -f docker-compose.sqlite.yml up -d
      - name: Run tests
        run: |
          chmod +x test_complete_system.sh
          ./test_complete_system.sh
```

---

## Checklist

Use this before deployment:

- [ ] All Docker containers running
- [ ] Airflow UI accessible (localhost:8080)
- [ ] Both DAGs detected and not paused
- [ ] API health check returns "healthy"
- [ ] Current price endpoint returns data
- [ ] Stats endpoint returns computed values
- [ ] Predictions endpoint returns model forecasts
- [ ] CoinGecko API accessible
- [ ] Database tables exist and queryable
- [ ] Reflex UI loads without errors
- [ ] Complete test script passes all tests

---

**Version:** 1.0  
**Last Updated:** December 14, 2025
