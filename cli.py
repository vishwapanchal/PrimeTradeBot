"""CLI entry point for the Binance Futures Testnet Trading Bot.

Provides both direct command-line arguments and an interactive menu mode.
Uses Click for CLI framework and Rich for styled output.
"""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from bot.logging_config import setup_logging
from bot.orders import execute_order

console = Console()

BANNER = r"""
  ╔═══════════════════════════════════════════════╗
  ║   🚀  PrimeTrade — Binance Futures Bot  🚀   ║
  ║        Testnet (USDT-M) Trading CLI           ║
  ╚═══════════════════════════════════════════════╝
"""


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """PrimeTrade — Binance Futures Testnet Trading Bot CLI."""
    setup_logging()
    if ctx.invoked_subcommand is None:
        console.print(Text(BANNER, style="bold cyan"))
        console.print("Use [bold]'python cli.py order'[/] to place an order,")
        console.print("or  [bold]'python cli.py interactive'[/] for guided mode.\n")
        console.print("Run [bold]'python cli.py --help'[/] for all options.\n")


@cli.command()
@click.option("--symbol", "-s", required=True, help="Trading pair (e.g., BTCUSDT)")
@click.option("--side", "-d", required=True, type=click.Choice(["BUY", "SELL"], case_sensitive=False), help="Order side")
@click.option("--order-type", "-t", required=True, type=click.Choice(["MARKET", "LIMIT", "STOP_LIMIT"], case_sensitive=False), help="Order type")
@click.option("--quantity", "-q", required=True, type=float, help="Order quantity")
@click.option("--price", "-p", type=float, default=None, help="Limit price (required for LIMIT/STOP_LIMIT)")
@click.option("--stop-price", "-sp", type=float, default=None, help="Stop trigger price (required for STOP_LIMIT)")
def order(symbol, side, order_type, quantity, price, stop_price):
    """Place an order on Binance Futures Testnet.

    Examples:

        python cli.py order --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001

        python cli.py order -s ETHUSDT -d SELL -t LIMIT -q 0.01 -p 3000

        python cli.py order -s BTCUSDT -d BUY -t STOP_LIMIT -q 0.001 -p 50000 -sp 49000
    """
    try:
        execute_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except ValueError as e:
        console.print(Panel(
            f"[bold red]❌ Validation Error[/]\n{str(e)}",
            border_style="red",
        ))
        logger_exit(1)
    except Exception as e:
        console.print(Panel(
            f"[bold red]❌ Error[/]\n{type(e).__name__}: {str(e)}",
            border_style="red",
        ))
        logger_exit(1)


@cli.command()
def interactive():
    """Interactive guided mode for placing orders."""
    console.print(Text(BANNER, style="bold cyan"))
    console.print(Panel(
        "[bold]Welcome to Interactive Trading Mode[/]\n"
        "Follow the prompts below to place an order.",
        border_style="cyan",
    ))

    while True:
        try:
            console.print()
            symbol = Prompt.ask(
                "[bold cyan]Symbol[/] (e.g., BTCUSDT)",
                default="BTCUSDT",
            )

            side = Prompt.ask(
                "[bold cyan]Side[/]",
                choices=["BUY", "SELL"],
                default="BUY",
            )

            order_type = Prompt.ask(
                "[bold cyan]Order Type[/]",
                choices=["MARKET", "LIMIT", "STOP_LIMIT"],
                default="MARKET",
            )

            quantity = Prompt.ask("[bold cyan]Quantity[/]")

            price = None
            stop_price = None

            if order_type in ("LIMIT", "STOP_LIMIT"):
                price = Prompt.ask("[bold cyan]Price[/]")

            if order_type == "STOP_LIMIT":
                stop_price = Prompt.ask("[bold cyan]Stop Price[/]")

            # Confirm before placing
            console.print()
            confirm = Prompt.ask(
                "[bold yellow]Place this order?[/]",
                choices=["y", "n"],
                default="y",
            )

            if confirm.lower() != "y":
                console.print("[dim]Order cancelled.[/]")
                continue

            execute_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                stop_price=stop_price,
            )

        except ValueError as e:
            console.print(Panel(
                f"[bold red]❌ Validation Error[/]\n{str(e)}",
                border_style="red",
            ))
        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye! 👋[/]")
            break
        except Exception as e:
            console.print(Panel(
                f"[bold red]❌ Error[/]\n{type(e).__name__}: {str(e)}",
                border_style="red",
            ))

        # Ask to continue
        console.print()
        again = Prompt.ask(
            "[bold cyan]Place another order?[/]",
            choices=["y", "n"],
            default="y",
        )
        if again.lower() != "y":
            console.print("[dim]Goodbye! 👋[/]")
            break


def logger_exit(code: int):
    """Exit with a return code."""
    sys.exit(code)


if __name__ == "__main__":
    cli()
