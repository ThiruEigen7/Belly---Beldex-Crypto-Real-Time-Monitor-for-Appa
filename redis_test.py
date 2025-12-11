import os
from dotenv import load_dotenv
from upstash_redis import Redis

# Load environment variables
load_dotenv()

# Get Redis Upstash URL from environment variables
REDIS_URL = os.getenv("REDIS_URL")
REDIS_TOKEN = os.getenv("REDIS_TOKEN")

if not REDIS_URL or not REDIS_TOKEN:
    raise ValueError("REDIS_URL and REDIS_TOKEN must be set in the environment variables.")

# Connect to Redis Upstash
try:
    redis = Redis(
        url=REDIS_URL,
        token=REDIS_TOKEN
    )

    # Test the connection
    redis.set("test_key", "test_value")
    value = redis.get("test_key")
    print(f"Successfully connected to Redis Upstash! Value for 'test_key': {value}")

except Exception as e:
    print(f"Failed to connect to Redis Upstash: {e}")