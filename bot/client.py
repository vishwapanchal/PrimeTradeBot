"""Binance Futures Testnet client wrapper.

Provides a clean interface to the Binance Futures Testnet API
with comprehensive logging and error handling.
"""

import logging
import os
from typing import Any, Dict, Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceFuturesClient:
    """Wrapper around python-binance for Futures Testnet operations."""

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Initialize the Binance Futures Testnet client.

        Args:
            api_key: Binance testnet API key (falls back to env var)
            api_secret: Binance testnet API secret (falls back to env var)

        Raises:
            ValueError: If API credentials are missing
        """
        load_dotenv()

        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")

        if not self.api_key or not self.api_secret:
            raise ValueError(
                "API credentials not found. Set BINANCE_API_KEY and BINANCE_API_SECRET "
                "in your .env file or pass them directly."
            )

        logger.info("Initializing Binance Futures Testnet client")
        self.client = Client(
            api_key=self.api_key,
            api_secret=self.api_secret,
            testnet=True,
        )
        # Override futures base URL for testnet
        self.client.FUTURES_URL = TESTNET_BASE_URL + "/fapi"
        logger.info("Client initialized successfully — testnet: %s", TESTNET_BASE_URL)

    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """Place a MARKET order on Binance Futures Testnet.

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity

        Returns:
            Order response dictionary from Binance API

        Raises:
            BinanceAPIException: On API-level errors
            BinanceRequestException: On network/request errors
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": quantity,
        }
        logger.info("Placing MARKET order — %s", params)

        try:
            response = self.client.futures_create_order(**params)
            logger.info("MARKET order response — orderId: %s, status: %s",
                        response.get("orderId"), response.get("status"))
            logger.debug("Full response: %s", response)
            return response
        except BinanceAPIException as e:
            logger.error("Binance API error [%s]: %s", e.code, e.message)
            raise
        except BinanceRequestException as e:
            logger.error("Binance request error: %s", str(e))
            raise
        except Exception as e:
            logger.error("Unexpected error placing MARKET order: %s", str(e))
            raise

    def place_limit_order(
        self, symbol: str, side: str, quantity: float, price: float,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """Place a LIMIT order on Binance Futures Testnet.

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force (default GTC)

        Returns:
            Order response dictionary from Binance API
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": "LIMIT",
            "quantity": quantity,
            "price": price,
            "timeInForce": time_in_force,
        }
        logger.info("Placing LIMIT order — %s", params)

        try:
            response = self.client.futures_create_order(**params)
            logger.info("LIMIT order response — orderId: %s, status: %s",
                        response.get("orderId"), response.get("status"))
            logger.debug("Full response: %s", response)
            return response
        except BinanceAPIException as e:
            logger.error("Binance API error [%s]: %s", e.code, e.message)
            raise
        except BinanceRequestException as e:
            logger.error("Binance request error: %s", str(e))
            raise
        except Exception as e:
            logger.error("Unexpected error placing LIMIT order: %s", str(e))
            raise

    def place_stop_limit_order(
        self, symbol: str, side: str, quantity: float,
        price: float, stop_price: float, time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """Place a STOP_LIMIT (STOP) order on Binance Futures Testnet.

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            price: Limit price
            stop_price: Stop trigger price
            time_in_force: Time in force (default GTC)

        Returns:
            Order response dictionary from Binance API
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": "STOP",
            "quantity": quantity,
            "price": price,
            "stopPrice": stop_price,
            "timeInForce": time_in_force,
        }
        logger.info("Placing STOP_LIMIT order — %s", params)

        try:
            response = self.client.futures_create_order(**params)
            logger.info("STOP_LIMIT order response — orderId: %s, status: %s",
                        response.get("orderId"), response.get("status"))
            logger.debug("Full response: %s", response)
            return response
        except BinanceAPIException as e:
            logger.error("Binance API error [%s]: %s", e.code, e.message)
            raise
        except BinanceRequestException as e:
            logger.error("Binance request error: %s", str(e))
            raise
        except Exception as e:
            logger.error("Unexpected error placing STOP_LIMIT order: %s", str(e))
            raise

    def get_account_info(self) -> Dict[str, Any]:
        """Get futures account information.

        Returns:
            Account info dictionary
        """
        logger.info("Fetching futures account info")
        try:
            info = self.client.futures_account()
            logger.info("Account info retrieved — total balance: %s USDT",
                        info.get("totalWalletBalance", "N/A"))
            return info
        except Exception as e:
            logger.error("Error fetching account info: %s", str(e))
            raise
