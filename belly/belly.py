"""
BELLY - Beldex Crypto Monitoring Dashboard
Main application file
"""
import reflex as rx
from typing import List, Dict, Any


class State(rx.State):
    """The app state."""
    # Current price data
    current_price_inr: float = 0.0
    current_price_usd: float = 0.0
    last_updated: str = "Loading..."
    
    # Historical data for chart
    historical_data: list = []
    
    # Stats data
    high_24h: float = 0.0
    low_24h: float = 0.0
    avg_24h: float = 0.0
    volatility: float = 0.0
    
    # Prediction data
    prediction_24h: float = 0.0
    prediction_7d: float = 0.0
    prediction_trend: str = "neutral"
    prediction_5d: List[Dict[str, Any]] = []  # Typed for rx.foreach
    
    # Calculator
    quantity: float = 1.0
    calculated_value: float = 0.0
    
    # Loading states
    is_loading: bool = True
    error_message: str = ""
    
    # API base URL (change this to your Railway deployment)
    api_base_url: str = "http://localhost:8000"  # Change to Railway URL later
    
    async def load_current_price(self):
        """Fetch current price from FastAPI."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_base_url}/current-price")
                if response.status_code == 200:
                    data = response.json()
                    self.current_price_inr = data["price_inr"]
                    self.current_price_usd = data["price_usd"]
                    self.last_updated = "Just now"
                    self.is_loading = False
                else:
                    raise Exception(f"API returned status {response.status_code}")
        except Exception as e:
            self.error_message = f"Error loading price: {str(e)}"
            self.is_loading = False
    
    async def load_history(self):
        """Fetch 5-day price history."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_base_url}/history?days=7")
                if response.status_code == 200:
                    data = response.json()
                    self.historical_data = data["data"]
                else:
                    raise Exception(f"API returned status {response.status_code}")
        except Exception as e:
            self.error_message = f"Error loading history: {str(e)}"
    
    async def load_stats(self):
        """Fetch market statistics."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_base_url}/stats?period=7d")
                if response.status_code == 200:
                    data = response.json()
                    self.high_24h = data["high"]
                    self.low_24h = data["low"]
                    self.avg_24h = data["average"]
                    self.volatility = data["volatility"]
                else:
                    raise Exception(f"API returned status {response.status_code}")
        except Exception as e:
            self.error_message = f"Error loading stats: {str(e)}"
    
    async def load_predictions(self):
        """Fetch price predictions."""
        try:
            import httpx
            from datetime import datetime, timedelta
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_base_url}/predict")
                if response.status_code == 200:
                    data = response.json()
                    self.prediction_24h = data["prediction_24h"]
                    self.prediction_7d = data["prediction_7d"]
                    self.prediction_trend = data["trend"]
                    
                    # Generate 5-day prediction spread
                    current = self.current_price_inr
                    target = self.prediction_7d
                    daily_change = (target - current) / 7
                    
                    self.prediction_5d = []
                    for i in range(1, 6):
                        date = (datetime.now() + timedelta(days=i)).strftime("%b %d")
                        price = round(current + (daily_change * i), 2)
                        self.prediction_5d.append({"date": date, "price": price})
                else:
                    raise Exception(f"API returned status {response.status_code}")
        except Exception as e:
            self.error_message = f"Error loading predictions: {str(e)}"
    
    async def load_all_data(self):
        """Load all data from API."""
        self.is_loading = True
        self.error_message = ""
        
        await self.load_current_price()
        await self.load_history()
        await self.load_stats()
        await self.load_predictions()
        
        # Update calculator
        self.calculate_value()
    
    def calculate_value(self):
        """Calculate total value based on quantity."""
        self.calculated_value = self.current_price_inr * self.quantity
    
    def set_quantity(self, value: str):
        """Update quantity for calculator."""
        try:
            self.quantity = float(value) if value else 0.0
            self.calculate_value()
        except ValueError:
            self.quantity = 0.0
            self.calculated_value = 0.0


def stat_item(label: str, value, color: str = "gray") -> rx.Component:
    """Individual stat item."""
    return rx.vstack(
        rx.text(label, size="2", color="gray"),
        rx.text(value, size="5", weight="bold", color=color),
        spacing="1",
        align="start",
    )


def stats_panel() -> rx.Component:
    """Market statistics panel."""
    return rx.card(
        rx.vstack(
            rx.text("24h Market Stats", size="4", weight="bold"),
            rx.divider(),
            rx.grid(
                stat_item("High", State.high_24h, "green"),
                stat_item("Low", State.low_24h, "red"),
                stat_item("Average", State.avg_24h, "blue"),
                stat_item(
                    "Volatility",
                    rx.text(State.volatility, "%"),
                    "orange"
                ),
                columns="2",
                spacing="4",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
        height="100%",
    )


def price_chart() -> rx.Component:
    """5-day price history chart."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text("5-Day Price History", size="4", weight="bold"),
                rx.spacer(),
                rx.badge("Last 5 days", variant="soft", color_scheme="blue"),
                width="100%",
            ),
            rx.recharts.line_chart(
                rx.recharts.line(
                    data_key="price",
                    stroke="var(--green-9)",
                    stroke_width=2,
                ),
                rx.recharts.x_axis(data_key="date"),
                rx.recharts.y_axis(),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                rx.recharts.tooltip(),
                data=State.historical_data,
                width="100%",
                height=250,
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
    )


