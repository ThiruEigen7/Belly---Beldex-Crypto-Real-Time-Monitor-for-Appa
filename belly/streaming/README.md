# BELLY Streaming Layer

Real-time price data ingestion pipeline using Kafka (Redpanda Cloud).

## Architecture

```
CoinGecko API → Producer → Redpanda Cloud → Consumer → Redis + Supabase
                (10 min)    (belly-price)           (cache)  (history)
```

## Components

### 1. Producer (`producer.py`)
- **Purpose**: Fetch Beldex price and publish to Kafka
- **Interval**: Every 10 minutes (configurable)
- **API**: CoinGecko Public API
- **Output**: Publishes to `belly-price` topic

### 2. Consumer (`consumer.py`)
- **Purpose**: Consume messages and store in Redis + Supabase
- **Input**: Reads from `belly-price` topic
- **Outputs**: 
  - Redis (Upstash): Hot cache for current price
  - Supabase: Historical price data

## Configuration

All configuration is in `.env` file:

```env
# Redpanda Cloud
KAFKA_BROKERS=your-cluster.cloud.redpanda.com:9092
KAFKA_TOPIC=belly-price
KAFKA_CONSUMER_GROUP=belly-consumers
KAFKA_USERNAME=your-username
KAFKA_PASSWORD=your-password
FETCH_INTERVAL=600  # 10 minutes

# Redis (Upstash)
REDIS_URL=https://your-redis.upstash.io
REDIS_TOKEN=your-redis-token

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

## Running

### Development

```bash
# Run producer once
python belly/streaming/producer.py

# Run consumer (continuous)
python belly/streaming/consumer.py
```

### Production

Use Docker or systemd services to run continuously.

#### Docker

```bash
# Producer
docker build -f belly/streaming/DockerFile.producer -t belly-producer .
docker run -d --env-file .env belly-producer

# Consumer
docker build -f belly/streaming/DockerFile.consumer -t belly-consumer .
docker run -d --env-file .env belly-consumer
```

## Testing

```bash
# Test end-to-end pipeline
python test_streaming_end_to_end.py

# Test producer only
python test_direct_producer.py

# Test services (Redis + Supabase)
python test_streaming_setup.py
```

## Monitoring

- **Producer**: Logs fetch and publish statistics
- **Consumer**: Logs consumption, Redis writes, DB writes
- **Redpanda Console**: View topics, partitions, consumer groups

## Security

- SASL/SSL authentication for Redpanda Cloud
- API keys for Redis and Supabase
- All credentials in `.env` (never commit to git)

## Troubleshooting

### Producer not connecting
- Check `KAFKA_BROKERS`, `KAFKA_USERNAME`, `KAFKA_PASSWORD`
- Verify Redpanda Cloud user has WRITE permission on topic

### Consumer not consuming
- Check consumer group ACLs in Redpanda Console
- User needs READ permission on topic AND consumer group

### Redis connection failed
- Verify `REDIS_URL` and `REDIS_TOKEN`
- Check Upstash Redis dashboard

### Supabase write failed
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- Check `price_history` table exists
- Verify table schema matches expected columns
