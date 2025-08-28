#!/usr/bin/env python3
"""
Tests for the backtester module
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qb.backtester import Backtester
from qb.strategy import BuyAndHold, SmaCrossover
from qb.metrics import equity_stats

class TestBacktester(unittest.TestCase):
    """Test cases for the Backtester class"""
    
    def setUp(self):
        """Set up test data"""
        # Create simple test data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        
        # Create a simple price series with some trends
        np.random.seed(42)
        base_price = 100
        trend = np.linspace(0, 20, 100)
        noise = np.random.normal(0, 2, 100)
        close_prices = base_price + trend + noise
        
        self.test_data = pd.DataFrame({
            'Open': close_prices * 0.99,
            'High': close_prices * 1.02,
            'Low': close_prices * 0.98,
            'Close': close_prices,
            'Volume': np.random.randint(1000000, 5000000, 100)
        }, index=dates)
    
    def test_backtester_initialization(self):
        """Test backtester initialization"""
        strategy = BuyAndHold(allocate=1.0)
        backtester = Backtester(self.test_data, strategy, initial_cash=100000)
        
        self.assertEqual(backtester.initial_cash, 100000)
        self.assertEqual(len(backtester.equity), len(self.test_data))
        self.assertEqual(backtester.equity.iloc[0], 100000)
    
    def test_buy_and_hold_backtest(self):
        """Test buy and hold strategy backtest"""
        strategy = BuyAndHold(allocate=1.0)
        backtester = Backtester(self.test_data, strategy, initial_cash=100000)
        results = backtester.run()
        
        # Check that we have equity curve
        self.assertIn('equity', results)
        self.assertEqual(len(results['equity']), len(self.test_data))
        
        # Check that equity starts at initial cash
        self.assertEqual(results['equity'].iloc[0], 100000)
        
        # Check that equity changes over time
        self.assertNotEqual(results['equity'].iloc[-1], 100000)
    
    def test_sma_crossover_backtest(self):
        """Test SMA crossover strategy backtest"""
        strategy = SmaCrossover(fast=5, slow=10, allocate=1.0)
        backtester = Backtester(self.test_data, strategy, initial_cash=100000)
        results = backtester.run()
        
        # Check that we have equity curve
        self.assertIn('equity', results)
        self.assertEqual(len(results['equity']), len(self.test_data))
        
        # Check that equity starts at initial cash
        self.assertEqual(results['equity'].iloc[0], 100000)
    
    def test_get_trades(self):
        """Test getting trade information"""
        strategy = SmaCrossover(fast=5, slow=10, allocate=1.0)
        backtester = Backtester(self.test_data, strategy, initial_cash=100000)
        backtester.run()
        
        trades = backtester.get_trades()
        
        # Should return a list
        self.assertIsInstance(trades, list)
        
        # If there are trades, they should have the right structure
        if trades:
            trade = trades[0]
            self.assertIn('entry_date', trade)
            self.assertIn('exit_date', trade)
            self.assertIn('entry_price', trade)
            self.assertIn('exit_price', trade)
            self.assertIn('return', trade)
    
    def test_metrics_calculation(self):
        """Test that metrics can be calculated from backtest results"""
        strategy = BuyAndHold(allocate=1.0)
        backtester = Backtester(self.test_data, strategy, initial_cash=100000)
        results = backtester.run()
        
        # Calculate metrics
        stats = equity_stats(results['equity'])
        
        # Check that all required metrics are present
        required_metrics = ['total_return', 'volatility', 'sharpe', 'max_drawdown']
        for metric in required_metrics:
            self.assertIn(metric, stats)
            self.assertIsInstance(stats[metric], (int, float))

if __name__ == "__main__":
    unittest.main()
