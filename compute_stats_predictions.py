#!/usr/bin/env python3
"""
Manually compute stats and predictions from current price data
and insert into Supabase
"""
import asyncio
import sys
from datetime import datetime, timedelta
from statistics import mean, stdev
sys.path.insert(0, '/home/thiru/belly')

from belly.zebra.services.db_service import DatabaseService

async def compute_stats():
    """Compute 24h, 7d, 30d statistics"""
    db = DatabaseService()
    print("📊 Computing statistics from current price data...\n")
    
    periods = {
        "24h": 1,
        "7d": 7,
        "30d": 30
    }
    
    for period_name, days in periods.items():
        print(f"Computing {period_name} stats...")
        
        # Get price history
        history = await db.get_price_history(days=days)
        
        if not history or len(history) < 2:
            print(f"  ⚠️  Not enough data for {period_name} (need at least 2 points)\n")
            continue
        
        # Extract prices
        prices = [float(item['price']) for item in history]
        
        # Compute stats
        high = max(prices)
        low = min(prices)
        avg = mean(prices)
        volatility = stdev(prices) if len(prices) > 1 else 0.0
        
        print(f"  High: ₹{high:.2f}")
        print(f"  Low: ₹{low:.2f}")
        print(f"  Average: ₹{avg:.2f}")
        print(f"  Volatility: {volatility:.2f}")
        
        # Store in database
        success = await db.store_stats(
            period=period_name,
            high=high,
            low=low,
            average=avg,
            volatility=volatility
        )
        
        if success:
            print(f"  ✅ Stored {period_name} stats\n")
        else:
            print(f"  ❌ Failed to store {period_name} stats\n")
    
    await db.close()

async def compute_predictions():
    """Compute simple predictions based on recent trend"""
    db = DatabaseService()
    print("🔮 Computing predictions...\n")
    
    # Get last 7 days of data
    history = await db.get_price_history(days=7)
    
    if not history or len(history) < 2:
        print("⚠️  Not enough data for predictions (need at least 2 points)\n")
        await db.close()
        return
    
    # Extract prices (most recent first)
    prices = [float(item['price']) for item in reversed(history)]
    current_price = prices[-1]
    
    # Simple trend analysis
    recent_avg = mean(prices[-3:]) if len(prices) >= 3 else current_price
    older_avg = mean(prices[:3]) if len(prices) >= 3 else current_price
    
    # Predict based on trend
    trend_multiplier = recent_avg / older_avg if older_avg > 0 else 1.0
    
    # 24h prediction (small change)
    prediction_24h = current_price * (1 + (trend_multiplier - 1) * 0.1)
    
    # 7d prediction (larger change)
    prediction_7d = current_price * trend_multiplier
    
    # Determine trend
    if trend_multiplier > 1.05:
        trend = "bullish"
        confidence = min(0.9, 0.6 + (trend_multiplier - 1))
    elif trend_multiplier < 0.95:
        trend = "bearish"
        confidence = min(0.9, 0.6 + (1 - trend_multiplier))
    else:
        trend = "neutral"
        confidence = 0.5
    
    print(f"Current Price: ₹{current_price:.2f}")
    print(f"24h Prediction: ₹{prediction_24h:.2f}")
    print(f"7d Prediction: ₹{prediction_7d:.2f}")
    print(f"Trend: {trend}")
    print(f"Confidence: {confidence:.2%}\n")
    
    # Store predictions
    success = await db.store_prediction(
        prediction_24h=prediction_24h,
        prediction_7d=prediction_7d,
        trend=trend,
        confidence=confidence,
        model_used="simple_trend"
    )
    
    if success:
        print("✅ Stored predictions\n")
    else:
        print("❌ Failed to store predictions\n")
    
    await db.close()

async def main():
    print("=" * 60)
    print("BELLY - Manual Stats & Predictions Computation")
    print("=" * 60)
    print()
    
    await compute_stats()
    await compute_predictions()
    
    print("=" * 60)
    print("✅ Done!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
