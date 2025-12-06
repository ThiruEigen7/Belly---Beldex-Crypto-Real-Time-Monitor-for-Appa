"""
Price chart component - 5-day historical view
"""
import reflex as rx
from .. import belly

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
            # Recharts line chart
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
                data=belly.State.historical_data,
                width="100%",
                height=250,
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
    )