"""
Test script for Supabase connection and operations
Run with: python test_supabase.py
"""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from belly.zebra.services.db_service import DatabaseService

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables")


async def test_connection():
    """Test basic connection to Supabase."""
    print("\n" + "="*60)
    print("1️⃣  Testing Supabase Connection")
    print("="*60)
    
    db = DatabaseService()
    
    # Show configuration
    print(f"\n📋 Configuration:")
    print(f"   URL: {db.supabase_url}")
    print(f"   API Key: {'✅ Set' if db.supabase_key else '❌ Not set'}")
    
    if not db.supabase_key:
        print("\n❌ SUPABASE_ANON_KEY is not set!")
        print("   Please add it to your .env file:")
        print("   SUPABASE_ANON_KEY=your-key-here")
        return False
    
    # Connect
    print("\n🔌 Connecting to Supabase...")
    await db.connect()
    
    if db.connected:
        print("✅ Connected successfully!")
        return db
    else:
        print("❌ Connection failed!")
        return False


async def test_health_check(db):
    """Test health check endpoint."""
    print("\n" + "="*60)
    print("2️⃣  Testing Health Check")
    print("="*60)
    
    health = await db.health_check()
    
    if health.get("connected"):
        print("\n✅ Health Check Passed:")
        print(f"   URL: {health.get('url')}")
        print(f"\n📊 Tables:")
        for table, count in health.get("tables", {}).items():
            status = "✅" if isinstance(count, int) else "⚠️"
            print(f"   {status} {table}: {count}")
        return True
    else:
        print(f"\n❌ Health Check Failed: {health.get('error')}")
        return False


async def test_price_operations(db):
    """Test price history operations."""
    print("\n" + "="*60)
    print("3️⃣  Testing Price Operations")
    print("="*60)
    
    # Insert test price
    print("\n📝 Inserting test price...")
    test_price_inr = 35.50
    test_price_usd = 0.43
    
    success = await db.insert_price(
        price_inr=test_price_inr,
        price_usd=test_price_usd,
        source="test"
    )
    
    if success:
        print(f"✅ Inserted: ₹{test_price_inr} / ${test_price_usd}")
    else:
        print("❌ Insert failed!")
        return False
    
    # Wait a moment
    await asyncio.sleep(1)
    
    # Get latest price
    print("\n📊 Fetching latest price...")
    latest = await db.get_latest_price()
    
    if latest:
        print(f"✅ Latest price:")
        print(f"   INR: ₹{latest['price_inr']}")
        print(f"   USD: ${latest['price_usd']}")
        print(f"   Time: {latest['timestamp']}")
    else:
        print("⚠️  No prices found")
    
    # Get latest 5 prices
    print("\n📊 Fetching latest 5 prices...")
    latest_prices = await db.get_latest_prices(5)
    
    if latest_prices:
        print(f"✅ Found {len(latest_prices)} prices:")
        for i, price in enumerate(latest_prices[:3], 1):
            print(f"   {i}. ₹{price['price_inr']} - {price['timestamp']}")
    else:
        print("⚠️  No prices found")
    
    # Get price history
    print("\n📊 Fetching 5-day history...")
    history = await db.get_price_history(days=5)
    
    if history:
        print(f"✅ Found {len(history)} data points:")
        for point in history[:3]:
            print(f"   {point['date']}: ₹{point['price']}")
    else:
        print("⚠️  No history found")
    
    return True


async def test_stats_operations(db):
    """Test stats operations."""
    print("\n" + "="*60)
    print("4️⃣  Testing Stats Operations")
    print("="*60)
    
    # Insert test stats
    print("\n📝 Inserting test stats...")
    success = await db.insert_stats(
        period="24h",
        high=36.00,
        low=34.50,
        average=35.25,
        volatility=2.3
    )
    
    if success:
        print("✅ Stats inserted")
    else:
        print("❌ Insert failed!")
        return False
    
    # Wait a moment
    await asyncio.sleep(1)
    
    # Get stats
    print("\n📊 Fetching stats for 24h...")
    stats = await db.get_stats("24h")
    
    if stats:
        print("✅ Stats retrieved:")
        print(f"   High: ₹{stats['high']}")
        print(f"   Low: ₹{stats['low']}")
        print(f"   Average: ₹{stats['average']}")
        print(f"   Volatility: {stats['volatility']}%")
        print(f"   Computed: {stats['computed_at']}")
    else:
        print("⚠️  No stats found")
    
    return True


