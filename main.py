"""
Main entry point.
Usage: python main.py [--once|--test|--interval N]
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.orchestrator import NewsFetcherBot
from core.config import log

def main():
    parser = argparse.ArgumentParser(description="Bitcoin News Fetcher Bot — @AdrianJordan_io")
    parser.add_argument("--once", action="store_true", help="Run one cycle")
    parser.add_argument("--test", action="store_true", help="Quick smoke test")
    parser.add_argument("--interval", type=int, default=5, help="Minutes between cycles")
    args = parser.parse_args()

    log.info("╔══════════════════════════════════════════╗")
    log.info("║   Bitcoin News Fetcher Bot v2.0         ║")
    log.info("║   Target: @AdrianJordan_io              ║")
    log.info("║   Primary: Google Search | Secondary: X  ║")
    log.info("╚══════════════════════════════════════════╝")

    bot = NewsFetcherBot()
    if args.test:
        bot.run_cycle()
    elif args.once:
        bot.run_cycle()
    else:
        bot.start()

if __name__ == "__main__":
    main()
