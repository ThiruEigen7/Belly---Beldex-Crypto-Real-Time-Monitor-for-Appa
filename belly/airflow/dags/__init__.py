"""
Airflow DAG initialization module.
"""
import os

# Set AIRFLOW_HOME if not already set
if 'AIRFLOW_HOME' not in os.environ:
    os.environ['AIRFLOW_HOME'] = os.path.expanduser('~/airflow')
