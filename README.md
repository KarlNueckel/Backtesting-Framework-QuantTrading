# Backtesting Framework for Quantitative Trading

A comprehensive Python framework for backtesting quantitative trading strategies with support for multiple strategies, performance metrics, and automated reporting.

## Features

- **Multiple Trading Strategies**: 8 different strategies with distinct approaches
- **Comprehensive Metrics**: Sharpe ratio, maximum drawdown, returns, volatility
- **Automated Reporting**: HTML reports with interactive charts and performance visualizations
- **Batch Processing**: Run multiple strategies across different parameters
- **Data Management**: Automated data fetching and caching
- **CLI Interface**: Easy-to-use command-line tools
- **Jupyter Notebooks**: Detailed analysis notebooks for each strategy

## Project Structure

```
Backtesting-Framework-QuantTrading/
├── qb/                    # Core backtesting engine
│   ├── backtester.py     # Main backtesting logic
│   ├── data.py           # Data loading and management
│   ├── metrics.py        # Performance calculations
│   └── strategy.py       # Strategy base classes
├── strategies/           # Strategy configurations (YAML files)
│   ├── buy_and_hold.yaml
│   ├── sma_crossover.yaml
│   ├── rsi.yaml
│   ├── bollinger.yaml
│   ├── MA200.yaml
│   ├── momentum.yaml
│   ├── atr_trailing.yaml
│   └── donchian.yaml
├── scripts/              # Utility scripts
│   ├── fetch_data.py     # Data fetching
│   ├── generate_report.py # Report generation
│   ├── run_all_strategies.py # Batch processing
│   ├── create_notebooks.py # Jupyter notebook generation
│   └── strategy_comparison.py # Strategy comparison
├── tests/                # Test suite
│   ├── test_strategies.py # Strategy tests
│   └── test_backtester.py # Backtester tests
├── notebooks/            # Jupyter notebooks for analysis
├── cli/                  # Command-line interface
│   └── run_batch.py      # Batch execution CLI
├── data/                 # Stock data (gitignored)
├── reports/              # Generated reports (gitignored)
├── main.py               # Main entry point
├── setup.py              # Package setup
└── CONTRIBUTING.md       # Contributing guidelines
```

## Quick Start

### Option 1: Using the Main Script (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt

# Fetch stock data
python main.py fetch-data

# Run all strategies on all stocks
python main.py run-all

# Compare all strategies on a specific stock
python main.py compare --stock GOOGL

# Generate comprehensive HTML report
python main.py report

# Run tests
python main.py test
```

### Option 2: Using Individual Scripts
```bash
# Install dependencies
pip install -r requirements.txt

# Fetch data
python scripts/fetch_data.py

# Run a single strategy
python cli/run_batch.py --strategy sma_crossover --symbol SPY

# Run all strategies
python scripts/run_all_strategies.py

# Generate report
python scripts/generate_report.py
```

## Available Strategies

| Strategy | Type | Description | Key Parameters |
|----------|------|-------------|----------------|
| **Buy & Hold** | Baseline | Buy once at the beginning and hold until the end | Allocate: 100% |
| **SMA Crossover** | Trend Following | Buy when fast MA crosses above slow MA (golden cross) | Fast: 20d, Slow: 50d |
| **RSI** | Mean Reversion | Buy when oversold (RSI < 30), sell when overbought (RSI > 70) | Period: 14d, Thresholds: 30/70 |
| **Bollinger Bands** | Mean Reversion | Buy at lower band, sell at upper band | Window: 20d, Std Dev: 2.0 |
| **MA200** | Trend Following | Buy above 200-day MA, sell below 200-day MA | Window: 200d |
| **Momentum** | Trend Following | Buy on positive momentum, sell on negative momentum | Lookback: 90d |
| **ATR Trailing Stop** | Risk Management | Dynamic trailing stops using ATR for position sizing | Window: 14d, Multiplier: 3.0 |
| **Donchian Channel** | Breakout | Buy on upper channel breakout, sell on lower channel breakout | Window: 20d, Tolerance: 1% |

## Configuration

Strategies are configured using YAML files in the `strategies/` directory. Each strategy can be customized with different parameters like:

- Initial cash amount
- Lookback periods
- Threshold values
- Risk management rules

## Reports

The framework generates comprehensive HTML reports including:
- Performance charts
- Risk-return scatter plots
- Sharpe ratio heatmaps
- Strategy comparisons

Reports are automatically saved to the `reports/` directory with timestamps.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your strategy or improvements
4. Submit a pull request

## License

This project is open source and available under the MIT License.