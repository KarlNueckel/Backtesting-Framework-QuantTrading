import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any

class Strategy(ABC):
    """Base class for all trading strategies."""
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals from price data.
        
        Returns:
            pd.Series with values: 1 (buy), -1 (sell), 0 (hold)
        """
        pass

class SmaCrossover(Strategy):
    """
    Simple Moving Average Crossover Strategy.
    
    Buy when fast MA crosses above slow MA (golden cross)
    Sell when fast MA crosses below slow MA (death cross)
    """
    
    def __init__(self, fast: int = 20, slow: int = 50, allocate: float = 1.0):
        """
        Initialize SMA Crossover strategy.
        
        Args:
            fast: Fast moving average period
            slow: Slow moving average period  
            allocate: Fraction of portfolio to allocate (0.0 to 1.0)
        """
        self.fast = fast
        self.slow = slow
        self.allocate = allocate
        
        if fast >= slow:
            raise ValueError("Fast MA period must be less than slow MA period")
        if not 0 <= allocate <= 1:
            raise ValueError("Allocate must be between 0 and 1")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on SMA crossover.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        # Calculate moving averages
        fast_ma = data['Close'].rolling(window=self.fast).mean()
        slow_ma = data['Close'].rolling(window=self.slow).mean()
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Golden cross: fast MA crosses above slow MA
        golden_cross = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
        signals[golden_cross] = 1
        
        # Death cross: fast MA crosses below slow MA  
        death_cross = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))
        signals[death_cross] = -1
        
        return signals
