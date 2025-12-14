#!/bin/bash
set -e

# Create logs directory - will be created in /home/airflow by volume mount
mkdir -p /home/airflow/logs/scheduler /home/airflow/logs/dag_processor_manager /home/airflow/logs/dag_runs 2>/dev/null || true

echo "🚀 Initializing Airflow database..."
airflow db init 2>&1 | head -20

echo "👤 Creating admin user..."
airflow users create --username admin --password admin123 --firstname Admin --lastname User --role Admin --email admin@belly.local 2>/dev/null || echo "   User already exists"

echo "📊 Starting webserver on port 8080..."
exec airflow webserver --port 8080
