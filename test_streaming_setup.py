"""
Test script to verify streaming setup without requiring Kafka
Tests Redis and Database connections
"""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add belly to path
sys.path.insert(0, str(Path(__file__).parent))

from belly.zebra.services.redis_service import RedisService
from belly.zebra.services.db_service import DatabaseService


async def test_redis():
    """Test Redis connection and operations."""
    print("\n" + "="*60)
    print("1️⃣  Testing Redis (Upstash)")
    print("="*60)
    
    try:
        redis = RedisService()
        await redis.connect()
        
        if redis.connected:
            print("✅ Redis connected successfully")
            
            # Test set/get
            test_price = {
                "price_inr": 123.45,
                "price_usd": 1.50,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            success = await redis.set_current_price(**test_price)
            if success:
                print("✅ Successfully wrote test price to Redis")
            else:
                print("❌ Failed to write to Redis")
            
            await redis.disconnect()
            return True
        else:
            print("❌ Redis connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Redis test error: {str(e)}")
        return False


async def test_database():
    """Test Database connection and operations."""
    print("\n" + "="*60)
    print("2️⃣  Testing Database (Supabase)")
    print("="*60)
    
    try:
        db = DatabaseService()
        await db.connect()
        
        if db.connected:
            print("✅ Database connected successfully")
            
            # Test insert
            success = await db.insert_price(
                price_inr=123.45,
                price_usd=1.50,
                source="test"
            )
            
            if success:
                print("✅ Successfully inserted test price to Database")
            else:
                print("❌ Failed to insert to Database")
            
            await db.disconnect()
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test error: {str(e)}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 STREAMING SETUP VERIFICATION")
    print("="*60)
    
    redis_ok = await test_redis()
    db_ok = await test_database()
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Redis (Upstash):     {'✅ PASS' if redis_ok else '❌ FAIL'}")
    print(f"Database (Supabase): {'✅ PASS' if db_ok else '❌ FAIL'}")
    
    if redis_ok and db_ok:
        print("\n🎉 All services are ready for streaming!")
        print("\n📝 Next steps:")
        print("   1. Install and run local Redpanda/Kafka")
        print("   2. Run: python belly/streaming/test.py")
    else:
        print("\n⚠️  Fix the failed services before testing streaming")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
