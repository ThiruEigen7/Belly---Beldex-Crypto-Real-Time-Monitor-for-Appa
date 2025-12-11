"""
Pydantic models for Belly storage layer.
Defines data structures for Price, Stats, and Predictions.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


# ==================== Price Models ====================

class PriceBase(BaseModel):
    """Base price data model."""
    price_inr: float = Field(..., gt=0, description="Price in Indian Rupees")
    price_usd: float = Field(..., gt=0, description="Price in US Dollars")
    source: str = Field(default="api", description="Data source")


class PriceCreate(PriceBase):
    """Model for creating a price record."""
    pass


class Price(PriceBase):
    """Price model with timestamp."""
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the price")
    
    class Config:
        from_attributes = True


class PriceHistory(BaseModel):
    """Price history with date and value."""
    date: str = Field(..., description="Date in format 'Mon DD'")
    price: float = Field(..., gt=0, description="Average price for the date")
    timestamp: datetime = Field(..., description="ISO 8601 timestamp")
    
    class Config:
        from_attributes = True


# ==================== Stats Models ====================

class StatsBase(BaseModel):
    """Base statistics model."""
    period: str = Field(..., description="Time period (e.g., '24h', '7d', '30d')")
    high: float = Field(..., gt=0, description="Maximum price in period")
    low: float = Field(..., gt=0, description="Minimum price in period")
    average: float = Field(..., gt=0, description="Average price in period")
    volatility: float = Field(..., ge=0, description="Standard deviation (volatility)")


class StatsCreate(StatsBase):
    """Model for creating a stats record."""
    pass


class Stats(StatsBase):
    """Statistics model with computation time."""
    computed_at: datetime = Field(default_factory=datetime.utcnow, description="When stats were computed")
    
    class Config:
        from_attributes = True


class StatsSummary(BaseModel):
    """Summary of stats across different periods."""
    stats_24h: Optional[Stats] = Field(None, description="24-hour statistics")
    stats_7d: Optional[Stats] = Field(None, description="7-day statistics")
    stats_30d: Optional[Stats] = Field(None, description="30-day statistics")
    
    class Config:
        from_attributes = True


# ==================== Prediction Models ====================

class PredictionBase(BaseModel):
    """Base prediction model."""
    prediction_24h: float = Field(..., gt=0, description="Price prediction for next 24 hours")
    prediction_7d: float = Field(..., gt=0, description="Price prediction for next 7 days")
    trend: str = Field(..., description="Market trend (BULLISH, BEARISH, NEUTRAL)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    model_used: str = Field(..., description="ML model used for prediction")


class PredictionCreate(PredictionBase):
    """Model for creating a prediction record."""
    pass


class Prediction(PredictionBase):
    """Prediction model with generation time."""
    prediction_1h: Optional[float] = Field(None, gt=0, description="Price prediction for next hour")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When prediction was generated")
    
    class Config:
        from_attributes = True


class PredictionDetail(Prediction):
    """Detailed prediction with additional metrics."""
    model_accuracy: Optional[float] = Field(None, ge=0, le=1, description="Model accuracy on test data")
    prediction_interval_lower: Optional[float] = Field(None, description="Lower bound of prediction interval")
    prediction_interval_upper: Optional[float] = Field(None, description="Upper bound of prediction interval")
    
    class Config:
        from_attributes = True


# ==================== Combined Models ====================

class DashboardData(BaseModel):
    """Complete dashboard data model."""
    current_price: Price = Field(..., description="Current price")
    stats: StatsSummary = Field(..., description="Statistics summary")
    predictions: Prediction = Field(..., description="Latest predictions")
    price_history: List[PriceHistory] = Field(default_factory=list, description="Recent price history")
    
    class Config:
        from_attributes = True


class AnalyticsReport(BaseModel):
    """Analytics report with historical data."""
    period: str = Field(..., description="Report period")
    stats: Stats = Field(..., description="Period statistics")
    predictions: Prediction = Field(..., description="Predictions for period")
    price_change_percent: float = Field(..., description="Percentage change in period")
    trend_strength: float = Field(..., ge=0, le=1, description="Trend strength indicator")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation time")
    
    class Config:
        from_attributes = True


# ==================== API Response Models ====================

class ApiResponse(BaseModel):
    """Standard API response model."""
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[dict] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if unsuccessful")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Paginated API response model."""
    success: bool = Field(..., description="Whether the request was successful")
    data: List[dict] = Field(default_factory=list, description="Paginated data")
    total: int = Field(0, ge=0, description="Total number of records")
    page: int = Field(1, ge=1, description="Current page number")
    page_size: int = Field(10, ge=1, description="Records per page")
    total_pages: int = Field(0, ge=0, description="Total number of pages")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        from_attributes = True
