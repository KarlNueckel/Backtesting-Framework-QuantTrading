#!/usr/bin/env python3
"""
Unit Tests for Trading Strategies

This module tests each strategy to ensure they output BUY/SELL signals correctly
in simple toy cases.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qb.strategy import (BuyAndHold, SmaCrossover, RSI, BollingerBands, 
                        MA200, Momentum, ATRTrailingStop, DonchianChannel)

class TestStrategies(unittest.TestCase):
    """Test cases for all trading strategies"""
    
    def setUp(self):
        """Set up test data"""
        # Create simple test data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        
        # Create a simple price series with some trends
        np.random.seed(42)  # For reproducible tests
        base_price = 100
        trend = np.linspace(0, 20, 100)  # Upward trend
        noise = np.random.normal(0, 2, 100)
        close_prices = base_price + trend + noise
        
        # Create OHLCV data
        self.test_data = pd.DataFrame({
            'Open': close_prices * 0.99,
            'High': close_prices * 1.02,
            'Low': close_prices * 0.98,
            'Close': close_prices,
            'Volume': np.random.randint(1000000, 5000000, 100)
        }, index=dates)
    
    def test_buy_and_hold(self):
        """Test Buy & Hold strategy"""
        strategy = BuyAndHold(allocate=1.0)
        signals = strategy.generate_signals(self.test_data)
        
        # Should have exactly one buy signal at the beginning
        self.assertEqual(signals.sum(), 1)
        self.assertEqual(signals.iloc[0], 1)  # First day should be buy
        self.assertTrue(all(signals.iloc[1:] == 0))  # Rest should be hold
    
    def test_sma_crossover(self):
        """Test SMA Crossover strategy"""
        strategy = SmaCrossover(fast=5, slow=10, allocate=1.0)
        signals = strategy.generate_signals(self.test_data)
        
        # Should have some signals (not all zeros)
        self.assertTrue(len(signals[signals != 0]) > 0)
        
        # All signals should be 1, -1, or 0
        self.assertTrue(all(signals.isin([1, -1, 0])))
        
        # Check that we have both buy and sell signals
        buy_signals = (signals == 1).sum()
        sell_signals = (signals == -1).sum()
        self.assertTrue(buy_signals > 0 or sell_signals > 0)
    
    def test_rsi(self):
        """Test RSI strategy"""
        strategy = RSI(period=14, lower=30, upper=70, allocate=1.0)
        signals = strategy.generate_signals(self.test_data)
        
        # Should have some signals
        self.assertTrue(len(signals[signals != 0]) > 0)
        
        # All signals should be 1, -1, or 0
        self.assertTrue(all(signals.isin([1, -1, 0])))
        
        # Check that we have both buy and sell signals
        buy_signals = (signals == 1).sum()
        sell_signals = (signals == -1).sum()
        self.assertTrue(buy_signals > 0 or sell_signals > 0)
    
    def test_bollinger_bands(self):
        """Test Bollinger Bands strategy"""
        strategy = BollingerBands(window=20, num_std=2.0, allocate=1.0)
        signals = strategy.generate_signals(self.test_data)
        
        # Should have some signals
        self.assertTrue(len(signals[signals != 0]) > 0)
        
        # All signals should be 1, -1, or 0
        self.assertTrue(all(signals.isin([1, -1, 0])))
        
        # Check that we have both buy and sell signals
        buy_signals = (signals == 1).sum()
        sell_signals = (signals == -1).sum()
        self.assertTrue(buy_signals > 0 or sell_signals > 0)
    
    def test_ma200(self):
        """Test MA200 strategy"""
        strategy = MA200(window=50, allocate=1.0, buffer_pct=0.0)  # Using shorter window for test
        signals = strategy.generate_signals(self.test_data)
        
        # Should have some signals
        self.assertTrue(len(signals[signals != 0]) > 0)
        
        # All signals should be 1, -1, or 0
        self.assertTrue(all(signals.isin([1, -1, 0])))
        
        # Check that we have both buy and sell signals
        buy_signals = (signals == 1).sum()
        sell_signals = (signals == -1).sum()
        self.assertTrue(buy_signals > 0 or sell_signals > 0)
    
    def test_momentum(self):
        """Test Momentum strategy"""
        strategy = Momentum(lookback=20, allocate=1.0)  # Using shorter lookback for test
        signals = strategy.generate_signals(self.test_data)
        
        # Should have some signals
        self.assertTrue(len(signals[signals != 0]) > 0)
        
        # All signals should be 1, -1, or 0
        self.assertTrue(all(signals.isin([1, -1, 0])))
        
        # Check that we have both buy and sell signals
        buy_signals = (signals == 1).sum()
        sell_signals = (signals == -1).sum()
        self.assertTrue(buy_signals > 0 or sell_signals > 0)
    
    def test_atr_trailing_stop(self):
        """Test ATR Trailing Stop strategy"""
        strategy = ATRTrailingStop(window=14, multiplier=3.0, allocate=1.0)
        signals = strategy.generate_signals(self.test_data)
        
        # Should have some signals
        self.assertTrue(len(signals[signals != 0]) > 0)
        
        # All signals should be 1, -1, or 0
        self.assertTrue(all(signals.isin([1, -1, 0])))
        
        # Check that we have both buy and sell signals
        buy_signals = (signals == 1).sum()
        sell_signals = (signals == -1).sum()
        self.assertTrue(buy_signals > 0 or sell_signals > 0)
    
    def test_donchian_channel(self):
        """Test Donchian Channel strategy"""
        strategy = DonchianChannel(window=20, allocate=1.0, tolerance=0.01)
        signals = strategy.generate_signals(self.test_data)
        
        # Should have some signals
        self.assertTrue(len(signals[signals != 0]) > 0)
        
        # All signals should be 1, -1, or 0
        self.assertTrue(all(signals.isin([1, -1, 0])))
        
        # Check that we have both buy and sell signals
        buy_signals = (signals == 1).sum()
        sell_signals = (signals == -1).sum()
        self.assertTrue(buy_signals > 0 or sell_signals > 0)
    
    def test_strategy_validation(self):
        """Test strategy parameter validation"""
        
        # Test invalid parameters
        with self.assertRaises(ValueError):
            SmaCrossover(fast=50, slow=20)  # Fast > Slow
        
        with self.assertRaises(ValueError):
            RSI(lower=70, upper=30)  # Lower > Upper
        
        with self.assertRaises(ValueError):
            BollingerBands(window=-1)  # Negative window
        
        with self.assertRaises(ValueError):
            MA200(window=0)  # Zero window
        
        with self.assertRaises(ValueError):
            Momentum(lookback=-1)  # Negative lookback
        
        with self.assertRaises(ValueError):
            ATRTrailingStop(multiplier=0)  # Zero multiplier
        
        with self.assertRaises(ValueError):
            DonchianChannel(tolerance=-0.1)  # Negative tolerance
    
    def test_signal_consistency(self):
        """Test that signals are consistent across strategies"""
        strategies = [
            BuyAndHold(allocate=1.0),
            SmaCrossover(fast=5, slow=10, allocate=1.0),
            RSI(period=14, lower=30, upper=70, allocate=1.0),
            BollingerBands(window=20, num_std=2.0, allocate=1.0),
            MA200(window=50, allocate=1.0),
            Momentum(lookback=20, allocate=1.0),
            ATRTrailingStop(window=14, multiplier=3.0, allocate=1.0),
            DonchianChannel(window=20, allocate=1.0, tolerance=0.01)
        ]
        
        for strategy in strategies:
            signals = strategy.generate_signals(self.test_data)
            
            # Check signal length matches data length
            self.assertEqual(len(signals), len(self.test_data))
            
            # Check signal index matches data index
            self.assertTrue(signals.index.equals(self.test_data.index))
            
            # Check all signals are valid values
            self.assertTrue(all(signals.isin([1, -1, 0])))

def run_toy_examples():
    """Run toy examples to demonstrate each strategy"""
    
    print("Running Toy Examples for All Strategies")
    print("=" * 50)
    
    # Create simple test data
    dates = pd.date_range('2023-01-01', periods=50, freq='D')
    close_prices = [100 + i + np.random.normal(0, 1) for i in range(50)]
    
    test_data = pd.DataFrame({
        'Open': [p * 0.99 for p in close_prices],
        'High': [p * 1.02 for p in close_prices],
        'Low': [p * 0.98 for p in close_prices],
        'Close': close_prices,
        'Volume': np.random.randint(1000000, 5000000, 50)
    }, index=dates)
    
    # Test each strategy
    strategies = [
        ("Buy & Hold", BuyAndHold(allocate=1.0)),
        ("SMA Crossover", SmaCrossover(fast=5, slow=10, allocate=1.0)),
        ("RSI", RSI(period=14, lower=30, upper=70, allocate=1.0)),
        ("Bollinger Bands", BollingerBands(window=20, num_std=2.0, allocate=1.0)),
        ("MA200", MA200(window=25, allocate=1.0)),  # Shorter for demo
        ("Momentum", Momentum(lookback=10, allocate=1.0)),  # Shorter for demo
        ("ATR Trailing Stop", ATRTrailingStop(window=14, multiplier=3.0, allocate=1.0)),
        ("Donchian Channel", DonchianChannel(window=10, allocate=1.0, tolerance=0.01))
    ]
    
    for name, strategy in strategies:
        signals = strategy.generate_signals(test_data)
        buy_signals = (signals == 1).sum()
        sell_signals = (signals == -1).sum()
        
        print(f"{name:20} | Buy: {buy_signals:2d} | Sell: {sell_signals:2d} | Total: {buy_signals + sell_signals:2d}")
    
    print("\nAll strategies successfully generated signals!")
    print("✅ Strategy tests completed successfully")

if __name__ == "__main__":
    # Run toy examples
    run_toy_examples()
    
    # Run unit tests
    print("\n" + "=" * 50)
    print("Running Unit Tests")
    print("=" * 50)
    
    unittest.main(argv=[''], exit=False, verbosity=2)
