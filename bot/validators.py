"""Input validation for trading bot parameters.

All validators raise ValueError with descriptive messages on invalid input.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

VALID_SIDES = ("BUY", "SELL")
VALID_ORDER_TYPES = ("MARKET", "LIMIT", "STOP_LIMIT")


def validate_symbol(symbol: str) -> str:
    """Validate and normalize trading symbol.

    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')

    Returns:
        Uppercased symbol string

    Raises:
        ValueError: If symbol is empty or contains invalid characters
    """
    if not symbol or not symbol.strip():
        raise ValueError("Symbol cannot be empty.")
    cleaned = symbol.strip().upper()
    if not cleaned.isalpha():
        raise ValueError(f"Symbol must contain only letters, got: '{symbol}'")
    if len(cleaned) < 5:
        raise ValueError(f"Symbol too short (min 5 chars), got: '{cleaned}'")
    logger.debug("Validated symbol: %s", cleaned)
    return cleaned


def validate_side(side: str) -> str:
    """Validate order side.

    Args:
        side: Order side ('BUY' or 'SELL')

    Returns:
        Uppercased side string

    Raises:
        ValueError: If side is not BUY or SELL
    """
    if not side:
        raise ValueError("Side cannot be empty.")
    cleaned = side.strip().upper()
    if cleaned not in VALID_SIDES:
        raise ValueError(f"Side must be one of {VALID_SIDES}, got: '{side}'")
    logger.debug("Validated side: %s", cleaned)
    return cleaned


def validate_order_type(order_type: str) -> str:
    """Validate order type.

    Args:
        order_type: Order type ('MARKET', 'LIMIT', or 'STOP_LIMIT')

    Returns:
        Uppercased order type string

    Raises:
        ValueError: If order type is not recognized
    """
    if not order_type:
        raise ValueError("Order type cannot be empty.")
    cleaned = order_type.strip().upper().replace("-", "_")
    if cleaned not in VALID_ORDER_TYPES:
        raise ValueError(f"Order type must be one of {VALID_ORDER_TYPES}, got: '{order_type}'")
    logger.debug("Validated order type: %s", cleaned)
    return cleaned


def validate_quantity(quantity: str | float) -> float:
    """Validate order quantity.

    Args:
        quantity: Order quantity (must be a positive number)

    Returns:
        Quantity as float

    Raises:
        ValueError: If quantity is not a positive number
    """
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Quantity must be a number, got: '{quantity}'")
    if qty <= 0:
        raise ValueError(f"Quantity must be positive, got: {qty}")
    logger.debug("Validated quantity: %s", qty)
    return qty


def validate_price(price: Optional[str | float], order_type: str) -> Optional[float]:
    """Validate price based on order type.

    Args:
        price: Order price (required for LIMIT/STOP_LIMIT orders)
        order_type: The order type to determine if price is required

    Returns:
        Price as float, or None for MARKET orders

    Raises:
        ValueError: If price is required but missing/invalid
    """
    requires_price = order_type in ("LIMIT", "STOP_LIMIT")

    if requires_price:
        if price is None or (isinstance(price, str) and not price.strip()):
            raise ValueError(f"Price is required for {order_type} orders.")
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValueError(f"Price must be a number, got: '{price}'")
        if p <= 0:
            raise ValueError(f"Price must be positive, got: {p}")
        logger.debug("Validated price: %s", p)
        return p

    return None


def validate_stop_price(stop_price: Optional[str | float], order_type: str) -> Optional[float]:
    """Validate stop price for stop-limit orders.

    Args:
        stop_price: Stop trigger price
        order_type: The order type

    Returns:
        Stop price as float, or None if not applicable

    Raises:
        ValueError: If stop price is required but missing/invalid
    """
    if order_type != "STOP_LIMIT":
        return None
    if stop_price is None or (isinstance(stop_price, str) and not stop_price.strip()):
        raise ValueError("Stop price is required for STOP_LIMIT orders.")
    try:
        sp = float(stop_price)
    except (ValueError, TypeError):
        raise ValueError(f"Stop price must be a number, got: '{stop_price}'")
    if sp <= 0:
        raise ValueError(f"Stop price must be positive, got: {sp}")
    logger.debug("Validated stop price: %s", sp)
    return sp
