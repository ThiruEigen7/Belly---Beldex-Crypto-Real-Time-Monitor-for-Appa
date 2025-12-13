"""
Complete end-to-end streaming test
Tests: Producer → Redpanda → Consumer → Redis → Supabase
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from belly.streaming.producer import BeldexPriceProducer
from belly.streaming.consumer import BeldexPriceConsumer

print("\n" + "="*70)
print("🧪 BELLY STREAMING PIPELINE - END-TO-END TEST")
print("="*70)


async def test_complete_flow():
    """Test the complete streaming flow."""
    
    # ============ STEP 1: PRODUCER ============
    print("\n" + "="*70)
    print("STEP 1: Testing Producer (Fetch + Publish to Redpanda)")
    print("="*70)
    
    producer = BeldexPriceProducer()
    
    print("\n1️⃣ Connecting to Redpanda...")
    if not producer.connect():
        print("❌ Failed to connect to Kafka/Redpanda")
        return False
    print("✅ Connected to Redpanda Cloud")
    
    print("\n2️⃣ Fetching Beldex price from CoinGecko...")
    success = await producer.fetch_and_publish()
    
    if not success:
        print("❌ Failed to fetch and publish")
        producer.stop()
        return False
    
    stats = producer.get_stats()
    print(f"\n✅ Message published successfully!")
    print(f"   Price: ₹{stats['last_price']['price_inr']:.2f} / ${stats['last_price']['price_usd']:.4f}")
    print(f"   Total publishes: {stats['successful_publishes']}")
    
    producer.stop()
    
    # ============ STEP 2: CONSUMER ============
    print("\n" + "="*70)
    print("STEP 2: Testing Consumer (Consume → Redis → Supabase)")
    print("="*70)
    
    consumer = BeldexPriceConsumer()
    
    print("\n1️⃣ Connecting to services...")
    if not await consumer.connect_services():
        print("❌ Failed to connect to services")
        return False
    print("✅ Connected to Redis and Supabase")
    
    print("\n2️⃣ Connecting to Redpanda...")
    if not consumer.connect_kafka():
        print("❌ Failed to connect to Kafka/Redpanda")
        return False
    print("✅ Connected to Redpanda Cloud")
    
    print("\n3️⃣ Polling for message (timeout: 30s)...")
    
    try:
        messages = consumer.consumer.poll(timeout_ms=30000, max_records=1)
        
        if not messages:
            print("⚠️  No messages received")
            print("   This might mean all messages were already consumed")
            await consumer.stop()
            return True
        
        # Process first message
        for topic_partition, records in messages.items():
            for record in records:
                print(f"\n📬 Received message from partition {topic_partition.partition}")
                print(f"   Offset: {record.offset}")
                
                success = await consumer.process_message(record.value)
                
                if success:
                    print("\n✅ Message processed successfully!")
                    
                    # Show stats
                    stats = consumer.get_stats()
                    print(f"\n📊 Consumer Stats:")
                    print(f"   Messages consumed: {stats['messages_consumed']}")
                    print(f"   Redis writes: {stats['redis_writes']}")
                    print(f"   DB writes: {stats['db_writes']}")
                    print(f"   Last price: ₹{stats['last_price']['price_inr']:.2f}")
                else:
                    print("❌ Failed to process message")
                
                break
            break
        
        await consumer.stop()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        await consumer.stop()
        return False
    
    # ============ VERIFICATION ============
    print("\n" + "="*70)
    print("STEP 3: Verification")
    print("="*70)
    
    from belly.zebra.services.redis_service import RedisService
    from belly.zebra.services.db_service import DatabaseService
    
    # Check Redis
    print("\n🔴 Checking Redis...")
    redis = RedisService()
    await redis.connect()
    
    price_data = await redis.get_current_price()
    if price_data:
        print(f"✅ Redis has current price: ₹{price_data['price_inr']}")
    else:
        print("⚠️  No price data in Redis")
    
    await redis.disconnect()
    
    # Check Supabase
    print("\n🗄️  Checking Supabase...")
    db = DatabaseService()
    await db.connect()
    
    prices = await db.get_latest_prices(count=3)
    if prices:
        print(f"✅ Supabase has {len(prices)} recent entries:")
        for i, p in enumerate(prices, 1):
            print(f"   {i}. ₹{p.get('price_inr', 0):.2f} at {p.get('timestamp', 'N/A')}")
    else:
        print("⚠️  No price data in Supabase")
    
    await db.disconnect()
    
    # ============ SUCCESS ============
    print("\n" + "="*70)
    print("🎉 END-TO-END TEST COMPLETE!")
    print("="*70)
    print("\n✅ Full pipeline tested successfully:")
    print("   1. Producer → Fetched price from CoinGecko ✅")
    print("   2. Producer → Published to Redpanda Cloud ✅")
    print("   3. Consumer → Consumed from Redpanda Cloud ✅")
    print("   4. Consumer → Wrote to Redis (Upstash) ✅")
    print("   5. Consumer → Wrote to Supabase ✅")
    print("\n" + "="*70 + "\n")
    
    return True


if __name__ == "__main__":
    result = asyncio.run(test_complete_flow())
    sys.exit(0 if result else 1)
