"""Order placement logic and response formatting.

Provides the high-level orchestrator for placing orders, mapping
validated inputs to client methods and formatting responses.
"""

import logging
from typing import Any, Dict, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from bot.client import BinanceFuturesClient
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

logger = logging.getLogger(__name__)
console = Console()


def format_order_summary(
    symbol: str, side: str, order_type: str,
    quantity: float, price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> Table:
    """Create a rich table summarizing the order request.

    Returns:
        Rich Table object for display
    """
    table = Table(title="📋 Order Request Summary", show_header=False, border_style="cyan")
    table.add_column("Field", style="bold white")
    table.add_column("Value", style="green")

    table.add_row("Symbol", symbol)
    table.add_row("Side", f"[{'green' if side == 'BUY' else 'red'}]{side}[/]")
    table.add_row("Type", order_type)
    table.add_row("Quantity", str(quantity))
    if price is not None:
        table.add_row("Price", str(price))
    if stop_price is not None:
        table.add_row("Stop Price", str(stop_price))

    return table


def format_order_response(response: Dict[str, Any]) -> Table:
    """Create a rich table with order response details.

    Returns:
        Rich Table object for display
    """
    table = Table(title="📊 Order Response", show_header=False, border_style="green")
    table.add_column("Field", style="bold white")
    table.add_column("Value", style="yellow")

    fields = [
        ("Order ID", "orderId"),
        ("Status", "status"),
        ("Symbol", "symbol"),
        ("Side", "side"),
        ("Type", "type"),
        ("Quantity", "origQty"),
        ("Executed Qty", "executedQty"),
        ("Price", "price"),
        ("Avg Price", "avgPrice"),
        ("Time in Force", "timeInForce"),
        ("Working Type", "workingType"),
    ]

    for label, key in fields:
        value = response.get(key)
        if value is not None:
            table.add_row(label, str(value))

    return table


def execute_order(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: Optional[str | float] = None,
    stop_price: Optional[str | float] = None,
) -> Dict[str, Any]:
    """Execute an order with full validation, logging and formatted output.

    This is the main entry point for order placement from both CLI and web UI.

    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        side: 'BUY' or 'SELL'
        order_type: 'MARKET', 'LIMIT', or 'STOP_LIMIT'
        quantity: Order quantity
        price: Limit price (required for LIMIT/STOP_LIMIT)
        stop_price: Stop trigger price (required for STOP_LIMIT)

    Returns:
        Order response dictionary

    Raises:
        ValueError: On validation errors
        Exception: On API/network errors
    """
    # ── Validate all inputs ──────────────────────────────────────
    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_type = validate_order_type(order_type)
    validated_qty = validate_quantity(quantity)
    validated_price = validate_price(price, validated_type)
    validated_stop = validate_stop_price(stop_price, validated_type)

    # ── Print request summary ────────────────────────────────────
    summary_table = format_order_summary(
        validated_symbol, validated_side, validated_type,
        validated_qty, validated_price, validated_stop,
    )
    console.print()
    console.print(summary_table)
    console.print()

    logger.info(
        "Executing order — symbol=%s side=%s type=%s qty=%s price=%s stop=%s",
        validated_symbol, validated_side, validated_type,
        validated_qty, validated_price, validated_stop,
    )

    # ── Place the order ──────────────────────────────────────────
    client = BinanceFuturesClient()

    if validated_type == "MARKET":
        response = client.place_market_order(validated_symbol, validated_side, validated_qty)
    elif validated_type == "LIMIT":
        response = client.place_limit_order(
            validated_symbol, validated_side, validated_qty, validated_price
        )
    elif validated_type == "STOP_LIMIT":
        response = client.place_stop_limit_order(
            validated_symbol, validated_side, validated_qty,
            validated_price, validated_stop
        )
    else:
        raise ValueError(f"Unsupported order type: {validated_type}")

    # ── Print response ───────────────────────────────────────────
    response_table = format_order_response(response)
    console.print(response_table)
    console.print()

    status = response.get("status", "UNKNOWN")
    order_id = response.get("orderId", "N/A")

    if status in ("NEW", "FILLED", "PARTIALLY_FILLED"):
        console.print(Panel(
            f"[bold green]✅ Order placed successfully![/]\n"
            f"Order ID: [cyan]{order_id}[/] | Status: [yellow]{status}[/]",
            border_style="green",
        ))
        logger.info("Order successful — orderId=%s status=%s", order_id, status)
    else:
        console.print(Panel(
            f"[bold yellow]⚠️ Order returned unexpected status[/]\n"
            f"Order ID: [cyan]{order_id}[/] | Status: [red]{status}[/]",
            border_style="yellow",
        ))
        logger.warning("Order returned unexpected status — orderId=%s status=%s", order_id, status)

    return response
