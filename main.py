"""
Main entry point for the Bitcoin News Fetcher Bot.

Usage:
    python main.py              # Run continuously (5-min intervals)
    python main.py --once       # Run one cycle and exit
    python main.py --test       # Quick smoke test
"""

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.orchestrator import NewsFetcherBot
from core.config import log, FETCH_INTERVAL_MINUTES


def main():
    parser = argparse.ArgumentParser(
        description="Bitcoin News Fetcher Bot — @AdrianJordan_io"
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Run one cycle and exit"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Quick smoke test (no posting)"
    )
    parser.add_argument(
        "--interval", type=int, default=FETCH_INTERVAL_MINUTES,
        help=f"Polling interval in minutes (default: {FETCH_INTERVAL_MINUTES})"
    )
    args = parser.parse_args()

    log.info("╔══════════════════════════════════════════╗")
    log.info("║   Bitcoin News Fetcher Bot v2.0         ║")
    log.info("║   Target: @AdrianJordan_io              ║")
    log.info("║   Sources: X + Google + SEC EDGAR       ║")
    log.info("╚══════════════════════════════════════════╝")

    bot = NewsFetcherBot()

    if args.test:
        log.info("── TEST MODE: Running single cycle (no posting) ──")
        bot.run_cycle()
        log.info("── TEST COMPLETE ──")
        return

    if args.once:
        log.info("── SINGLE CYCLE MODE ──")
        bot.run_cycle()
        return

    # Continuous mode
    log.info(f"── CONTINUOUS MODE (every {args.interval} min) ──")
    bot.start()


if __name__ == "__main__":
    main()
