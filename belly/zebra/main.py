"""
BELLY Backend - FastAPI Application
Serves as the façade layer between UI and data storage
"""
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Optional
import logging

from .models import (
    CurrentPriceResponse,
    HistoryResponse,
    StatsResponse,
    PredictionResponse,
    HealthResponse
)
from .services.redis_service import RedisService
from .services.db_service import DatabaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BELLY API",
    description="Beldex Crypto Monitoring Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - allow Reflex UI to access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Reflex Cloud URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
redis_service = RedisService()
db_service = DatabaseService()


@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup."""
    logger.info("Starting BELLY Backend API...")
    await redis_service.connect()
    await db_service.connect()
    logger.info("✅ All services connected successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Close connections on shutdown."""
    logger.info("Shutting down BELLY Backend API...")
    await redis_service.disconnect()
    await db_service.disconnect()
    logger.info("✅ All services disconnected")


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="BELLY API is running",
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check with service status."""
    redis_status = await redis_service.ping()
    db_status = await db_service.ping()
    
    return HealthResponse(
        status="healthy" if (redis_status and db_status) else "degraded",
        message="All systems operational" if (redis_status and db_status) else "Some services down",
        timestamp=datetime.utcnow().isoformat(),
        services={
            "redis": "up" if redis_status else "down",
            "database": "up" if db_status else "down"
        }
    )


@app.get("/current-price", response_model=CurrentPriceResponse)
async def get_current_price():
    """
    Fetch latest Beldex price from Redis cache.
    
    Returns:
        CurrentPriceResponse with price_inr, price_usd, timestamp
    
    Fallback:
        If Redis is down, fetches from database (last known price)
    """
    try:
        # Try Redis first (hot data)
        price_data = await redis_service.get_current_price()
        
        if price_data:
            logger.info("✅ Price fetched from Redis")
            return CurrentPriceResponse(**price_data)
        
        # Fallback to database
        logger.warning("⚠️ Redis miss, falling back to database")
        price_data = await db_service.get_latest_price()
        
        if price_data:
            return CurrentPriceResponse(**price_data)
        
        raise HTTPException(
            status_code=503,
            detail="Unable to fetch current price from any source"
        )
        
    except Exception as e:
        logger.error(f"❌ Error fetching current price: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history", response_model=HistoryResponse)
async def get_price_history(
    days: int = Query(default=5, ge=1, le=365, description="Number of days of history")
):
    """
    Fetch historical price data from Postgres.
    
    Args:
        days: Number of days of history (1-365)
    
    Returns:
        HistoryResponse with list of price points
    """
    try:
        history = await db_service.get_price_history(days=days)
        
        if not history:
            logger.warning(f"⚠️ No history found for {days} days")
            return HistoryResponse(
                days=days,
                data=[],
                count=0
            )
        
        logger.info(f"✅ Fetched {len(history)} price points for {days} days")
        return HistoryResponse(
            days=days,
            data=history,
            count=len(history)
        )
        
    except Exception as e:
        logger.error(f"❌ Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=StatsResponse)
async def get_market_stats(
    period: str = Query(default="24h", description="Time period: 24h, 7d, 30d")
):
    """
    Fetch market statistics computed by Airflow.
    
    Args:
        period: Time period for stats (24h, 7d, 30d)
    
    Returns:
        StatsResponse with high, low, avg, volatility
    """
    try:
        stats = await db_service.get_stats(period=period)
        
        if not stats:
            logger.warning(f"⚠️ No stats found for period: {period}")
            # Return default empty stats
            return StatsResponse(
                period=period,
                high=0.0,
                low=0.0,
                average=0.0,
                volatility=0.0,
                computed_at=datetime.utcnow().isoformat()
            )
        
        logger.info(f"✅ Fetched stats for period: {period}")
        return StatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"❌ Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predict", response_model=PredictionResponse)
async def get_predictions():
    """
    Fetch ML-based price predictions computed by Airflow.
    
    Returns:
        PredictionResponse with 24h and 7d forecasts
    """
    try:
        predictions = await db_service.get_predictions()
        
        if not predictions:
            logger.warning("⚠️ No predictions available")
            # Return neutral predictions
            return PredictionResponse(
                prediction_24h=0.0,
                prediction_7d=0.0,
                trend="neutral",
                confidence=0.0,
                model_used="none",
                generated_at=datetime.utcnow().isoformat()
            )
        
        logger.info("✅ Fetched predictions")
        return PredictionResponse(**predictions)
        
    except Exception as e:
        logger.error(f"❌ Error fetching predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Additional utility endpoints

@app.get("/latest/{count}")
async def get_latest_prices(count: int = Query(default=10, ge=1, le=100)):
    """Get the latest N price entries."""
    try:
        prices = await db_service.get_latest_prices(count)
        return {"count": len(prices), "data": prices}
    except Exception as e:
        logger.error(f"❌ Error fetching latest prices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/price-range")
async def get_price_range(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get price data within a date range."""
    try:
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
        if not end_date:
            end_date = datetime.utcnow().isoformat()
        
        prices = await db_service.get_price_range(start_date, end_date)
        return {
            "start_date": start_date,
            "end_date": end_date,
            "count": len(prices),
            "data": prices
        }
    except Exception as e:
        logger.error(f"❌ Error fetching price range: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )