"""
Custom operator for computing price statistics.
Computes high, low, average, and volatility for the last 24 hours.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

logger = logging.getLogger(__name__)


class StatsOperator(BaseOperator):
    """
    Operator for computing price statistics from price history.
    
    Attributes:
        db_service: Database service instance for fetching and storing data
        period: Statistics period (e.g., "24h", "7d", "30d")
    """
    
    @apply_defaults
    def __init__(self, db_service=None, period: str = "24h", *args, **kwargs):
        """
        Initialize the stats operator.
        
        Args:
            db_service: Database service instance
            period: Statistics period
        """
        super().__init__(*args, **kwargs)
        self.db_service = db_service
        self.period = period
    
    def execute(self, context):
        """
        Execute stats computation.
        
        Args:
            context: Airflow context
            
        Returns:
            Dictionary containing computed statistics
        """
        import asyncio
        
        logger.info(f"📊 Computing statistics for period: {self.period}")
        
        try:
            # Run async operation
            stats = asyncio.run(self._compute_stats())
            logger.info(f"✅ Statistics computed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error computing statistics: {str(e)}")
            raise
    
    async def _compute_stats(self) -> Dict[str, Any]:
        """
        Compute statistics from price history.
        
        Returns:
            Dictionary containing high, low, average, volatility
        """
        if not self.db_service:
            logger.error("❌ Database service not configured")
            return {}
        
        try:
            # Determine days based on period
            days_map = {"24h": 1, "7d": 7, "30d": 30}
            days = days_map.get(self.period, 1)
            
            # Fetch price history
            prices = await self.db_service.get_price_history(days=days)
            
            if not prices:
                logger.warning(f"⚠️ No price history found for period: {self.period}")
                return {}
            
            # Extract price values
            price_values = [float(p["price"]) for p in prices]
            
            # Compute statistics
            high = max(price_values)
            low = min(price_values)
            average = sum(price_values) / len(price_values)
            
            # Compute volatility (standard deviation)
            variance = sum((x - average) ** 2 for x in price_values) / len(price_values)
            volatility = variance ** 0.5
            
            stats = {
                "period": self.period,
                "high": round(high, 4),
                "low": round(low, 4),
                "average": round(average, 4),
                "volatility": round(volatility, 4),
                "computed_at": datetime.utcnow().isoformat()
            }
            
            # Store in database
            await self.db_service.insert_stats(
                period=self.period,
                high=high,
                low=low,
                average=average,
                volatility=volatility
            )
            
            logger.info(f"✅ Stats stored in database: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error in _compute_stats: {str(e)}")
            raise
