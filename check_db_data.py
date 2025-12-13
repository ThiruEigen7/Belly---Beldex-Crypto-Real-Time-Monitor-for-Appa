"""
Check if data was successfully written to Supabase
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from belly.zebra.services.db_service import DatabaseService


async def check_data():
    """Check recent data in Supabase."""
    print("\n" + "="*60)
    print("📊 Checking Supabase price_history table")
    print("="*60 + "\n")
    
    db = DatabaseService()
    await db.connect()
    
    if not db.connected:
        print("❌ Failed to connect to database")
        return
    
    # Get latest prices
    try:
        prices = await db.get_latest_prices(count=5)
        
        if prices:
            print(f"✅ Found {len(prices)} recent price entries:\n")
            for i, price in enumerate(prices, 1):
                print(f"{i}. ₹{price.get('price_inr')} / ${price.get('price_usd')}")
                print(f"   Source: {price.get('source')}")
                print(f"   Time: {price.get('timestamp')}\n")
        else:
            print("⚠️  No price data found in database")
            
    except Exception as e:
        print(f"❌ Error querying data: {str(e)}")
    
    await db.disconnect()
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(check_data())
