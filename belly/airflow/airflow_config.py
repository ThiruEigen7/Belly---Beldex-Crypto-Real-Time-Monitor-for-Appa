"""
Airflow configuration for Belly monitoring system.
Supports local Docker deployment.
"""
import os
from datetime import timedelta

# Airflow Home
AIRFLOW_HOME = os.path.expanduser("~/airflow")

# Core configuration
AIRFLOW__CORE__DAGS_FOLDER = os.path.join(os.path.dirname(__file__), 'dags')
AIRFLOW__CORE__PLUGINS_FOLDER = os.path.join(os.path.dirname(__file__), 'plugins')
AIRFLOW__CORE__EXECUTOR = 'LocalExecutor'
AIRFLOW__CORE__SQL_ALCHEMY_CONN = os.getenv(
    'AIRFLOW_SQL_ALCHEMY_CONN',
    'postgresql://postgres:postgres@localhost:5432/airflow'
)

# Load examples
AIRFLOW__CORE__LOAD_EXAMPLES = False

# Logging
AIRFLOW__LOGGING__BASE_LOG_FOLDER = '/var/log/airflow'

# Security
AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS = False

# DAG configuration
AIRFLOW__CORE__DAG_ORIENTATION = 'LR'
AIRFLOW__SCHEDULER__CATCHUP_BY_DEFAULT = False
AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL = 300

# Email configuration (update as needed)
AIRFLOW__SMTP__SMTP_HOST = os.getenv('SMTP_HOST', 'localhost')
AIRFLOW__SMTP__SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
AIRFLOW__SMTP__SMTP_USER = os.getenv('SMTP_USER', '')
AIRFLOW__SMTP__SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
AIRFLOW__SMTP__SMTP_MAIL_FROM = os.getenv('SMTP_MAIL_FROM', 'airflow@belly.local')

# Webserver
AIRFLOW__WEBSERVER__WEB_SERVER_PORT = 8080
AIRFLOW__WEBSERVER__EXPOSE_CONFIG = True

# Connection strings from environment
AIRFLOW__CONNECTIONS__DATABASE_CONN = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@postgres:5432/belly'
)

AIRFLOW__CONNECTIONS__REDIS_CONN = os.getenv(
    'REDIS_URL',
    'redis://redis:6379/0'
)

# Default task retry configuration
AIRFLOW__CORE__DEFAULT_TASK_RETRIES = 2
AIRFLOW__CORE__DEFAULT_TASK_RETRY_DELAY = 300  # 5 minutes

# Worker configuration (for distributed execution)
AIRFLOW__CELERY__BROKER_URL = os.getenv(
    'CELERY_BROKER_URL',
    'redis://redis:6379/0'
)
AIRFLOW__CELERY__RESULT_BACKEND = os.getenv(
    'CELERY_RESULT_BACKEND',
    'redis://redis:6379/0'
)

# Enable API
AIRFLOW__API__AUTH_BACKEND = 'airflow.api.auth.backend.basic_auth'

# Custom Belly configuration - Using Cloud Services
BELLY_SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://bcioieesyhilfrfgogpq.supabase.co')
BELLY_SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY', '')

BELLY_REDIS_URL = os.getenv('REDIS_URL', '')
BELLY_REDIS_TOKEN = os.getenv('REDIS_TOKEN', '')

# Kafka/Redpanda configuration
BELLY_KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', '')
BELLY_KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'belly-price')

# Prediction configuration
BELLY_PREDICTION_MODEL = os.getenv('PREDICTION_MODEL', 'prophet')
BELLY_PREDICTION_LOOKBACK_DAYS = int(os.getenv('PREDICTION_LOOKBACK_DAYS', 30))
