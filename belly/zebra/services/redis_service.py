"""
Redis service for hot data caching (Upstash)
Provides caching layer for real-time price data and stats
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import asyncio

from upstash_redis import Redis

logger = logging.getLogger(__name__)


class RedisService:
    """
    Service for interacting with Redis cache (Upstash).
    
    Features:
    - Hot data caching (current price)
    - Stats caching
    - Automatic TTL management
    - Connection pooling
    - Graceful degradation
    - Retry logic
    """
    
    def __init__(self):
        """Initialize Redis connection configuration."""
        self.redis_url = os.getenv("REDIS_URL")
        self.redis_token = os.getenv("REDIS_TOKEN")

        if not self.redis_url or not self.redis_token:
            raise ValueError("REDIS_URL and REDIS_TOKEN must be set in the environment variables.")

        self.client = Redis(url=self.redis_url, token=self.redis_token)
        self.key_prefix = "belly:"
        self.connected = True  # upstash-redis handles connection internally

        # TTL defaults (in seconds)
        self.ttl_current_price = 900  # 15 minutes
        self.ttl_stats = 3600  # 1 hour
        self.ttl_predictions = 7200  # 2 hours
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    async def connect(self):
        """
        Establish Redis connection with retry logic.
        
        Raises:
            Exception: If Redis library not installed
        """
        for attempt in range(self.max_retries):
            try:
                # Test connection
                self.client.ping()
                self.connected = True
                logger.info(f"✅ Redis connected successfully (attempt {attempt + 1})")
                return
                
            except Exception as e:
                logger.warning(
                    f"⚠️ Redis connection attempt {attempt + 1}/{self.max_retries} failed: {str(e)}"
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("❌ Redis connection failed after all retries")
                    self.connected = False
                    
            except Exception as e:
                logger.error(f"❌ Unexpected error connecting to Redis: {str(e)}")
                self.connected = False
                break
    
    async def disconnect(self):
        """Close Redis connection gracefully."""
        try:
            # upstash-redis doesn't require explicit close
            self.connected = False
            logger.info("✅ Redis connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing Redis connection: {str(e)}")
    
    async def ping(self) -> bool:
        """
        Check if Redis is reachable.
        
        Returns:
            bool: True if Redis responds, False otherwise
        """
        try:
            result = self.client.ping()
            return result
        except Exception as e:
            logger.warning(f"⚠️ Redis ping failed: {str(e)}")
            return False
    
    async def _safe_get(self, key: str) -> Optional[str]:
        """
        Safely get value from Redis with error handling.
        
        Args:
            key: Redis key to fetch
            
        Returns:
            Value as string or None if error/not found
        """
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"❌ Redis GET error for key '{key}': {str(e)}")
            return None
    
    async def _safe_set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Safely set value in Redis with error handling.
        
        Args:
            key: Redis key
            value: Value to store
            ttl: Time to live in seconds (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if ttl:
                self.client.set(key, value, ex=ttl)
            else:
                self.client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"❌ Redis SET error for key '{key}': {str(e)}")
            return False
    
    # ==================== Current Price Methods ====================
    
    async def get_current_price(self) -> Optional[Dict[str, Any]]:
        """
        Get current Beldex price from Redis.
        
        Returns:
            Dict with price_inr, price_usd, timestamp, source or None
            
        Example:
            {
                "price_inr": 35.50,
                "price_usd": 0.43,
                "timestamp": "2024-12-07T10:30:00",
                "source": "redis"
            }
        """
        key = f"{self.key_prefix}current"
        data = await self._safe_get(key)
        
        if data:
            try:
                price_data = json.loads(data)
                return {
                    "price_inr": float(price_data["price_inr"]),
                    "price_usd": float(price_data["price_usd"]),
                    "timestamp": price_data["timestamp"],
                    "source": price_data["source"]
                }
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"❌ Error decoding current price data: {str(e)}")
        return None

    async def set_current_price(
        self,
        price_inr: float,
        price_usd: float,
        timestamp: str
    ) -> bool:
        """
        Set current Beldex price in Redis.

        Args:
            price_inr: Price in INR.
            price_usd: Price in USD.
            timestamp: ISO 8601 timestamp.

        Returns:
            True if successful, False otherwise.
        """
        key = f"{self.key_prefix}current"
        value = json.dumps({
            "price_inr": price_inr,
            "price_usd": price_usd,
            "timestamp": timestamp,
            "source": "redis"
        })
        return await self._safe_set(key, value, self.ttl_current_price)
    
    # ==================== Stats Methods ====================
    
    async def get_stats_cache(self, period: str = "24h") -> Optional[Dict[str, Any]]:
        """
        Get cached market stats for a period.
        
        Args:
            period: Time period (24h, 7d, 30d)
            
        Returns:
            Dict with high, low, average, volatility or None
        """
        key = f"{self.key_prefix}stats:{period}"
        data = await self._safe_get(key)
        
        if data:
            try:
                stats = json.loads(data)
                logger.info(f"✅ Stats fetched from Redis for period: {period}")
                return stats
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON in Redis for stats: {str(e)}")
                return None
        
        logger.debug(f"⚠️ Stats not found in Redis for period: {period}")
        return None
    
    async def set_stats_cache(
        self,
        period: str,
        high: float,
        low: float,
        average: float,
        volatility: float,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache market stats for a period.
        
        Args:
            period: Time period (24h, 7d, 30d)
            high: Highest price
            low: Lowest price
            average: Average price
            volatility: Price volatility percentage
            ttl: Time to live in seconds (default: 1 hour)
            
        Returns:
            True if successful
        """
        key = f"{self.key_prefix}stats:{period}"
        
        data = {
            "period": period,
            "high": round(high, 4),
            "low": round(low, 4),
            "average": round(average, 4),
            "volatility": round(volatility, 4),
            "computed_at": datetime.utcnow().isoformat()
        }
        
        ttl = ttl or self.ttl_stats
        success = await self._safe_set(key, json.dumps(data), ttl)
        
        if success:
            logger.info(f"✅ Stats cached for period: {period}")
        
        return success
    
    # ==================== Predictions Methods ====================
    
    async def get_predictions_cache(self) -> Optional[Dict[str, Any]]:
        """
        Get cached ML predictions.
        
        Returns:
            Dict with prediction_24h, prediction_7d, trend, confidence or None
        """
        key = f"{self.key_prefix}predictions"
        data = await self._safe_get(key)
        
        if data:
            try:
                predictions = json.loads(data)
                logger.info("✅ Predictions fetched from Redis")
                return predictions
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON in Redis for predictions: {str(e)}")
                return None
        
        logger.debug("⚠️ Predictions not found in Redis")
        return None
    
    async def set_predictions_cache(
        self,
        prediction_24h: float,
        prediction_7d: float,
        trend: str,
        confidence: float,
        model_used: str,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache ML predictions.
        
        Args:
            prediction_24h: 24-hour forecast
            prediction_7d: 7-day forecast
            trend: Trend direction (bullish/bearish/neutral)
            confidence: Model confidence (0-1)
            model_used: ML model name
            ttl: Time to live in seconds (default: 2 hours)
            
        Returns:
            True if successful
        """
        key = f"{self.key_prefix}predictions"
        
        data = {
            "prediction_24h": round(prediction_24h, 4),
            "prediction_7d": round(prediction_7d, 4),
            "trend": trend,
            "confidence": round(confidence, 4),
            "model_used": model_used,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        ttl = ttl or self.ttl_predictions
        success = await self._safe_set(key, json.dumps(data), ttl)
        
        if success:
            logger.info(f"✅ Predictions cached (model: {model_used})")
        
        return success
    
    async def set_stats(self, period: str, stats: Dict[str, float]) -> bool:
        """
        Set stats in Redis.

        Args:
            period: Time period (e.g., "24h").
            stats: Dictionary containing high, low, average, volatility.

        Returns:
            True if successful, False otherwise.
        """
        key = f"{self.key_prefix}stats:{period}"
        value = json.dumps(stats)
        return await self._safe_set(key, value, self.ttl_stats)

    async def get_stats(self, period: str) -> Optional[Dict[str, float]]:
        """
        Get stats from Redis.

        Args:
            period: Time period (e.g., "24h").

        Returns:
            Dictionary containing high, low, average, volatility or None.
        """
        key = f"{self.key_prefix}stats:{period}"
        data = await self._safe_get(key)

        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Error decoding stats data: {str(e)}")
        return None

    async def set_predictions(self, predictions: Dict[str, Any]) -> bool:
        """
        Set predictions in Redis.

        Args:
            predictions: Dictionary containing prediction_24h, prediction_7d, trend, confidence, model_used, generated_at.

        Returns:
            True if successful, False otherwise.
        """
        key = f"{self.key_prefix}predictions"
        value = json.dumps(predictions)
        return await self._safe_set(key, value, self.ttl_predictions)

    async def get_predictions(self) -> Optional[Dict[str, Any]]:
        """
        Get predictions from Redis.

        Returns:
            Dictionary containing prediction_24h, prediction_7d, trend, confidence, model_used, generated_at or None.
        """
        key = f"{self.key_prefix}predictions"
        data = await self._safe_get(key)

        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Error decoding predictions data: {str(e)}")
        return None
    
    # ==================== Utility Methods ====================
    
    async def clear_cache(self, pattern: str = "*") -> int:
        """
        Clear cache matching pattern.
        
        Args:
            pattern: Key pattern to match (e.g., "stats:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            full_pattern = f"{self.key_prefix}{pattern}"
            keys = await self.client.keys(full_pattern)
            
            if keys:
                count = await self.client.delete(*keys)
                logger.info(f"✅ Cleared {count} keys matching '{full_pattern}'")
                return count
            
            logger.info(f"No keys found matching '{full_pattern}'")
            return 0
            
        except Exception as e:
            logger.error(f"❌ Error clearing cache: {str(e)}")
            return 0
    
    async def get_all_keys(self) -> List[str]:
        """
        Get all keys with the belly: prefix.
        
        Returns:
            List of all keys
        """
        if not self.client:
            return []
        
        try:
            pattern = f"{self.key_prefix}*"
            keys = await self.client.keys(pattern)
            logger.info(f"✅ Found {len(keys)} keys in Redis")
            return keys
        except Exception as e:
            logger.error(f"❌ Error getting keys: {str(e)}")
            return []
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """
        Get TTL (time to live) for a key.
        
        Args:
            key: Redis key (without prefix)
            
        Returns:
            TTL in seconds, -1 if no expiry, -2 if key doesn't exist, None on error
        """
        if not self.client:
            return None
        
        try:
            full_key = f"{self.key_prefix}{key}"
            ttl = await self.client.ttl(full_key)
            return ttl
        except Exception as e:
            logger.error(f"❌ Error getting TTL: {str(e)}")
            return None
    
    async def set_custom_data(
        self,
        key: str,
        data: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set custom data in Redis.
        
        Args:
            key: Key name (prefix will be added)
            data: Any JSON-serializable data
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        full_key = f"{self.key_prefix}{key}"
        
        try:
            json_data = json.dumps(data)
            return await self._safe_set(full_key, json_data, ttl)
        except (TypeError, ValueError) as e:
            logger.error(f"❌ Data not JSON serializable: {str(e)}")
            return False
    
    async def get_custom_data(self, key: str) -> Optional[Any]:
        """
        Get custom data from Redis.
        
        Args:
            key: Key name (prefix will be added)
            
        Returns:
            Deserialized data or None
        """
        full_key = f"{self.key_prefix}{key}"
        data = await self._safe_get(full_key)
        
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data  # Return as string if not JSON
        
        return None
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for Redis.
        
        Returns:
            Dict with connection status, memory info, key count
        """
        if not self.client:
            return {
                "connected": False,
                "error": "Redis client not initialized"
            }
        
        try:
            # Ping test
            ping_result = await self.ping()
            
            if not ping_result:
                return {
                    "connected": False,
                    "error": "Redis not responding to ping"
                }
            
            # Get info
            info = await self.client.info()
            
            # Count keys
            keys = await self.get_all_keys()
            
            return {
                "connected": True,
                "memory_used": info.get("used_memory_human", "N/A"),
                "uptime_seconds": info.get("uptime_in_seconds", 0),
                "connected_clients": info.get("connected_clients", 0),
                "total_keys": len(keys),
                "version": info.get("redis_version", "unknown")
            }
            
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }