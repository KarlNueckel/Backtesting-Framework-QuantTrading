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

class BuyAndHold(Strategy):
    """
    Buy and Hold Strategy.
    
    Buy once at the beginning and hold until the end.
    This serves as a baseline comparison for other strategies.
    """
    
    def __init__(self, allocate: float = 1.0):
        """
        Initialize Buy and Hold strategy.
        
        Args:
            allocate: Fraction of portfolio to allocate (0.0 to 1.0)
        """
        self.allocate = allocate
        
        if not 0 <= allocate <= 1:
            raise ValueError("Allocate must be between 0 and 1")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals for buy and hold.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with signals: 1 (buy once), 0 (hold)
        """
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Buy signal only on the first day
        if len(signals) > 0:
            signals.iloc[0] = 1
        
        return signals

class RSI(Strategy):
    """
    RSI (Relative Strength Index) Mean Reversion Strategy.
    
    Buy when RSI is oversold (below lower threshold)
    Sell when RSI is overbought (above upper threshold)
    """
    
    def __init__(self, period: int = 14, lower: float = 30, upper: float = 70, allocate: float = 1.0):
        """
        Initialize RSI strategy.
        
        Args:
            period: RSI calculation period
            lower: Oversold threshold (buy signal)
            upper: Overbought threshold (sell signal)
            allocate: Fraction of portfolio to allocate (0.0 to 1.0)
        """
        self.period = period
        self.lower = lower
        self.upper = upper
        self.allocate = allocate
        
        if lower >= upper:
            raise ValueError("Lower threshold must be less than upper threshold")
        if not 0 <= allocate <= 1:
            raise ValueError("Allocate must be between 0 and 1")
    
    def calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate RSI (Relative Strength Index).
        
        Args:
            data: Price series (typically Close prices)
            period: Lookback period for RSI calculation
            
        Returns:
            RSI values between 0 and 100
        """
        # Calculate price changes
        delta = data.diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on RSI.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        # Calculate RSI
        rsi = self.calculate_rsi(data['Close'], self.period)
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Buy signal: RSI crosses below lower threshold (oversold)
        oversold = (rsi < self.lower) & (rsi.shift(1) >= self.lower)
        signals[oversold] = 1
        
        # Sell signal: RSI crosses above upper threshold (overbought)
        overbought = (rsi > self.upper) & (rsi.shift(1) <= self.upper)
        signals[overbought] = -1
        
        return signals

class BollingerBands(Strategy):
    """
    Bollinger Bands Mean Reversion Strategy.
    
    Buy when price touches the lower band (oversold)
    Sell when price touches the upper band (overbought)
    """
    
    def __init__(self, window: int = 20, num_std: float = 2.0, allocate: float = 1.0):
        """
        Initialize Bollinger Bands strategy.
        
        Args:
            window: Moving average window period
            num_std: Number of standard deviations for bands
            allocate: Fraction of portfolio to allocate (0.0 to 1.0)
        """
        self.window = window
        self.num_std = num_std
        self.allocate = allocate
        
        if window <= 0:
            raise ValueError("Window must be positive")
        if num_std <= 0:
            raise ValueError("Number of standard deviations must be positive")
        if not 0 <= allocate <= 1:
            raise ValueError("Allocate must be between 0 and 1")
    
    def calculate_bollinger_bands(self, data: pd.Series, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
        """
        Calculate Bollinger Bands.
        
        Args:
            data: Price series (typically Close prices)
            window: Moving average window period
            num_std: Number of standard deviations for bands
            
        Returns:
            DataFrame with 'middle', 'upper', and 'lower' bands
        """
        # Calculate middle band (simple moving average)
        middle = data.rolling(window=window).mean()
        
        # Calculate standard deviation
        std = data.rolling(window=window).std()
        
        # Calculate upper and lower bands
        upper = middle + (num_std * std)
        lower = middle - (num_std * std)
        
        return pd.DataFrame({
            'middle': middle,
            'upper': upper,
            'lower': lower
        })
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on Bollinger Bands.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        # Calculate Bollinger Bands
        bands = self.calculate_bollinger_bands(data['Close'], self.window, self.num_std)
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Buy signal: price crosses below lower band (oversold)
        oversold = (data['Close'] <= bands['lower']) & (data['Close'].shift(1) > bands['lower'].shift(1))
        signals[oversold] = 1
        
        # Sell signal: price crosses above upper band (overbought)
        overbought = (data['Close'] >= bands['upper']) & (data['Close'].shift(1) < bands['upper'].shift(1))
        signals[overbought] = -1
        
        return signals
