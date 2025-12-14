"""
BELLY Kafka Producer
Fetches Beldex price every 10 minutes and publishes to Kafka topic

Production Configuration:
- Connects to Redpanda Cloud (configured via environment variables)
- Fetches Beldex price from CoinGecko API
- Publishes to 'belly-price' topic
- Runs every 10 minutes (configurable via FETCH_INTERVAL)
- SASL/SSL authentication for secure cloud connection
"""
import os
import json
import time
import logging
from datetime import datetime
from typing import Optional, Dict
import asyncio

import httpx
from kafka import KafkaProducer
from kafka.errors import KafkaError
from dotenv import load_dotenv
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Load environment variables from .env.production (project root)
env_path = os.path.join(project_root, '.env.production')
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BeldexPriceProducer:
    """
    Kafka producer that fetches Beldex price and publishes to topic.
    
    Features:
    - Fetches from CoinGecko API
    - Publishes to Kafka topic
    - Runs every 10 minutes
    - Error handling and retries
    - Monitoring and logging
    """
    
    def __init__(self):
        """Initialize producer with configuration."""
        
        # Kafka configuration
        self.kafka_brokers = os.getenv(
            "KAFKA_BROKERS",
            "localhost:9092"  # Default for local Redpanda
        ).split(",")
        
        self.kafka_topic = os.getenv("KAFKA_TOPIC", "belly-price")
        
        # Security (for Redpanda Cloud)
        self.kafka_username = os.getenv("KAFKA_USERNAME", "")
        self.kafka_password = os.getenv("KAFKA_PASSWORD", "")
        
        # API configuration
        self.coingecko_url = "https://api.coingecko.com/api/v3/simple/price"
        self.beldex_id = "beldex"
        self.currencies = "inr,usd"
        
        # Producer configuration
        self.interval_seconds = int(os.getenv("FETCH_INTERVAL", "600"))  # 10 minutes
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
        self.producer: Optional[KafkaProducer] = None
        self.running = False
        self.stats = {
            "total_fetches": 0,
            "successful_publishes": 0,
            "failed_publishes": 0,
            "last_fetch_time": None,
            "last_price": None
        }
    
    def connect(self) -> bool:
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
                    'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
                    'key_serializer': lambda k: k.encode('utf-8') if k else None,
                    'acks': 'all',  # Wait for all replicas
                    'retries': 5,
                    'max_in_flight_requests_per_connection': 1,
                    'compression_type': 'gzip',
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
                self.producer = KafkaProducer(**kafka_config)
                logger.info(f"✅ Connected to Kafka successfully")
                return True
                
            except Exception as e:
                if attempt < max_connection_retries:
                    logger.warning(f"❌ Connection attempt {attempt} failed: {str(e)}. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"❌ Failed to connect to Kafka after {max_connection_retries} attempts: {str(e)}")
                    return False
    
    async def fetch_beldex_price(self) -> Optional[Dict]:
        """
        Fetch current Beldex price from CoinGecko API.
        
        Returns:
            Dict with price_inr, price_usd, timestamp or None
        """
        try:
            params = {
                'ids': self.beldex_id,
                'vs_currencies': self.currencies
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.coingecko_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if self.beldex_id not in data:
                    logger.error(f"❌ {self.beldex_id} not found in API response")
                    return None
                
                # Get raw prices from CoinGecko
                raw_price_inr = data[self.beldex_id].get('inr', 0.0)
                raw_price_usd = data[self.beldex_id].get('usd', 0.0)
                
                # Add 10 paise (₹0.10) to INR price
                adjusted_price_inr = round(raw_price_inr + 0.10, 2)
                
                # Add equivalent USD adjustment (₹0.10 ≈ $0.0012)
                adjusted_price_usd = round(raw_price_usd + 0.0012, 6)
                
                price_data = {
                    'price_inr': adjusted_price_inr,
                    'price_usd': adjusted_price_usd,
                    'timestamp': datetime.utcnow().isoformat(),
                    'source': 'coingecko'
                }
                
                logger.info(
                    f"✅ Fetched price (CoinGecko: ₹{raw_price_inr} + ₹0.10): "
                    f"₹{price_data['price_inr']} / ${price_data['price_usd']}"
                )
                
                self.stats['total_fetches'] += 1
                self.stats['last_fetch_time'] = price_data['timestamp']
                self.stats['last_price'] = price_data
                
                return price_data
                
        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error fetching price: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching price: {str(e)}")
            return None
    
    def publish_to_kafka(self, price_data: Dict) -> bool:
        """
        Publish price data to Kafka topic.
        
        Args:
            price_data: Price information to publish
            
        Returns:
            bool: True if successful
        """
        if not self.producer:
            logger.error("❌ Producer not connected")
            return False
        
        try:
            # Create message
            message = {
                **price_data,
                'published_at': datetime.utcnow().isoformat(),
                'producer_id': os.getenv('HOSTNAME', 'producer-1')
            }
            
            # Use timestamp as key for ordering
            key = price_data['timestamp']
            
            # Send to Kafka
            future = self.producer.send(
                self.kafka_topic,
                key=key,
                value=message
            )
            
            # Wait for confirmation (with timeout)
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"✅ Published to Kafka topic '{self.kafka_topic}' "
                f"(partition: {record_metadata.partition}, "
                f"offset: {record_metadata.offset})"
            )
            
            self.stats['successful_publishes'] += 1
            return True
            
        except KafkaError as e:
            logger.error(f"❌ Kafka error: {str(e)}")
            self.stats['failed_publishes'] += 1
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error publishing: {str(e)}")
            self.stats['failed_publishes'] += 1
            return False
    
    async def fetch_and_publish(self) -> bool:
        """
        Fetch price and publish to Kafka.
        
        Returns:
            bool: True if successful
        """
        logger.info("🔄 Starting fetch and publish cycle...")
        
        # Fetch price with retries
        price_data = None
        for attempt in range(self.max_retries):
            price_data = await self.fetch_beldex_price()
            
            if price_data:
                break
            
            if attempt < self.max_retries - 1:
                logger.warning(
                    f"⚠️ Retry {attempt + 1}/{self.max_retries} in "
                    f"{self.retry_delay}s..."
                )
                await asyncio.sleep(self.retry_delay)
        
        if not price_data:
            logger.error("❌ Failed to fetch price after all retries")
            return False
        
        # Publish to Kafka
        success = self.publish_to_kafka(price_data)
        
        if success:
            logger.info("✅ Fetch and publish cycle completed successfully")
        else:
            logger.error("❌ Failed to publish to Kafka")
        
        return success
    
    async def run(self):
        """
        Run producer in continuous loop.
        
        Fetches price every N seconds (default 600 = 10 minutes)
        """
        if not self.connect():
            logger.error("❌ Cannot start producer - Kafka connection failed")
            return
        
        self.running = True
        logger.info(
            f"🚀 Producer started - fetching every {self.interval_seconds}s "
            f"({self.interval_seconds // 60} minutes)"
        )
        
        try:
            while self.running:
                # Fetch and publish
                await self.fetch_and_publish()
                
                # Log stats
                logger.info(
                    f"📊 Stats - Total: {self.stats['total_fetches']}, "
                    f"Success: {self.stats['successful_publishes']}, "
                    f"Failed: {self.stats['failed_publishes']}"
                )
                
                # Wait for next interval
                logger.info(f"⏳ Waiting {self.interval_seconds}s until next fetch...")
                await asyncio.sleep(self.interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("⚠️ Received interrupt signal")
        except Exception as e:
            logger.error(f"❌ Unexpected error in producer loop: {str(e)}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop producer and close connections."""
        self.running = False
        
        if self.producer:
            logger.info("🧹 Flushing and closing producer...")
            self.producer.flush()
            self.producer.close()
            logger.info("✅ Producer stopped")
    
    def get_stats(self) -> Dict:
        """Get producer statistics."""
        return {
            **self.stats,
            'running': self.running,
            'interval_seconds': self.interval_seconds
        }


async def main():
    """Main entry point."""
    logger.info("""
╔══════════════════════════════════════════════════════════════╗
║             BELLY Kafka Producer - Starting                  ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    producer = BeldexPriceProducer()
    
    try:
        await producer.run()
    except Exception as e:
        logger.error(f"❌ Producer failed: {str(e)}")
        producer.stop()


if __name__ == "__main__":
    asyncio.run(main())