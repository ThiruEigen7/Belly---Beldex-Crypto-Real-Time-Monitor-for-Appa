"""
Custom operator for price predictions using ML models.
Supports Prophet, ARIMA, and LSTM models.
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

logger = logging.getLogger(__name__)


class PredictionOperator(BaseOperator):
    """
    Operator for generating price predictions using ML models.
    
    Attributes:
        db_service: Database service instance
        model_type: Type of model to use ("prophet", "arima", "lstm")
        lookback_days: Number of days of historical data to use for training
    """
    
    @apply_defaults
    def __init__(
        self,
        db_service=None,
        model_type: str = "prophet",
        lookback_days: int = 30,
        *args,
        **kwargs
    ):
        """
        Initialize the prediction operator.
        
        Args:
            db_service: Database service instance
            model_type: Type of model ("prophet", "arima", "lstm")
            lookback_days: Days of history for training
        """
        super().__init__(*args, **kwargs)
        self.db_service = db_service
        self.model_type = model_type
        self.lookback_days = lookback_days
    
    def execute(self, context):
        """
        Execute prediction generation.
        
        Args:
            context: Airflow context
            
        Returns:
            Dictionary containing predictions
        """
        import asyncio
        
        logger.info(f"🤖 Generating predictions using {self.model_type} model")
        
        try:
            # Run async operation
            predictions = asyncio.run(self._generate_predictions())
            logger.info(f"✅ Predictions generated: {predictions}")
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Error generating predictions: {str(e)}")
            raise
    
    async def _generate_predictions(self) -> Dict[str, Any]:
        """
        Generate price predictions using the configured model.
        
        Returns:
            Dictionary containing predictions for 1h, 24h, and 7d
        """
        if not self.db_service:
            logger.error("❌ Database service not configured")
            return {}
        
        try:
            # Fetch historical price data
            prices = await self.db_service.get_price_history(days=self.lookback_days)
            
            if not prices:
                logger.warning("⚠️ No price history found for prediction")
                return {}
            
            # Extract price values
            price_values = [float(p["price"]) for p in prices]
            
            # Generate predictions based on model type
            if self.model_type == "prophet":
                predictions = await self._predict_prophet(price_values)
            elif self.model_type == "arima":
                predictions = await self._predict_arima(price_values)
            elif self.model_type == "lstm":
                predictions = await self._predict_lstm(price_values)
            else:
                logger.error(f"❌ Unknown model type: {self.model_type}")
                return {}
            
            # Determine trend
            trend = self._determine_trend(price_values, predictions)
            
            # Calculate confidence (based on model accuracy)
            confidence = self._calculate_confidence(price_values, predictions)
            
            result = {
                "prediction_1h": round(predictions.get("1h", 0), 4),
                "prediction_24h": round(predictions.get("24h", 0), 4),
                "prediction_7d": round(predictions.get("7d", 0), 4),
                "trend": trend,
                "confidence": round(confidence, 4),
                "model_used": self.model_type,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Store in database
            await self.db_service.insert_prediction(
                prediction_24h=predictions.get("24h", 0),
                prediction_7d=predictions.get("7d", 0),
                trend=trend,
                confidence=confidence,
                model_used=self.model_type
            )
            
            logger.info(f"✅ Predictions stored in database: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in _generate_predictions: {str(e)}")
            raise
    
    async def _predict_prophet(self, prices: List[float]) -> Dict[str, float]:
        """
        Generate predictions using Prophet model.
        
        Args:
            prices: List of historical prices
            
        Returns:
            Dictionary with predictions for 1h, 24h, 7d
        """
        try:
            from prophet import Prophet
            import pandas as pd
            from datetime import datetime, timedelta
            
            logger.info("📊 Training Prophet model...")
            
            # Prepare data
            df = pd.DataFrame({
                'ds': pd.date_range(end=datetime.now(), periods=len(prices), freq='h'),
                'y': prices
            })
            
            # Train model
            model = Prophet(interval_width=0.95, yearly_seasonality=False)
            model.fit(df)
            
            # Make future predictions
            future = model.make_future_dataframe(periods=168)  # 7 days ahead
            forecast = model.predict(future)
            
            # Extract predictions
            forecast_prices = forecast.tail(168)['yhat'].values
            
            return {
                "1h": float(forecast_prices[1]) if len(forecast_prices) > 1 else prices[-1],
                "24h": float(forecast_prices[24]) if len(forecast_prices) > 24 else prices[-1],
                "7d": float(forecast_prices[-1])
            }
            
        except ImportError:
            logger.warning("⚠️ Prophet not installed. Falling back to simple moving average.")
            return self._simple_forecast(prices)
        except Exception as e:
            logger.error(f"❌ Error in Prophet prediction: {str(e)}")
            return self._simple_forecast(prices)
    
    async def _predict_arima(self, prices: List[float]) -> Dict[str, float]:
        """
        Generate predictions using ARIMA model.
        
        Args:
            prices: List of historical prices
            
        Returns:
            Dictionary with predictions for 1h, 24h, 7d
        """
        try:
            from statsmodels.tsa.arima.model import ARIMA
            
            logger.info("📊 Training ARIMA model...")
            
            # Train ARIMA(1,1,1) model
            model = ARIMA(prices, order=(1, 1, 1))
            fitted_model = model.fit()
            
            # Forecast
            forecast = fitted_model.get_forecast(steps=168)
            forecast_prices = forecast.predicted_mean.values
            
            return {
                "1h": float(forecast_prices[1]) if len(forecast_prices) > 1 else prices[-1],
                "24h": float(forecast_prices[24]) if len(forecast_prices) > 24 else prices[-1],
                "7d": float(forecast_prices[-1])
            }
            
        except ImportError:
            logger.warning("⚠️ statsmodels not installed. Falling back to simple moving average.")
            return self._simple_forecast(prices)
        except Exception as e:
            logger.error(f"❌ Error in ARIMA prediction: {str(e)}")
            return self._simple_forecast(prices)
    
    async def _predict_lstm(self, prices: List[float]) -> Dict[str, float]:
        """
        Generate predictions using LSTM model.
        
        Args:
            prices: List of historical prices
            
        Returns:
            Dictionary with predictions for 1h, 24h, 7d
        """
        try:
            import numpy as np
            from tensorflow import keras
            from tensorflow.keras.layers import LSTM, Dense
            from sklearn.preprocessing import MinMaxScaler
            
            logger.info("📊 Training LSTM model...")
            
            # Normalize data
            scaler = MinMaxScaler()
            scaled_prices = scaler.fit_transform(np.array(prices).reshape(-1, 1))
            
            # Prepare sequences
            sequence_length = 24
            X, y = [], []
            for i in range(len(scaled_prices) - sequence_length):
                X.append(scaled_prices[i:i + sequence_length])
                y.append(scaled_prices[i + sequence_length])
            
            X, y = np.array(X), np.array(y)
            
            # Build and train LSTM model
            model = keras.Sequential([
                LSTM(50, activation='relu', input_shape=(sequence_length, 1)),
                Dense(1)
            ])
            model.compile(optimizer='adam', loss='mse')
            model.fit(X, y, epochs=10, verbose=0, batch_size=32)
            
            # Predict
            last_sequence = scaled_prices[-sequence_length:]
            forecast_prices = []
            for _ in range(168):
                next_pred = model.predict(last_sequence.reshape(1, sequence_length, 1), verbose=0)
                forecast_prices.append(next_pred[0, 0])
                last_sequence = np.append(last_sequence[1:], next_pred)
            
            # Denormalize predictions
            forecast_prices = scaler.inverse_transform(np.array(forecast_prices).reshape(-1, 1)).flatten()
            
            return {
                "1h": float(forecast_prices[1]) if len(forecast_prices) > 1 else prices[-1],
                "24h": float(forecast_prices[24]) if len(forecast_prices) > 24 else prices[-1],
                "7d": float(forecast_prices[-1])
            }
            
        except ImportError:
            logger.warning("⚠️ TensorFlow not installed. Falling back to simple moving average.")
            return self._simple_forecast(prices)
        except Exception as e:
            logger.error(f"❌ Error in LSTM prediction: {str(e)}")
            return self._simple_forecast(prices)
    
    def _simple_forecast(self, prices: List[float]) -> Dict[str, float]:
        """
        Simple exponential moving average forecast as fallback.
        
        Args:
            prices: List of historical prices
            
        Returns:
            Dictionary with simple predictions
        """
        logger.info("📊 Using simple exponential moving average")
        
        if not prices:
            return {"1h": 0, "24h": 0, "7d": 0}
        
        # Calculate 7-day moving average
        window = min(7, len(prices))
        ma = sum(prices[-window:]) / window
        
        # Simple forecast: assume slight trend continuation
        trend = (prices[-1] - prices[-window]) / window if window > 1 else 0
        
        return {
            "1h": ma + trend * 0.1,
            "24h": ma + trend * 1,
            "7d": ma + trend * 7
        }
    
    def _determine_trend(self, prices: List[float], predictions: Dict[str, float]) -> str:
        """
        Determine market trend based on prices and predictions.
        
        Args:
            prices: Historical prices
            predictions: Predicted prices
            
        Returns:
            Trend string: "BULLISH", "BEARISH", or "NEUTRAL"
        """
        if not prices or not predictions:
            return "NEUTRAL"
        
        current = prices[-1]
        predicted_24h = predictions.get("24h", current)
        
        change = ((predicted_24h - current) / current) * 100
        
        if change > 2:
            return "BULLISH"
        elif change < -2:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _calculate_confidence(self, prices: List[float], predictions: Dict[str, float]) -> float:
        """
        Calculate confidence score for predictions.
        
        Args:
            prices: Historical prices
            predictions: Predicted prices
            
        Returns:
            Confidence score between 0 and 1
        """
        if len(prices) < 2:
            return 0.5
        
        # Simple confidence based on price volatility
        avg_price = sum(prices) / len(prices)
        variance = sum((p - avg_price) ** 2 for p in prices) / len(prices)
        std_dev = variance ** 0.5
        coefficient_of_variation = (std_dev / avg_price) if avg_price > 0 else 0
        
        # Higher volatility = lower confidence
        confidence = max(0.3, 1 - coefficient_of_variation)
        
        return min(0.95, confidence)
