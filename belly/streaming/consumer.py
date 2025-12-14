"""
BELLY Kafka Consumer
Listens to Kafka topic and writes to Redis + Supabase

Production Configuration:
- Connects to Redpanda Cloud (configured via environment variables)
- Consumes from 'belly-price' topic
- Writes latest price to Redis (Upstash) for hot cache
- Writes price history to Supabase for persistent storage
- SASL/SSL authentication for secure cloud connection
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict
import asyncio

from kafka import KafkaConsumer
from kafka.errors import KafkaError
from dotenv import load_dotenv
import sys

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Load environment variables from .env.production (project root)
env_path = os.path.join(project_root, '.env.production')
load_dotenv(env_path)

try:
    from belly.zebra.services.redis_service import RedisService
    from belly.zebra.services.db_service import DatabaseService
except ImportError:
    # Try alternative import path when running from project root
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from zebra.services.redis_service import RedisService
    from zebra.services.db_service import DatabaseService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BeldexPriceConsumer:
    """
    Kafka consumer that processes price messages and stores them.
    
    Features:
    - Consumes from Kafka topic
    - Writes to Redis (hot cache)
    - Writes to Postgres (history)
    - Handles errors gracefully
    - Tracks statistics
    """
    
    def __init__(self):
        """Initialize consumer with configuration."""
        
        # Kafka configuration
        self.kafka_brokers = os.getenv(
            "KAFKA_BROKERS",
            "localhost:9092"
        ).split(",")
        
        self.kafka_topic = os.getenv("KAFKA_TOPIC", "belly-price")
        self.consumer_group = os.getenv("KAFKA_CONSUMER_GROUP", "belly-consumers")
        
        # Security (for Redpanda Cloud)
        self.kafka_username = os.getenv("KAFKA_USERNAME", "")
        self.kafka_password = os.getenv("KAFKA_PASSWORD", "")
        
        # Services
        self.redis: Optional[RedisService] = None
        self.db: Optional[DatabaseService] = None
        self.consumer: Optional[KafkaConsumer] = None
        
        self.running = False
        self.stats = {
            "messages_consumed": 0,
            "redis_writes": 0,
            "db_writes": 0,
            "redis_failures": 0,
            "db_failures": 0,
            "last_message_time": None,
            "last_price": None
        }
    
    async def connect_services(self) -> bool:
        """
        Connect to Redis and Database services.
        
        Returns:
            bool: True if at least one service connected
        """
        logger.info("🔌 Connecting to services...")
        
        # Connect to Redis
        self.redis = RedisService()
        await self.redis.connect()
        
        if self.redis.connected:
            logger.info("✅ Redis connected")
        else:
            logger.warning("⚠️ Redis not connected - will skip Redis writes")
        
        # Connect to Database
        self.db = DatabaseService()
        await self.db.connect()
        
        if self.db.pool:
            logger.info("✅ Database connected")
        else:
            logger.error("❌ Database not connected - consumer cannot function!")
            return False
        
        return True
    
    def connect_kafka(self) -> bool:
        """
        Connect to Kafka broker with retry logic.
        
        Returns:
            bool: True if successful
        """
        max_connection_retries = 3
        retry_delay = 5
        
        for attempt in range(1, max_connection_retries + 1):
            try:
                # Build Kafka config
                kafka_config = {
                    'bootstrap_servers': self.kafka_brokers,
                    'group_id': self.consumer_group,
                    'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
                    'key_deserializer': lambda k: k.decode('utf-8') if k else None,
                    'auto_offset_reset': 'earliest',  # Start from beginning if no offset
                    'enable_auto_commit': True,
                    'auto_commit_interval_ms': 5000,
                    'max_poll_records': 10,
                    'max_poll_interval_ms': 300000,  # 5 minutes
                    'request_timeout_ms': 30000,  # 30 seconds
                    'api_version_auto_timeout_ms': 10000,  # 10 seconds
                    'connections_max_idle_ms': 540000  # 9 minutes
                }
                
                # Add SASL authentication for Redpanda Cloud
                if self.kafka_username and self.kafka_password:
                    kafka_config.update({
                        'security_protocol': 'SASL_SSL',
                        'sasl_mechanism': 'SCRAM-SHA-256',
                        'sasl_plain_username': self.kafka_username,
                        'sasl_plain_password': self.kafka_password
                    })
                    logger.info("Using SASL authentication for Kafka")
                
                logger.info(f"Connection attempt {attempt}/{max_connection_retries} to Kafka brokers: {self.kafka_brokers}")
                self.consumer = KafkaConsumer(
                    self.kafka_topic,
                    **kafka_config
                )
                
                logger.info(
                    f"✅ Connected to Kafka - consuming from topic '{self.kafka_topic}' "
                    f"(group: {self.consumer_group})"
                )
                return True
                
            except Exception as e:
                if attempt < max_connection_retries:
                    logger.warning(f"❌ Connection attempt {attempt} failed: {str(e)}. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"❌ Failed to connect to Kafka after {max_connection_retries} attempts: {str(e)}")
                    return False
    
    async def process_message(self, message: Dict) -> bool:
        """
        Process a price message and store in Redis + Database.
        
        Args:
            message: Price message from Kafka
            
        Returns:
            bool: True if at least one storage succeeded
        """
        try:
            # Extract price data
            price_inr = message.get('price_inr', 0.0)
            price_usd = message.get('price_usd', 0.0)
            timestamp = message.get('timestamp')
            source = message.get('source', 'unknown')
            
            logger.info(
                f"📨 Processing message: ₹{price_inr} / ${price_usd} "
                f"(source: {source})"
            )
            
            redis_success = False
            db_success = False
            
            # Write to Redis (hot cache)
            if self.redis and self.redis.connected:
                redis_success = await self.redis.set_current_price(
                    price_inr=price_inr,
                    price_usd=price_usd,
                    timestamp=timestamp
                )
                
                if redis_success:
                    self.stats['redis_writes'] += 1
                    logger.info("✅ Written to Redis")
                else:
                    self.stats['redis_failures'] += 1
                    logger.warning("⚠️ Failed to write to Redis")
            
            # Write to Database (history)
            if self.db and self.db.pool:
                db_success = await self.db.insert_price(
                    price_inr=price_inr,
                    price_usd=price_usd,
                    source=source
                )
                
                if db_success:
                    self.stats['db_writes'] += 1
                    logger.info("✅ Written to Database")
                else:
                    self.stats['db_failures'] += 1
                    logger.error("❌ Failed to write to Database")
            
            # Update stats
            self.stats['messages_consumed'] += 1
            self.stats['last_message_time'] = datetime.utcnow().isoformat()
            self.stats['last_price'] = {
                'price_inr': price_inr,
                'price_usd': price_usd
            }
            
            # Consider it success if at least one write succeeded
            return redis_success or db_success
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {str(e)}")
            return False
    
    async def run(self):
        """
        Run consumer in continuous loop.
        
        Listens to Kafka topic and processes messages.
        """
        # Connect to services
        if not await self.connect_services():
            logger.error("❌ Cannot start consumer - service connection failed")
            return
        
        # Connect to Kafka
        if not self.connect_kafka():
            logger.error("❌ Cannot start consumer - Kafka connection failed")
            return
        
        self.running = True
        logger.info(f"🚀 Consumer started - listening to topic '{self.kafka_topic}'")
        
        try:
            # Consume messages
            for message in self.consumer:
                if not self.running:
                    break
                
                try:
                    logger.info(
                        f"📬 Received message from partition {message.partition} "
                        f"offset {message.offset}"
                    )
                    
                    # Process message
                    success = await self.process_message(message.value)
                    
                    if success:
                        logger.info("✅ Message processed successfully")
                    else:
                        logger.error("❌ Failed to process message")
                    
                    # Log stats periodically
                    if self.stats['messages_consumed'] % 10 == 0:
                        logger.info(
                            f"📊 Stats - Consumed: {self.stats['messages_consumed']}, "
                            f"Redis: {self.stats['redis_writes']}, "
                            f"DB: {self.stats['db_writes']}"
                        )
                    
                except Exception as e:
                    logger.error(f"❌ Error handling message: {str(e)}")
                    continue
                    
        except KeyboardInterrupt:
            logger.info("⚠️ Received interrupt signal")
        except Exception as e:
            logger.error(f"❌ Unexpected error in consumer loop: {str(e)}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop consumer and close connections."""
        self.running = False
        
        logger.info("🧹 Shutting down consumer...")
        
        # Close Kafka consumer
        if self.consumer:
            self.consumer.close()
            logger.info("✅ Kafka consumer closed")
        
        # Close Redis
        if self.redis:
            await self.redis.disconnect()
        
        # Close Database
        if self.db:
            await self.db.disconnect()
        
        logger.info("✅ Consumer stopped")
        
        # Log final stats
        logger.info(f"""
📊 Final Statistics:
   Messages Consumed: {self.stats['messages_consumed']}
   Redis Writes: {self.stats['redis_writes']} (failures: {self.stats['redis_failures']})
   DB Writes: {self.stats['db_writes']} (failures: {self.stats['db_failures']})
   Last Price: ₹{self.stats['last_price'].get('price_inr') if self.stats['last_price'] else 'N/A'}
        """)
    
    def get_stats(self) -> Dict:
        """Get consumer statistics."""
        return {
            **self.stats,
            'running': self.running
        }


async def main():
    """Main entry point."""
    logger.info("""
╔══════════════════════════════════════════════════════════════╗
║             BELLY Kafka Consumer - Starting                  ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    consumer = BeldexPriceConsumer()
    
    try:
        await consumer.run()
    except Exception as e:
        logger.error(f"❌ Consumer failed: {str(e)}")
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())