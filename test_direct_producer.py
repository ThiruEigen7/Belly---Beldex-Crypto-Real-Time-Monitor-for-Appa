"""
Direct test - try to produce to belly-price topic
"""
import os
import json
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS")
KAFKA_USERNAME = os.getenv("KAFKA_USERNAME")
KAFKA_PASSWORD = os.getenv("KAFKA_PASSWORD")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "belly-price")

print("\n" + "="*60)
print("📤 Direct Producer Test")
print("="*60)
print(f"Topic: {KAFKA_TOPIC}\n")

kafka_config = {
    'bootstrap_servers': KAFKA_BROKERS.split(","),
    'security_protocol': 'SASL_SSL',
    'sasl_mechanism': 'SCRAM-SHA-256',
    'sasl_plain_username': KAFKA_USERNAME,
    'sasl_plain_password': KAFKA_PASSWORD,
    'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
    'api_version': (2, 5, 0),
    'request_timeout_ms': 30000,
}

try:
    print("1️⃣ Creating producer...")
    producer = KafkaProducer(**kafka_config)
    print("✅ Producer created\n")
    
    print("2️⃣ Sending test message...")
    test_message = {
        "price_inr": 123.45,
        "price_usd": 1.50,
        "timestamp": "2025-12-12T10:00:00Z",
        "source": "test"
    }
    
    future = producer.send(KAFKA_TOPIC, test_message)
    record_metadata = future.get(timeout=30)
    
    print(f"✅ Message sent successfully!")
    print(f"   Topic: {record_metadata.topic}")
    print(f"   Partition: {record_metadata.partition}")
    print(f"   Offset: {record_metadata.offset}\n")
    
    producer.flush()
    producer.close()
    
    print("="*60)
    print("🎉 Producer test successful!")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
