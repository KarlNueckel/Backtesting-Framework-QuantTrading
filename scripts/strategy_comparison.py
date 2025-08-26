#!/usr/bin/env python3
"""
Strategy Comparison Script

This script compares all 8 strategies on a single stock (GOOGL or NVDA)
and generates a comprehensive comparison chart and table.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
import os
from datetime import datetime

# Add parent directory to path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our framework
from qb.data import load_csv
from qb.strategy import (BuyAndHold, SmaCrossover, RSI, BollingerBands, 
                        MA200, Momentum, ATRTrailingStop, DonchianChannel)
from qb.backtester import Backtester
from qb.metrics import equity_stats

# Strategy configurations
STRATEGIES = [
    {
        'name': 'Buy & Hold',
        'class': BuyAndHold,
        'yaml_file': 'buy_and_hold.yaml',
        'color': '#1f77b4'
    },
    {
        'name': 'SMA Crossover',
        'class': SmaCrossover,
        'yaml_file': 'sma_crossover.yaml',
        'color': '#ff7f0e'
    },
    {
        'name': 'RSI',
        'class': RSI,
        'yaml_file': 'rsi.yaml',
        'color': '#2ca02c'
    },
    {
        'name': 'Bollinger Bands',
        'class': BollingerBands,
        'yaml_file': 'bollinger.yaml',
        'color': '#d62728'
    },
    {
        'name': 'MA200',
        'class': MA200,
        'yaml_file': 'MA200.yaml',
        'color': '#9467bd'
    },
    {
        'name': 'Momentum',
        'class': Momentum,
        'yaml_file': 'momentum.yaml',
        'color': '#8c564b'
    },
    {
        'name': 'ATR Trailing Stop',
        'class': ATRTrailingStop,
        'yaml_file': 'atr_trailing.yaml',
        'color': '#e377c2'
    },
    {
        'name': 'Donchian Channel',
        'class': DonchianChannel,
        'yaml_file': 'donchian.yaml',
        'color': '#7f7f7f'
    }
]

def run_strategy_comparison(ticker='GOOGL'):
    """Run comparison of all strategies on a single stock"""
    
    print(f"Running strategy comparison on {ticker}...")
    
    # Load data
    data = load_csv(f'data/{ticker}.csv')
    print(f"Loaded {len(data)} days of {ticker} data")
    
    # Results storage
    results = []
    equity_curves = {}
    
    # Test each strategy
    for strategy_config in STRATEGIES:
        print(f"Testing {strategy_config['name']}...")
        
        try:
            # Load strategy configuration
            with open(f'strategies/{strategy_config["yaml_file"]}', 'r') as f:
                config = yaml.safe_load(f)
            
            # Create strategy instance
            strategy = strategy_config['class'](**config['params'])
            
            # Run backtest
            backtester = Backtester(data, strategy, initial_cash=config['initial_cash'])
            backtest_results = backtester.run()
            
            # Calculate metrics
            stats = equity_stats(backtest_results['equity'])
            
            # Store results
            result = {
                'Strategy': strategy_config['name'],
                'Total Return (%)': stats['total_return'] * 100,
                'Volatility (%)': stats['volatility'] * 100,
                'Sharpe Ratio': stats['sharpe'],
                'Max Drawdown (%)': stats['max_drawdown'] * 100,
                'Color': strategy_config['color']
            }
            results.append(result)
            
            # Store equity curve
            equity_curves[strategy_config['name']] = backtest_results['equity']
            
        except Exception as e:
            print(f"Error testing {strategy_config['name']}: {e}")
            continue
    
    return results, equity_curves, data

def create_comparison_charts(results, equity_curves, data, ticker):
    """Create comprehensive comparison charts"""
    
    # Set up the plotting style
    plt.style.use('seaborn-v0_8')
    fig = plt.figure(figsize=(20, 16))
    
    # Create subplots
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # 1. Equity Curves Comparison
    ax1 = fig.add_subplot(gs[0, :])
    for strategy_name, equity in equity_curves.items():
        color = next(r['Color'] for r in results if r['Strategy'] == strategy_name)
        ax1.plot(equity.index, equity, label=strategy_name, linewidth=2, color=color)
    
    ax1.set_title(f'{ticker} - Strategy Equity Curves Comparison', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Portfolio Value ($)')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 2. Total Returns Bar Chart
    ax2 = fig.add_subplot(gs[1, 0])
    df_results = pd.DataFrame(results)
    colors = df_results['Color'].tolist()
    bars = ax2.bar(df_results['Strategy'], df_results['Total Return (%)'], color=colors, alpha=0.7)
    ax2.set_title('Total Returns Comparison')
    ax2.set_ylabel('Total Return (%)')
    ax2.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # 3. Sharpe Ratio Comparison
    ax3 = fig.add_subplot(gs[1, 1])
    bars = ax3.bar(df_results['Strategy'], df_results['Sharpe Ratio'], color=colors, alpha=0.7)
    ax3.set_title('Sharpe Ratio Comparison')
    ax3.set_ylabel('Sharpe Ratio')
    ax3.tick_params(axis='x', rotation=45)
    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    
    # 4. Risk-Return Scatter
    ax4 = fig.add_subplot(gs[2, 0])
    for _, row in df_results.iterrows():
        ax4.scatter(row['Volatility (%)'], row['Total Return (%)'], 
                   s=100, alpha=0.7, color=row['Color'], label=row['Strategy'])
        ax4.annotate(row['Strategy'], (row['Volatility (%)'], row['Total Return (%)']), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax4.set_xlabel('Volatility (Risk) (%)')
    ax4.set_ylabel('Total Return (%)')
    ax4.set_title('Risk vs Return')
    ax4.grid(True, alpha=0.3)
    
    # 5. Max Drawdown Comparison
    ax5 = fig.add_subplot(gs[2, 1])
    bars = ax5.bar(df_results['Strategy'], df_results['Max Drawdown (%)'], color=colors, alpha=0.7)
    ax5.set_title('Maximum Drawdown Comparison')
    ax5.set_ylabel('Max Drawdown (%)')
    ax5.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height - 1,
                f'{height:.1f}%', ha='center', va='top', fontsize=9)
    
    plt.suptitle(f'{ticker} - Comprehensive Strategy Comparison', fontsize=18, fontweight='bold')
    plt.tight_layout()
    
    return fig

def create_comparison_table(results):
    """Create a formatted comparison table"""
    
    df = pd.DataFrame(results)
    
    # Round numeric columns
    numeric_cols = ['Total Return (%)', 'Volatility (%)', 
                   'Sharpe Ratio', 'Max Drawdown (%)']
    
    for col in numeric_cols:
        if col in df.columns:
            if 'Ratio' in col or 'Factor' in col:
                df[col] = df[col].round(3)
            else:
                df[col] = df[col].round(2)
    
    # Remove color column for display
    display_df = df.drop('Color', axis=1)
    
    return display_df

def main():
    """Main function"""
    
    # Choose ticker (GOOGL or NVDA)
    ticker = 'GOOGL'  # Change to 'NVDA' for different stock
    
    print(f"Strategy Comparison Analysis")
    print(f"Stock: {ticker}")
    print("=" * 50)
    
    # Run comparison
    results, equity_curves, data = run_strategy_comparison(ticker)
    
    if not results:
        print("No results generated. Exiting.")
        return
    
    # Create comparison table
    comparison_table = create_comparison_table(results)
    
    print(f"\nStrategy Comparison Results for {ticker}:")
    print("=" * 50)
    print(comparison_table.to_string(index=False))
    
    # Save table to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"strategy_comparison_{ticker}_{timestamp}.csv"
    comparison_table.to_csv(csv_filename, index=False)
    print(f"\nComparison table saved to: {csv_filename}")
    
    # Create and save charts
    fig = create_comparison_charts(results, equity_curves, data, ticker)
    
    # Save chart
    chart_filename = f"strategy_comparison_{ticker}_{timestamp}.png"
    fig.savefig(chart_filename, dpi=300, bbox_inches='tight')
    print(f"Comparison chart saved to: {chart_filename}")
    
    # Show the best performing strategies
    df_results = pd.DataFrame(results)
    best_return = df_results.loc[df_results['Total Return (%)'].idxmax()]
    best_sharpe = df_results.loc[df_results['Sharpe Ratio'].idxmax()]
    lowest_drawdown = df_results.loc[df_results['Max Drawdown (%)'].idxmin()]
    
    print(f"\nBest Performers:")
    print(f"- Highest Return: {best_return['Strategy']} ({best_return['Total Return (%)']:.1f}%)")
    print(f"- Best Sharpe Ratio: {best_sharpe['Strategy']} ({best_sharpe['Sharpe Ratio']:.3f})")
    print(f"- Lowest Drawdown: {lowest_drawdown['Strategy']} ({lowest_drawdown['Max Drawdown (%)']:.1f}%)")
    
    plt.show()

if __name__ == "__main__":
    main()
