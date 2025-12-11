-- BELLY Storage Layer - PostgreSQL Schema
-- Initialization script for Supabase or local PostgreSQL

-- ============================================
-- Price History Table
-- ============================================
CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    price_inr NUMERIC(18, 8) NOT NULL,
    price_usd NUMERIC(18, 8) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    source VARCHAR(50) DEFAULT 'market_api' NOT NULL,
    volume NUMERIC(18, 2),
    market_cap NUMERIC(20, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for efficient querying
CREATE INDEX idx_price_history_timestamp ON price_history(timestamp DESC);
CREATE INDEX idx_price_history_date ON price_history(DATE(timestamp));
CREATE INDEX idx_price_history_created_at ON price_history(created_at DESC);

-- ============================================
-- Market Statistics Table
-- ============================================
CREATE TABLE IF NOT EXISTS stats (
    id SERIAL PRIMARY KEY,
    period VARCHAR(20) NOT NULL DEFAULT '24h', -- '1h', '24h', '7d', '30d'
    high NUMERIC(18, 8) NOT NULL,
    low NUMERIC(18, 8) NOT NULL,
    average NUMERIC(18, 8) NOT NULL,
    volatility NUMERIC(5, 2) NOT NULL, -- percentage
    volume NUMERIC(20, 2),
    change_percent NUMERIC(6, 2), -- price change %
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(period, DATE(timestamp))
);

-- Create indexes
CREATE INDEX idx_stats_period ON stats(period);
CREATE INDEX idx_stats_timestamp ON stats(timestamp DESC);
CREATE INDEX idx_stats_period_timestamp ON stats(period, timestamp DESC);

-- ============================================
-- Price Predictions Table
-- ============================================
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    predicted_price NUMERIC(18, 8) NOT NULL,
    confidence NUMERIC(4, 2) NOT NULL, -- 0-100 percentage
    forecast_date DATE NOT NULL,
    forecast_period VARCHAR(20) NOT NULL DEFAULT '24h', -- '24h', '7d', '30d'
    model_version VARCHAR(50) NOT NULL,
    trend VARCHAR(20) NOT NULL DEFAULT 'neutral', -- 'bullish', 'bearish', 'neutral'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes
CREATE INDEX idx_predictions_forecast_date ON predictions(forecast_date DESC);
CREATE INDEX idx_predictions_forecast_period ON predictions(forecast_period);
CREATE INDEX idx_predictions_created_at ON predictions(created_at DESC);

-- ============================================
-- Analytics Events Table (for tracking system activity)
-- ============================================
CREATE TABLE IF NOT EXISTS analytics_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    user_id VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_events_timestamp ON analytics_events(timestamp DESC);

-- ============================================
-- Create Views for Common Queries
-- ============================================

-- Latest price view
CREATE OR REPLACE VIEW v_latest_price AS
SELECT 
    price_inr,
    price_usd,
    timestamp,
    source,
    volume,
    market_cap
FROM price_history
ORDER BY timestamp DESC
LIMIT 1;

-- 24h stats view
CREATE OR REPLACE VIEW v_24h_stats AS
SELECT 
    high,
    low,
    average,
    volatility,
    change_percent,
    timestamp
FROM stats
WHERE period = '24h'
ORDER BY timestamp DESC
LIMIT 1;

-- Latest predictions view
CREATE OR REPLACE VIEW v_latest_predictions AS
SELECT 
    predicted_price,
    confidence,
    forecast_date,
    forecast_period,
    trend,
    model_version
FROM predictions
WHERE forecast_date >= CURRENT_DATE
ORDER BY created_at DESC
LIMIT 5;

-- ============================================
-- Enable PostGIS (optional, for geospatial data)
-- Uncomment if needed
-- ============================================
-- CREATE EXTENSION IF NOT EXISTS postgis;
-- CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- ============================================
-- Grant permissions (for non-admin users)
-- ============================================
-- GRANT USAGE ON SCHEMA public TO belly_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO belly_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO belly_user;
