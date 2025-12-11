# Airflow Setup for Belly Monitoring

## Overview

Apache Airflow orchestrates scheduled workflows for:
- **Stats DAG**: Computes price statistics every 24 hours
- **Prediction DAG**: Generates price predictions every night

## Directory Structure

```
airflow/
├── dags/
│   ├── __init__.py
│   ├── stats_dag.py          # Stats computation DAG (runs every 24h)
│   └── prediction_dag.py      # Prediction generation DAG (runs nightly)
├── plugins/
│   ├── __init__.py
│   └── operators/
│       ├── __init__.py
│       ├── stats_operator.py      # Custom operator for stats
│       └── prediction_operator.py # Custom operator for predictions
├── airflow_config.py          # Airflow configuration
├── docker-compose.yml         # Docker Compose setup
├── Dockerfile.airflow         # Airflow image
└── README.md
```

## DAG Details

### 📊 Stats DAG (`stats_dag.py`)

**Schedule**: Every 24 hours at 00:00 UTC

**Tasks**:
1. `check_price_data` - Verify price history exists
2. `compute_stats_24h` - Compute stats for 24h period
3. `compute_stats_7d` - Compute stats for 7d period
4. `compute_stats_30d` - Compute stats for 30d period
5. `notify_completion` - Send completion notification

**Computed Metrics**:
- **High**: Maximum price in period
- **Low**: Minimum price in period
- **Average**: Mean price
- **Volatility**: Standard deviation of prices

**Data Flow**:
```
check_price_data → [compute_stats_24h, compute_stats_7d, compute_stats_30d] → notify_completion
```

### 🤖 Prediction DAG (`prediction_dag.py`)

**Schedule**: Every night at 22:00 UTC

**Tasks**:
1. `fetch_historical_data` - Fetch 30 days of price history
2. `train_prophet_model` - Train Prophet model and generate predictions
3. `evaluate_predictions` - Evaluate prediction accuracy
4. `store_predictions` - Store predictions in database
5. `notify_predictions` - Send prediction notifications

**Supported Models**:
- **Prophet** (default) - Time series forecasting with seasonality
- **ARIMA** - AutoRegressive Integrated Moving Average
- **LSTM** - Long Short-Term Memory neural network
- **Simple MA** - Fallback simple moving average

**Predictions Generated**:
- `prediction_1h` - Price prediction for next hour
- `prediction_24h` - Price prediction for next 24 hours
- `prediction_7d` - Price prediction for next 7 days
- `trend` - Market trend (BULLISH, BEARISH, NEUTRAL)
- `confidence` - Confidence score (0-1)

**Data Flow**:
```
fetch_historical_data → train_prophet_model → evaluate_predictions → store_predictions → notify_predictions
```

## Setup Instructions

### 1. Prerequisites

Ensure you have:
- Docker and Docker Compose installed
- Python 3.11+
- PostgreSQL (via Docker)
- Redis (via Docker)

### 2. Environment Configuration

Create `.env` file in the project root:

```bash
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=belly

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Airflow
AIRFLOW_USERNAME=admin
AIRFLOW_PASSWORD=admin123
AIRFLOW_EMAIL=admin@belly.local

# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/belly

# Redis
REDIS_URL=redis://redis:6379/0

# Prediction
PREDICTION_MODEL=prophet
PREDICTION_LOOKBACK_DAYS=30
```

### 3. Start Services

```bash
# Navigate to airflow directory
cd belly/airflow

# Start all services
docker-compose up -d

# Initialize Airflow database
docker-compose exec airflow-webserver airflow db init

# Create admin user (if not auto-created)
docker-compose exec airflow-webserver airflow users create \
  --username admin \
  --firstname Belly \
  --lastname Admin \
  --role Admin \
  --email admin@belly.local \
  --password admin123
```

### 4. Access Airflow UI

- **URL**: `http://localhost:8080`
- **Username**: `admin`
- **Password**: `admin123`