async def test_predictions_operations(db):
    """Test predictions operations."""
    print("\n" + "="*60)
    print("5️⃣  Testing Predictions Operations")
    print("="*60)
    
    # Insert test prediction
    print("\n📝 Inserting test prediction...")
    success = await db.insert_prediction(
        prediction_24h=36.20,
        prediction_7d=37.50,
        trend="bullish",
        confidence=0.85,
        model_used="test_model"
    )
    
    if success:
        print("✅ Prediction inserted")
    else:
        print("❌ Insert failed!")
        return False
    
    # Wait a moment
    await asyncio.sleep(1)
    
    # Get predictions
    print("\n📊 Fetching predictions...")
    predictions = await db.get_predictions()
    
    if predictions:
        print("✅ Predictions retrieved:")
        print(f"   24h: ₹{predictions['prediction_24h']}")
        print(f"   7d: ₹{predictions['prediction_7d']}")
        print(f"   Trend: {predictions['trend']}")
        print(f"   Confidence: {predictions['confidence']}")
        print(f"   Model: {predictions['model_used']}")
    else:
        print("⚠️  No predictions found")
    
    return True


async def test_table_queries(db):
    """Test generic table query."""
    print("\n" + "="*60)
    print("6️⃣  Testing Generic Table Queries")
    print("="*60)
    
    # Query price_history table
    print("\n📊 Querying price_history table...")
    rows = await db.query_table(
        table="price_history",
        select="price_inr,timestamp",
        limit=3,
        order="timestamp.desc"
    )
    
    if rows:
        print(f"✅ Found {len(rows)} rows:")
        for row in rows:
            print(f"   ₹{row.get('price_inr')} - {row.get('timestamp')}")
    else:
        print("⚠️  No rows found or query failed")
    
    return True


async def run_all_tests():
    """Run all tests in sequence."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║          BELLY Supabase Connection Test Suite               ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Test connection
    db = await test_connection()
    if not db:
        print("\n❌ Connection test failed. Exiting.")
        return
    
    try:
        # Test health check
        health_ok = await test_health_check(db)
        if not health_ok:
            print("\n⚠️  Health check failed, but continuing...")
        
        # Test price operations
        print("\n⏳ Testing price operations...")
        await test_price_operations(db)
        
        # Test stats operations
        print("\n⏳ Testing stats operations...")
        await test_stats_operations(db)
        
        # Test predictions operations
        print("\n⏳ Testing predictions operations...")
        await test_predictions_operations(db)
        
        # Test generic queries
        print("\n⏳ Testing generic queries...")
        await test_table_queries(db)
        
        print("\n" + "="*60)
        print("✅ All Tests Complete!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        await db.disconnect()


async def quick_test():
    """Quick connection test only."""
    print("\n🔍 Quick Connection Test\n")
    
    db = DatabaseService()
    
    print(f"URL: {db.supabase_url}")
    print(f"Key: {'✅ Set' if db.supabase_key else '❌ Missing'}")
    
    if not db.supabase_key:
        print("\n❌ Add SUPABASE_ANON_KEY to .env file")
        return
    
    await db.connect()
    
    if db.connected:
        print("\n✅ Connection successful!")
        
        # Quick health check
        health = await db.health_check()
        print(f"\nTables found:")
        for table, count in health.get("tables", {}).items():
            print(f"  • {table}: {count}")
    else:
        print("\n❌ Connection failed!")
    
    await db.disconnect()


def main_menu():
    """Interactive menu."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║          BELLY Supabase Test - Choose Option                ║
╚══════════════════════════════════════════════════════════════╝

1. Quick Connection Test (fast)
2. Run All Tests (comprehensive)
3. Test Connection Only
4. Test Price Operations
5. Test Stats Operations
6. Test Predictions Operations

0. Exit
""")
    
    return input("Enter choice (0-6): ").strip()


async def main():
    """Main entry point."""
    
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found!")
        print("   Create .env with:")
        print("   SUPABASE_URL=https://your-project.supabase.co")
        print("   SUPABASE_ANON_KEY=your-anon-key")
        return
    
    while True:
        choice = main_menu()
        
        if choice == "0":
            print("\n👋 Goodbye!")
            break
        elif choice == "1":
            await quick_test()
        elif choice == "2":
            await run_all_tests()
        elif choice == "3":
            db = await test_connection()
            if db:
                await db.disconnect()
        elif choice == "4":
            db = await test_connection()
            if db:
                await test_price_operations(db)
                await db.disconnect()
        elif choice == "5":
            db = await test_connection()
            if db:
                await test_stats_operations(db)
                await db.disconnect()
        elif choice == "6":
            db = await test_connection()
            if db:
                await test_predictions_operations(db)
                await db.disconnect()
        else:
            print("\n❌ Invalid choice")
        
        input("\n\nPress Enter to continue...")


if __name__ == "__main__":
    # Quick test if no args, otherwise interactive
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        asyncio.run(quick_test())
    else:
        asyncio.run(main())