# Airflow Orchestration System

Complete Apache Airflow setup for Belly price monitoring and prediction pipeline.

## Quick Start (30 seconds)

```bash
cd /home/thiru/belly/belly/airflow

# Start services
docker-compose -f docker-compose.sqlite.yml up -d

# Wait for startup
sleep 40

# Access UI
# Open: http://localhost:8080
# Login: admin / admin123
```

## Architecture

- **Scheduler**: Detects and schedules DAGs
- **Webserver**: Web UI on port 8080
- **Redis**: Cache & message broker
- **SQLite**: Embedded metadata database
- **Executor**: SequentialExecutor (single-threaded, required for SQLite)

## DAGs

### 1. Stats DAG (`stats_computation_24h`)
- **Schedule**: Daily at 00:00 UTC
- **Purpose**: Compute price statistics
- **Tasks**: 
  - check_price_data → compute_stats_24h/7d/30d → notify_completion
- **Output**: High, Low, Average, Volatility metrics

### 2. Prediction DAG (`price_prediction_nightly`)
- **Schedule**: Daily at 22:00 UTC  
- **Purpose**: Generate ML forecasts
- **Tasks**:
  - fetch_historical_data → train_prophet_model → evaluate_predictions → store_predictions → notify_predictions
- **Model**: Prophet time series forecasting
- **Output**: 24h, 7d, 30d price predictions with confidence scores

## Commands

### Start/Stop

```bash
# Start
docker-compose -f docker-compose.sqlite.yml up -d

# Stop
docker-compose -f docker-compose.sqlite.yml down

# Restart
docker-compose -f docker-compose.sqlite.yml restart
```

### Logs

```bash
# Scheduler
docker logs belly-airflow-scheduler -f

# Webserver  
docker logs belly-airflow-webserver -f

# Redis
docker logs belly-redis -f
```

### CLI Commands

```bash
# List DAGs
docker exec belly-airflow-scheduler airflow dags list

# List recent runs
docker exec belly-airflow-scheduler airflow dags list-runs -d stats_computation_24h

# Trigger DAG manually
docker exec belly-airflow-scheduler airflow dags trigger stats_computation_24h
```

## Access Points

- **Webserver**: http://localhost:8080 (admin/admin123)
- **Redis**: localhost:6379

## Database

- **Type**: SQLite
- **Location**: `/home/airflow/airflow.db` (in container)
- **Auto-created**: Yes

Check contents:
```bash
docker exec belly-airflow-scheduler sqlite3 /home/airflow/airflow.db \
  "SELECT dag_id FROM dag;"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| DAGs not showing | Hard refresh browser (Ctrl+Shift+R), click "All" tab |
| Login fails | Default: admin/admin123 |
| Webserver down | `docker logs belly-airflow-webserver` |
| DAGs not detected | `docker logs belly-airflow-scheduler \| grep -i dag` |

## Files

- `docker-compose.sqlite.yml` - Docker setup
- `Dockerfile.airflow.nodumb` - Image definition
- `start-scheduler.sh` - Scheduler startup
- `start-webserver.sh` - Webserver startup
- `dags/` - DAG definitions
- `plugins/` - Custom operators
- `logs/` - Execution logs

## Next Steps

1. Open http://localhost:8080
2. Login with admin/admin123
3. Click "All" to see DAGs
4. Toggle DAGs to enable execution
5. Monitor logs in "Log" section

## Technology

- Apache Airflow 2.7.3
- Python 3.11
- SQLite (dev/test)
- Redis 7
- Prophet ML library
