"""
Stats DAG - Computes price statistics every 24 hours.

Schedule: Every 24 hours at 00:00 UTC
Tasks:
  1. check_price_data - Verify price history exists
  2. compute_stats_24h - Compute stats for 24h period
  3. compute_stats_7d - Compute stats for 7d period
  4. compute_stats_30d - Compute stats for 30d period
  5. notify_completion - Send notification
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
import logging
import asyncio
import sys
import os

logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from zebra.services.db_service import DatabaseService

# Initialize database service
db_service = DatabaseService()

# DAG definition
default_args = {
    'owner': 'belly-team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 12, 1),
    'email_on_failure': True,
    'email': ['alerts@belly.local'],
}

dag = DAG(
    'stats_computation_24h',
    default_args=default_args,
    description='Compute price statistics every 24 hours',
    schedule_interval='0 0 * * *',  # Every day at 00:00 UTC
    catchup=False,
    tags=['belly', 'stats', 'daily']
)

# Task functions
def check_price_data(**context):
    """Verify price history data exists."""
    logger.info("🔍 Checking price data availability...")
    
    async def check():
        await db_service.connect()
        prices = await db_service.get_price_history(days=1)
        await db_service.disconnect()
        
        if not prices:
            raise Exception("❌ No price data found for the last 24 hours")
        
        logger.info(f"✅ Found {len(prices)} price records")
        return len(prices)
    
    result = asyncio.run(check())
    context['task_instance'].xcom_push(key='price_count', value=result)
    return result


def compute_stats_24h(**context):
    """Compute statistics for 24h period."""
    logger.info("📊 Computing 24h statistics...")
    
    async def compute():
        await db_service.connect()
        
        # Fetch price history
        prices = await db_service.get_price_history(days=1)
        
        if not prices:
            logger.warning("⚠️ No price history found")
            return {}
        
        # Extract price values
        price_values = [float(p["price"]) for p in prices]
        
        # Compute statistics
        high = max(price_values)
        low = min(price_values)
        average = sum(price_values) / len(price_values)
        variance = sum((x - average) ** 2 for x in price_values) / len(price_values)
        volatility = variance ** 0.5
        
        # Store in database
        await db_service.insert_stats(
            period='24h',
            high=high,
            low=low,
            average=average,
            volatility=volatility
        )
        
        await db_service.disconnect()
        
        result = {
            "period": "24h",
            "high": round(high, 4),
            "low": round(low, 4),
            "average": round(average, 4),
            "volatility": round(volatility, 4)
        }
        
        logger.info(f"✅ 24h stats computed: {result}")
        return result
    
    result = asyncio.run(compute())
    context['task_instance'].xcom_push(key='stats_24h', value=result)
    return result


def compute_stats_7d(**context):
    """Compute statistics for 7d period."""
    logger.info("📊 Computing 7d statistics...")
    
    async def compute():
        await db_service.connect()
        
        # Fetch price history
        prices = await db_service.get_price_history(days=7)
        
        if not prices:
            logger.warning("⚠️ No price history found")
            return {}
        
        # Extract price values
        price_values = [float(p["price"]) for p in prices]
        
        # Compute statistics
        high = max(price_values)
        low = min(price_values)
        average = sum(price_values) / len(price_values)
        variance = sum((x - average) ** 2 for x in price_values) / len(price_values)
        volatility = variance ** 0.5
        
        # Store in database
        await db_service.insert_stats(
            period='7d',
            high=high,
            low=low,
            average=average,
            volatility=volatility
        )
        
        await db_service.disconnect()
        
        result = {
            "period": "7d",
            "high": round(high, 4),
            "low": round(low, 4),
            "average": round(average, 4),
            "volatility": round(volatility, 4)
        }
        
        logger.info(f"✅ 7d stats computed: {result}")
        return result
    
    result = asyncio.run(compute())
    context['task_instance'].xcom_push(key='stats_7d', value=result)
    return result


def compute_stats_30d(**context):
    """Compute statistics for 30d period."""
    logger.info("📊 Computing 30d statistics...")
    
    async def compute():
        await db_service.connect()
        
        # Fetch price history
        prices = await db_service.get_price_history(days=30)
        
        if not prices:
            logger.warning("⚠️ No price history found")
            return {}
        
        # Extract price values
        price_values = [float(p["price"]) for p in prices]
        
        # Compute statistics
        high = max(price_values)
        low = min(price_values)
        average = sum(price_values) / len(price_values)
        variance = sum((x - average) ** 2 for x in price_values) / len(price_values)
        volatility = variance ** 0.5
        
        # Store in database
        await db_service.insert_stats(
            period='30d',
            high=high,
            low=low,
            average=average,
            volatility=volatility
        )
        
        await db_service.disconnect()
        
        result = {
            "period": "30d",
            "high": round(high, 4),
            "low": round(low, 4),
            "average": round(average, 4),
            "volatility": round(volatility, 4)
        }
        
        logger.info(f"✅ 30d stats computed: {result}")
        return result
    
    result = asyncio.run(compute())
    context['task_instance'].xcom_push(key='stats_30d', value=result)
    return result


def notify_completion(**context):
    """Send completion notification."""
    task_instance = context['task_instance']
    
    stats_24h = task_instance.xcom_pull(task_ids='compute_stats_24h', key='stats_24h')
    stats_7d = task_instance.xcom_pull(task_ids='compute_stats_7d', key='stats_7d')
    stats_30d = task_instance.xcom_pull(task_ids='compute_stats_30d', key='stats_30d')
    
    logger.info("✅ Stats computation DAG completed successfully")
    logger.info(f"📊 24h Stats: {stats_24h}")
    logger.info(f"📊 7d Stats: {stats_7d}")
    logger.info(f"📊 30d Stats: {stats_30d}")


# Define tasks
start = DummyOperator(task_id='start', dag=dag)

check_data = PythonOperator(
    task_id='check_price_data',
    python_callable=check_price_data,
    provide_context=True,
    dag=dag
)

compute_24h = PythonOperator(
    task_id='compute_stats_24h',
    python_callable=compute_stats_24h,
    provide_context=True,
    dag=dag
)

compute_7d = PythonOperator(
    task_id='compute_stats_7d',
    python_callable=compute_stats_7d,
    provide_context=True,
    dag=dag
)

compute_30d = PythonOperator(
    task_id='compute_stats_30d',
    python_callable=compute_stats_30d,
    provide_context=True,
    dag=dag
)

notify = PythonOperator(
    task_id='notify_completion',
    python_callable=notify_completion,
    provide_context=True,
    dag=dag
)

end = DummyOperator(task_id='end', dag=dag)

# Define dependencies
start >> check_data
check_data >> [compute_24h, compute_7d, compute_30d]
[compute_24h, compute_7d, compute_30d] >> notify >> end
