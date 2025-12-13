-- Update predictions table to match Airflow DAG expectations
-- This migration adds columns needed by the prediction DAG

ALTER TABLE predictions 
ADD COLUMN IF NOT EXISTS prediction_1h NUMERIC(18, 8),
ADD COLUMN IF NOT EXISTS prediction_24h NUMERIC(18, 8),
ADD COLUMN IF NOT EXISTS prediction_7d NUMERIC(18, 8),
ADD COLUMN IF NOT EXISTS model_used VARCHAR(50),
ADD COLUMN IF NOT EXISTS generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Add index for quick lookups
CREATE INDEX IF NOT EXISTS idx_predictions_generated_at ON predictions(generated_at DESC);

-- Update stats table to add computed_at column
ALTER TABLE stats
ADD COLUMN IF NOT EXISTS computed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_stats_computed_at ON stats(computed_at DESC);

-- Create or replace view for latest predictions
CREATE OR REPLACE VIEW v_latest_predictions AS
SELECT 
    prediction_1h,
    prediction_24h,
    prediction_7d,
    trend,
    confidence,
    model_used,
    generated_at
FROM predictions
ORDER BY generated_at DESC
LIMIT 1;

COMMENT ON TABLE predictions IS 'ML-generated price predictions for various time horizons';
COMMENT ON TABLE stats IS 'Computed price statistics for different time periods';
COMMENT ON TABLE price_history IS 'Real-time price data from streaming layer';