### 5. Trigger DAGs

```bash
# Trigger stats DAG
docker-compose exec airflow-webserver airflow dags trigger stats_computation_24h

# Trigger prediction DAG
docker-compose exec airflow-webserver airflow dags trigger price_prediction_nightly

# List all DAGs
docker-compose exec airflow-webserver airflow dags list
```

## Monitoring

### Check DAG Execution

```bash
# List DAG runs
docker-compose exec airflow-webserver airflow dags list-runs -d stats_computation_24h

# Check task status
docker-compose exec airflow-webserver airflow tasks list stats_computation_24h

# View logs
docker logs belly-airflow-scheduler | tail -100
```

### Check Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d belly

# Check tables
\dt

# View latest stats
SELECT * FROM stats ORDER BY computed_at DESC LIMIT 5;

# View latest predictions
SELECT * FROM predictions ORDER BY generated_at DESC LIMIT 5;
```

### Check Redis

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# List keys
KEYS belly:*

# Get current price
GET belly:current
```

## Custom Operators

### StatsOperator

Computes price statistics from historical data.

```python
from airflow.operators.python import PythonOperator

stats_task = PythonOperator(
    task_id='compute_stats',
    python_callable=compute_stats,
    op_kwargs={
        'db_service': db_service,
        'period': '24h'
    }
)
```

### PredictionOperator

Generates price predictions using ML models.

```python
from airflow.operators.python import PythonOperator

prediction_task = PythonOperator(
    task_id='generate_predictions',
    python_callable=generate_predictions,
    op_kwargs={
        'db_service': db_service,
        'model_type': 'prophet',
        'lookback_days': 30
    }
)
```

## Troubleshooting

### Airflow Scheduler Not Starting

```bash
# Check logs
docker logs belly-airflow-scheduler

# Restart scheduler
docker-compose restart airflow-scheduler
```

### Database Connection Issues

```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready

# Test connection
docker-compose exec postgres psql -U postgres -d belly -c "SELECT 1"
```

### Redis Connection Issues

```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Test connection
docker-compose exec redis redis-cli -h redis ping
```

### Model Training Failures

- Check if required libraries are installed (prophet, statsmodels, tensorflow)
- Verify sufficient historical data exists
- Check logs for specific errors

## Performance Optimization

### Increase Parallelization

Edit `docker-compose.yml`:

```yaml
airflow-worker:
  command: airflow celery worker --concurrency=8  # Increase from 4
```

### Adjust Scheduler Settings

Edit `airflow_config.py`:

```python
AIRFLOW__SCHEDULER__CATCHUP_BY_DEFAULT = True
AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL = 60  # Faster DAG discovery
```

### Database Optimization

Add indexes in PostgreSQL:

```sql
CREATE INDEX idx_stats_computed_at ON stats(computed_at DESC);
CREATE INDEX idx_predictions_generated_at ON predictions(generated_at DESC);
```

## Maintenance

### Backup Database

```bash
docker-compose exec postgres pg_dump -U postgres -d belly > belly_backup.sql
```

### Clean Old Logs

```bash
# Airflow logs older than 30 days
docker-compose exec airflow-webserver airflow db clean --db-cleanup-max-db-entry-age-in-days 30
```

### Stop Services

```bash
docker-compose down

# Remove volumes (careful - deletes data)
docker-compose down -v
```

## Next Steps

1. Configure SMTP for email notifications
2. Set up monitoring/alerting (Grafana, Prometheus)
3. Implement custom hooks for data validation
4. Add more sophisticated models (XGBoost, Random Forest)
5. Implement model versioning and A/B testing

## References

- [Apache Airflow Documentation](https://airflow.apache.org/)
- [Prophet Documentation](https://facebook.github.io/prophet/)
- [AsyncPG Documentation](https://magicstack.github.io/asyncpg/)
- [Redis Documentation](https://redis.io/)
