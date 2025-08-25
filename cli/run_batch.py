# cli/run_batch.py
#
# This script lets you test the SAME trading strategy across MULTIPLE stocks at once.
# Example usage:
#   python -m cli.run_batch --tickers GOOGL WMT AMD NVDA --config strategies/sma_crossover.yaml
#
# What happens when you run it:
#   1. It opens each stock's historical price data (CSV in your data/ folder).
#   2. It applies your strategy (example: moving average crossover).
#   3. It simulates "pretend trades" over time (backtesting).
#   4. It collects results like profit, risk, and worst loss.
#   5. It prints a comparison table AND saves results to batch_stats.csv.
#
# The goal: let you quickly compare how well the same strategy works
#           on different stocks (steady WMT vs volatile NVDA, etc.).

import argparse
import pandas as pd
import yaml

# Import our framework modules
from qb.data import load_csv       # loads price data (OHLCV) into pandas DataFrame
from qb.strategy import SmaCrossover, BuyAndHold, RSI, BollingerBands  # strategies: SMA crossover, buy & hold, RSI, and Bollinger Bands
from qb.backtester import Backtester  # runs the backtest "simulation loop"
from qb.metrics import equity_stats   # calculates performance metrics (returns, sharpe, etc.)


def run_one(ticker: str, config_path: str) -> dict:
    """
    Run the backtest for a single ticker (like 'GOOGL').

    Steps:
      1. Load the strategy settings from the config YAML file.
      2. Load that stock's historical price data from data/{ticker}.csv.
      3. Apply the chosen strategy to that data.
      4. Run the backtest to simulate trades and track account value.
      5. Calculate summary statistics (return, risk, drawdowns).
      6. Return those stats as a dictionary.
    """
    # Load strategy parameters from YAML (e.g. fast=20, slow=50 for SMA crossover)
    cfg = yaml.safe_load(open(config_path))

    # Load price data for this ticker (expects file like data/GOOGL.csv)
    df = load_csv(f"data/{ticker}.csv")

    # Build the strategy object with chosen parameters
    strategy_name = cfg.get("name", "sma_crossover")
    if strategy_name == "sma_crossover":
        strat = SmaCrossover(**cfg["params"])
    elif strategy_name == "buy_and_hold":
        strat = BuyAndHold(**cfg["params"])
    elif strategy_name == "rsi":
        strat = RSI(**cfg["params"])
    elif strategy_name == "bollinger":
        strat = BollingerBands(**cfg["params"])
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    # Create the backtester, starting with $100,000 "pretend money"
    bt = Backtester(df, strat, initial_cash=cfg.get("initial_cash", 100_000))

    # Run the backtest: this simulates day-by-day (or bar-by-bar) trading
    equity = bt.run()

    # Calculate stats about performance
    stats = equity_stats(equity["equity"])
    stats["ticker"] = ticker  # tag results with ticker name

    return stats


if __name__ == "__main__":
    # Argument parser so you can run from the command line
    p = argparse.ArgumentParser()
    # Default tickers if you don't pass any: GOOGL, WMT, AMD
    p.add_argument("--tickers", nargs="+", default=["GOOGL", "WMT", "AMD"])
    # Config file with strategy parameters (YAML)
    p.add_argument("--config", default="strategies/sma_crossover.yaml")
    args = p.parse_args()

    # Run the backtest for each ticker the user requested
    rows = [run_one(t, args.config) for t in args.tickers]

    # Put all results into a single DataFrame for comparison
    df = pd.DataFrame(rows)[["ticker", "total_return", "volatility", "sharpe", "max_drawdown"]]

    # Print results as a nice table in the terminal
    print("\n=== Batch Backtest Results ===")
    print(df.to_string(index=False))

    # Save results to CSV with strategy name in filename
    strategy_name = yaml.safe_load(open(args.config)).get("name", "unknown")
    output_file = f"batch_stats_{strategy_name}.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved results to {output_file}")