def calculator() -> rx.Component:
    """Price calculator (quantity × price)."""
    return rx.card(
        rx.vstack(
            rx.text("Price Calculator", size="4", weight="bold"),
            rx.divider(),
            rx.vstack(
                rx.text("Quantity (BDX)", size="2", color="gray"),
                rx.input(
                    type="number",
                    placeholder="Enter quantity...",
                    value=State.quantity,
                    on_change=State.set_quantity,
                    size="3",
                    width="100%",
                ),
                spacing="2",
                width="100%",
            ),
            rx.hstack(
                rx.icon("x", size=16, color="gray"),
                rx.text(
                    "₹",
                    State.current_price_inr,
                    size="3",
                    color="gray",
                ),
                spacing="2",
            ),
            rx.divider(),
            rx.vstack(
                rx.text("Total Value", size="2", color="gray"),
                rx.heading(
                    "₹ ",
                    rx.cond(
                        State.calculated_value > 0,
                        State.calculated_value,
                        "0.00",
                    ),
                    size="7",
                    weight="bold",
                    color="green",
                ),
                spacing="1",
                align="start",
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
        height="100%",
    )


def prediction_item(label: str, value, icon: str) -> rx.Component:
    """Individual prediction item."""
    return rx.hstack(
        rx.icon(icon, size=20, color="blue"),
        rx.vstack(
            rx.text(label, size="2", color="gray"),
            rx.text(
                "₹",
                value,
                size="4",
                weight="bold",
            ),
            spacing="0",
            align="start",
        ),
        spacing="3",
        align="center",
    )


def prediction_panel() -> rx.Component:
    """Price predictions panel."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text("Price Predictions", size="4", weight="bold"),
                rx.spacer(),
                rx.badge(
                    rx.cond(
                        State.prediction_trend == "bullish",
                        rx.hstack(
                            rx.icon("trending-up", size=12),
                            "Bullish",
                            spacing="1",
                        ),
                        rx.cond(
                            State.prediction_trend == "bearish",
                            rx.hstack(
                                rx.icon("trending-down", size=12),
                                "Bearish",
                                spacing="1",
                            ),
                            rx.hstack(
                                rx.icon("minus", size=12),
                                "Neutral",
                                spacing="1",
                            ),
                        ),
                    ),
                    color_scheme=rx.cond(
                        State.prediction_trend == "bullish",
                        "green",
                        rx.cond(
                            State.prediction_trend == "bearish",
                            "red",
                            "gray",
                        ),
                    ),
                ),
                width="100%",
            ),
            rx.divider(),
            # 5-day forecast grid using rx.foreach
            rx.grid(
                rx.foreach(
                    State.prediction_5d,
                    lambda pred: prediction_item(pred["date"], pred["price"], "calendar"),
                ),
                columns="5",
                spacing="4",
                width="100%",
            ),
            rx.callout(
                "Predictions powered by ML models",
                icon="sparkles",
                size="1",
                variant="soft",
                color_scheme="blue",
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
        height="100%",
    )


def header() -> rx.Component:
    """Header with title and refresh button."""
    return rx.hstack(
        rx.heading("BELLY ", size="8", weight="bold"),
        rx.text(
            "Beldex Real-Time Monitor",
            size="4",
            color="gray",
        ),
        rx.spacer(),
        rx.button(
            rx.icon("refresh-cw", size=18),
            "Refresh",
            on_click=State.load_all_data,
            variant="soft",
            size="3",
        ),
        width="100%",
        align="center",
        padding="1em",
        border_bottom="1px solid var(--gray-5)",
    )


def current_price_card() -> rx.Component:
    """Display current price prominently."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text("Current Price", size="2", weight="bold", color="gray"),
                rx.badge(
                    State.last_updated,
                    variant="soft",
                    size="1",
                ),
                width="100%",
                justify="between",
            ),
            rx.hstack(
                rx.vstack(
                    rx.heading(
                        rx.text("₹", size="5", color="gray", as_="span"),
                        rx.cond(
                            State.is_loading,
                            "...",
                            State.current_price_inr,
                        ),
                        size="9",
                        weight="bold",
                        color="green",
                    ),
                    rx.text(
                        rx.text("$", color="gray", as_="span"),
                        State.current_price_usd,
                        size="4",
                        color="gray",
                    ),
                    align="start",
                    spacing="0",
                ),
                rx.spacer(),
                rx.icon("trending-up", size=48, color="green"),
                width="100%",
                align="center",
            ),
            spacing="3",
            align="start",
        ),
        width="100%",
    )


def dashboard_grid() -> rx.Component:
    """Main dashboard layout."""
    return rx.vstack(
        current_price_card(),
        rx.grid(
            price_chart(),
            stats_panel(),
            columns="2",
            spacing="4",
            width="100%",
        ),
        rx.grid(
            calculator(),
            prediction_panel(),
            columns="2",
            spacing="4",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def index() -> rx.Component:
    """Main page."""
    return rx.container(
        rx.vstack(
            header(),
            rx.cond(
                State.error_message != "",
                rx.callout(
                    State.error_message,
                    icon="alert-circle",
                    color_scheme="red",
                    size="2",
                ),
            ),
            dashboard_grid(),
            spacing="4",
            padding_y="2em",
        ),
        size="4",
        on_mount=State.load_all_data,
    )


# Create the app
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        radius="large",
        accent_color="green",
    )
)

app.add_page(index, title="BELLY - Beldex Monitor")