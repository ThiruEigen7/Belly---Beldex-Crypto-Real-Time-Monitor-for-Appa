"""
Test Redpanda Cloud connection and create topic
"""
import os
from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
from dotenv import load_dotenv

load_dotenv()

# Get credentials from environment
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS")
KAFKA_USERNAME = os.getenv("KAFKA_USERNAME")
KAFKA_PASSWORD = os.getenv("KAFKA_PASSWORD")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "belly-price")

print("\n" + "="*60)
print("🔌 Testing Redpanda Cloud Connection")
print("="*60)
print(f"Broker: {KAFKA_BROKERS}")
print(f"Username: {KAFKA_USERNAME}")
print(f"Topic: {KAFKA_TOPIC}")
print("="*60 + "\n")

# Kafka configuration
kafka_config = {
    'bootstrap_servers': KAFKA_BROKERS.split(","),
    'security_protocol': 'SASL_SSL',
    'sasl_mechanism': 'SCRAM-SHA-256',
    'sasl_plain_username': KAFKA_USERNAME,
    'sasl_plain_password': KAFKA_PASSWORD,
    'api_version': (2, 5, 0),  # Specify API version
    'request_timeout_ms': 30000,
    'connections_max_idle_ms': 540000,
}

try:
    print("1️⃣ Connecting to Redpanda Cloud...")
    admin = KafkaAdminClient(**kafka_config)
    print("✅ Connected successfully!\n")
    
    print("2️⃣ Listing existing topics...")
    consumer_config = kafka_config.copy()
    consumer_config['group_id'] = 'test-group'
    consumer_config['value_deserializer'] = lambda m: m.decode('utf-8') if m else None
    
    from kafka import KafkaConsumer
    test_consumer = KafkaConsumer(**consumer_config)
    topics = test_consumer.topics()
    test_consumer.close()
    
    print(f"📋 Available topics: {topics}")
    
    if KAFKA_TOPIC in topics:
        print(f"✅ Topic '{KAFKA_TOPIC}' exists\n")
    else:
        print(f"⚠️  Topic '{KAFKA_TOPIC}' does not exist")
        print(f"   Please verify the topic name in Redpanda Console")
        print(f"   Expected: '{KAFKA_TOPIC}'\n")
    
    admin.close()
    
    print("3️⃣ Testing producer...")
    producer_config = kafka_config.copy()
    producer_config['value_serializer'] = lambda v: str(v).encode('utf-8')
    
    producer = KafkaProducer(**producer_config)
    future = producer.send(KAFKA_TOPIC, b'test-message')
    result = future.get(timeout=10)
    print(f"✅ Message sent successfully to partition {result.partition}\n")
    producer.close()
    
    print("="*60)
    print("🎉 Redpanda Cloud is ready!")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
