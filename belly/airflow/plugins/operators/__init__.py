"""
Custom operators for Belly Airflow DAGs.
"""
# Don't import here - let Airflow load them directly
# Relative imports don't work when plugins are loaded as modules

__all__ = ["StatsOperator", "PredictionOperator"]
