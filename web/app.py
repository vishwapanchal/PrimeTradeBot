"""Lightweight web server for the trading bot.

Serves a static HTML page with a trading panel and intern details,
plus a JSON API endpoint for placing orders.
"""

import json
import logging
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.logging_config import setup_logging
from bot.orders import execute_order

logger = logging.getLogger(__name__)

WEB_DIR = os.path.dirname(os.path.abspath(__file__))
HOST = "0.0.0.0"
PORT = 8080


class TradingBotHandler(SimpleHTTPRequestHandler):
    """HTTP request handler with API endpoint for order placement."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_POST(self):
        """Handle POST requests to /api/order."""
        if self.path == "/api/order":
            self._handle_order()
        else:
            self.send_error(404, "Not Found")

    def _handle_order(self):
        """Process an order placement request."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)

            logger.info("Web API order request: %s", data)

            response = execute_order(
                symbol=data.get("symbol", ""),
                side=data.get("side", ""),
                order_type=data.get("orderType", ""),
                quantity=data.get("quantity", ""),
                price=data.get("price"),
                stop_price=data.get("stopPrice"),
            )

            self._send_json(200, {
                "success": True,
                "order": {
                    "orderId": response.get("orderId"),
                    "status": response.get("status"),
                    "symbol": response.get("symbol"),
                    "side": response.get("side"),
                    "type": response.get("type"),
                    "origQty": response.get("origQty"),
                    "executedQty": response.get("executedQty"),
                    "price": response.get("price"),
                    "avgPrice": response.get("avgPrice"),
                },
            })

        except ValueError as e:
            logger.warning("Validation error from web: %s", str(e))
            self._send_json(400, {"success": False, "error": str(e)})
        except Exception as e:
            logger.error("Error processing web order: %s", str(e))
            self._send_json(500, {"success": False, "error": str(e)})

    def _send_json(self, status_code: int, data: dict):
        """Send a JSON response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        """Override to use our logger instead of stderr."""
        logger.info("HTTP %s", format % args)


def main():
    """Start the web server."""
    setup_logging()
    server = HTTPServer((HOST, PORT), TradingBotHandler)
    logger.info("Web server starting on http://%s:%d", HOST, PORT)
    print(f"\n  🌐  PrimeTrade Web UI running at http://localhost:{PORT}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
