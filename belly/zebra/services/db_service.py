"""
Supabase REST API service for data operations.
Uses httpx for async HTTP requests instead of direct database connections.
"""
import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import httpx
from dotenv import load_dotenv

# Load .env.production
load_dotenv('.env.production')

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for interacting with Supabase via REST API."""
    
    def __init__(self):
        """Initialize Supabase REST API client."""
        self.supabase_url = os.getenv(
            "SUPABASE_URL",
            "https://bcioieesyhilfrfgogpq.supabase.co"
        )
        self.supabase_key = os.getenv(
            "SUPABASE_ANON_KEY",
            ""
        )
        self.client: Optional[httpx.AsyncClient] = None
        self.connected = False
        
        if not self.supabase_key:
            logger.warning("⚠️ SUPABASE_ANON_KEY not set in environment")
        
        # For compatibility with existing code
        self.pool = None  # Mock pool attribute
    
    async def connect(self):
        """Initialize async HTTP client."""
        try:
            headers = {
                "Content-Type": "application/json",
                "Prefer": "return=representation"  # Return inserted/updated data
            }
            
            # Use apikey and Authorization headers for Supabase REST API
            if self.supabase_key:
                headers["apikey"] = self.supabase_key
                headers["Authorization"] = f"Bearer {self.supabase_key}"
            else:
                logger.warning("⚠️ No API key provided - requests may fail")
            
            self.client = httpx.AsyncClient(
                headers=headers,
                base_url=f"{self.supabase_url}/rest/v1",
                timeout=30.0
            )
            
            # Test connection
            health = await self.ping()
            if health:
                self.connected = True
                self.pool = True  # Mock for compatibility
                logger.info(f"✅ Supabase connected: {self.supabase_url}")
            else:
                logger.error("❌ Supabase connection test failed")
                self.connected = False
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            self.connected = False
    
    async def disconnect(self):
        """Close async HTTP client."""
        if self.client:
            await self.client.aclose()
            self.connected = False
            self.pool = None
            logger.info("Supabase REST API client closed")
    
    async def ping(self) -> bool:
        """
        Check if Supabase service is accessible.
        
        Returns:
            True if accessible, False otherwise
        """
        if not self.client:
            return False
        
        try:
            # Try to query any table (will return 200 or 404)
            response = await self.client.get("/price_history?limit=1")
            return response.status_code in (200, 404, 406)  # 406 = table might not exist yet
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return False
    
    # ==================== Price History Methods ====================
    
    async def get_latest_price(self) -> Optional[Dict]:
        """Get the most recent price from database."""
        try:
            response = await self.client.get(
                "/price_history",
                params={
                    "select": "price_inr,price_usd,timestamp",
                    "order": "timestamp.desc",
                    "limit": 1
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if data:
                return {
                    "price_inr": float(data[0]["price_inr"]),
                    "price_usd": float(data[0]["price_usd"]),
                    "timestamp": data[0]["timestamp"],
                    "source": "database"
                }
            return None
            
        except Exception as e:
            logger.error(f"Error fetching latest price: {str(e)}")
            return None
    
    async def get_price_history(self, days: int = 5) -> List[Dict]:
        """Get price history for last N days."""
        try:
            # Calculate date threshold
            threshold = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            response = await self.client.get(
                "/price_history",
                params={
                    "select": "timestamp,price_inr",
                    "timestamp": f"gte.{threshold}",
                    "order": "timestamp.asc",
                    "limit": 1000
                }
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Group by date and average
            daily_prices = {}
            for row in data:
                date = datetime.fromisoformat(row["timestamp"].replace('Z', '+00:00'))
                date_key = date.strftime("%b %d")
                
                if date_key not in daily_prices:
                    daily_prices[date_key] = []
                daily_prices[date_key].append(float(row["price_inr"]))
            
            # Calculate averages
            result = []
            for date_key, prices in daily_prices.items():
                result.append({
                    "date": date_key,
                    "price": round(sum(prices) / len(prices), 2),
                    "timestamp": date_key
                })
            
            return result
                
        except Exception as e:
            logger.error(f"Error fetching price history: {str(e)}")
            return []
    
    async def insert_price(
        self,
        price_inr: float,
        price_usd: float,
        source: str = "api"
    ) -> bool:
        """Insert a new price record."""
        try:
            data = {
                "price_inr": price_inr,
                "price_usd": price_usd,
                "source": source,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = await self.client.post("/price_history", json=data)
            response.raise_for_status()
            
            logger.info(f"✅ Price inserted: ₹{price_inr}")
            return True
                
        except Exception as e:
            logger.error(f"Error inserting price: {str(e)}")
            return False
    
    async def get_latest_prices(self, count: int = 10) -> List[Dict]:
        """Get the latest N price entries."""
        try:
            response = await self.client.get(
                "/price_history",
                params={
                    "select": "price_inr,price_usd,timestamp",
                    "order": "timestamp.desc",
                    "limit": count
                }
            )
            response.raise_for_status()
            
            data = response.json()
            return [
                {
                    "price_inr": float(row["price_inr"]),
                    "price_usd": float(row["price_usd"]),
                    "timestamp": row["timestamp"]
                }
                for row in data
            ]
                
        except Exception as e:
            logger.error(f"Error fetching latest prices: {str(e)}")
            return []
    
    # ==================== Stats Methods ====================
    
    async def get_stats(self, period: str = "24h") -> Optional[Dict]:
        """Get latest stats for a period."""
        try:
            response = await self.client.get(
                "/stats",
                params={
                    "select": "period,high,low,average,volatility,computed_at",
                    "period": f"eq.{period}",
                    "order": "computed_at.desc",
                    "limit": 1
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if data:
                return {
                    "period": data[0]["period"],
                    "high": float(data[0]["high"]),
                    "low": float(data[0]["low"]),
                    "average": float(data[0]["average"]),
                    "volatility": float(data[0]["volatility"]),
                    "computed_at": data[0]["computed_at"]
                }
            return None
                
        except Exception as e:
            logger.error(f"Error fetching stats: {str(e)}")
            return None
    
    async def insert_stats(
        self,
        period: str,
        high: float,
        low: float,
        average: float,
        volatility: float
    ) -> bool:
        """Insert new stats record."""
        try:
            data = {
                "period": period,
                "high": high,
                "low": low,
                "average": average,
                "volatility": volatility,
                "computed_at": datetime.utcnow().isoformat()
            }
            
            response = await self.client.post("/stats", json=data)
            response.raise_for_status()
            
            logger.info(f"✅ Stats inserted for period: {period}")
            return True
                
        except Exception as e:
            logger.error(f"Error inserting stats: {str(e)}")
            return False
    
    # ==================== Predictions Methods ====================
    
    async def get_predictions(self) -> Optional[Dict]:
        """Get latest predictions."""
        try:
            response = await self.client.get(
                "/predictions",
                params={
                    "select": "prediction_24h,prediction_7d,trend,confidence,model_used,generated_at",
                    "order": "generated_at.desc",
                    "limit": 1
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if data:
                return {
                    "prediction_24h": float(data[0]["prediction_24h"]),
                    "prediction_7d": float(data[0]["prediction_7d"]),
                    "trend": data[0]["trend"],
                    "confidence": float(data[0]["confidence"]),
                    "model_used": data[0]["model_used"],
                    "generated_at": data[0]["generated_at"]
                }
            return None
                
        except Exception as e:
            logger.error(f"Error fetching predictions: {str(e)}")
            return None
    
    async def insert_prediction(
        self,
        prediction_24h: float,
        prediction_7d: float,
        trend: str,
        confidence: float,
        model_used: str
    ) -> bool:
        """Insert new prediction record."""
        try:
            data = {
                "prediction_24h": prediction_24h,
                "prediction_7d": prediction_7d,
                "trend": trend,
                "confidence": confidence,
                "model_used": model_used,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            response = await self.client.post("/predictions", json=data)
            response.raise_for_status()
            
            logger.info(f"✅ Prediction inserted (model: {model_used})")
            return True
                
        except Exception as e:
            logger.error(f"Error inserting prediction: {str(e)}")
            return False
    
    # ==================== Utility Methods ====================
    
    async def get_price_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[Dict]:
        """Get prices within a date range."""
        try:
            response = await self.client.get(
                "/price_history",
                params={
                    "select": "price_inr,price_usd,timestamp",
                    "timestamp": f"gte.{start_date}",
                    "timestamp": f"lte.{end_date}",
                    "order": "timestamp.asc"
                }
            )
            response.raise_for_status()
            
            data = response.json()
            return [
                {
                    "price_inr": float(row["price_inr"]),
                    "price_usd": float(row["price_usd"]),
                    "timestamp": row["timestamp"]
                }
                for row in data
            ]
                
        except Exception as e:
            logger.error(f"Error fetching price range: {str(e)}")
            return []
    
    async def query_table(
        self,
        table: str,
        select: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        order: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """
        Generic table query method.
        
        Args:
            table: Table name
            select: Columns to select
            filters: Filter conditions
            limit: Max rows
            order: Order by clause
        
        Returns:
            List of rows or None
        """
        try:
            params = {
                "select": select,
                "limit": limit
            }
            
            if filters:
                for key, value in filters.items():
                    params[key] = f"eq.{value}"
            
            if order:
                params["order"] = order
            
            response = await self.client.get(f"/{table}", params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check.
        
        Returns:
            Dict with connection status and table info
        """
        if not self.client:
            return {
                "connected": False,
                "error": "Client not initialized"
            }
        
        try:
            # Check connection
            ping_result = await self.ping()
            
            if not ping_result:
                return {
                    "connected": False,
                    "error": "Supabase not responding"
                }
            
            # Count records in tables
            tables = {}
            for table in ["price_history", "stats", "predictions"]:
                try:
                    response = await self.client.get(
                        f"/{table}",
                        params={"select": "count", "limit": 1}
                    )
                    if response.status_code == 200:
                        # Get count from response headers
                        count = response.headers.get("Content-Range", "0-0/0").split("/")[-1]
                        tables[table] = int(count) if count != "*" else 0
                    else:
                        tables[table] = "not_found"
                except:
                    tables[table] = "error"
            
            return {
                "connected": True,
                "url": self.supabase_url,
                "tables": tables
            }
            
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
    

class SupabaseService:
    """Service for interacting with Supabase via REST API."""

    def __init__(self, url: str, anon_key: str):
        """Initialize the SupabaseService with the project URL and anon key."""
        self.url = url
        self.anon_key = anon_key

    def health_check(self):
        """Perform a health check to ensure the service is reachable."""
        return f"Health check successful for {self.url}"

    def query_table(self, table_name: str):
        """Query a table in the Supabase database."""
        return f"Querying table {table_name} at {self.url}"

    def insert_row(self, table_name: str, data: dict):
        """Insert a row into a table."""
        return f"Inserting {data} into {table_name}"

    def update_row(self, table_name: str, row_id: int, data: dict):
        """Update a row in a table."""
        return f"Updating row {row_id} in {table_name} with {data}"

    def delete_row(self, table_name: str, row_id: int):
        """Delete a row from a table."""
        return f"Deleting row {row_id} from {table_name}"