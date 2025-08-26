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

class MA200(Strategy):
    """
    MA200 (200-day Moving Average) Trend Following Strategy.
    
    Buy when price is above the 200-day moving average (uptrend)
    Sell when price is below the 200-day moving average (downtrend)
    """
    
    def __init__(self, window: int = 200, allocate: float = 1.0, buffer_pct: float = 0.0):
        """
        Initialize MA200 strategy.
        
        Args:
            window: Moving average window period (default 200 days)
            allocate: Fraction of portfolio to allocate (0.0 to 1.0)
            buffer_pct: Buffer percentage to reduce whipsaws (0.0 to 1.0)
        """
        self.window = window
        self.allocate = allocate
        self.buffer_pct = buffer_pct
        
        if window <= 0:
            raise ValueError("Window must be positive")
        if not 0 <= allocate <= 1:
            raise ValueError("Allocate must be between 0 and 1")
        if not 0 <= buffer_pct <= 1:
            raise ValueError("Buffer percentage must be between 0 and 1")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on MA200 trend filter.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        # Calculate 200-day moving average
        ma200 = data['Close'].rolling(window=self.window).mean()
        
        # Apply buffer if specified
        if self.buffer_pct > 0:
            buffer = ma200 * self.buffer_pct
            upper_threshold = ma200 + buffer
            lower_threshold = ma200 - buffer
        else:
            upper_threshold = ma200
            lower_threshold = ma200
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Buy signal: price crosses above MA200 (with buffer)
        buy_signal = (data['Close'] > upper_threshold) & (data['Close'].shift(1) <= upper_threshold.shift(1))
        signals[buy_signal] = 1
        
        # Sell signal: price crosses below MA200 (with buffer)
        sell_signal = (data['Close'] < lower_threshold) & (data['Close'].shift(1) >= lower_threshold.shift(1))
        signals[sell_signal] = -1
        
        return signals

class Momentum(Strategy):
    """
    Momentum (Rate-of-Change) Strategy.
    
    Buy when stock has been going up (positive momentum)
    Sell when stock has been going down (negative momentum)
    This is the opposite of RSI - it follows the trend rather than mean reversion.
    """
    
    def __init__(self, lookback: int = 90, allocate: float = 1.0):
        """
        Initialize Momentum strategy.
        
        Args:
            lookback: Number of days to look back for momentum calculation
            allocate: Fraction of portfolio to allocate (0.0 to 1.0)
        """
        self.lookback = lookback
        self.allocate = allocate
        
        if lookback <= 0:
            raise ValueError("Lookback period must be positive")
        if not 0 <= allocate <= 1:
            raise ValueError("Allocate must be between 0 and 1")
    
    def calculate_momentum(self, data: pd.Series, lookback: int = 90) -> pd.Series:
        """
        Calculate momentum as the rate of change over the lookback period.
        
        Args:
            data: Price series (typically Close prices)
            lookback: Number of periods to look back
            
        Returns:
            Momentum values (can be positive or negative)
        """
        # Calculate momentum as (current_price - price_lookback_periods_ago) / price_lookback_periods_ago
        momentum = (data - data.shift(lookback)) / data.shift(lookback)
        return momentum
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on momentum.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        # Calculate momentum
        momentum = self.calculate_momentum(data['Close'], self.lookback)
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Buy signal: momentum becomes positive (stock starts going up)
        buy_signal = (momentum > 0) & (momentum.shift(1) <= 0)
        signals[buy_signal] = 1
        
        # Sell signal: momentum becomes negative (stock starts going down)
        sell_signal = (momentum < 0) & (momentum.shift(1) >= 0)
        signals[sell_signal] = -1
        
        return signals

class ATRTrailingStop(Strategy):
    """
    ATR (Average True Range) Trailing Stop Strategy.
    
    Uses ATR to set dynamic trailing stops that move up as price rises.
    This allows "cutting losers fast, riding winners long."
    """
    
    def __init__(self, window: int = 14, multiplier: float = 3.0, allocate: float = 1.0):
        """
        Initialize ATR Trailing Stop strategy.
        
        Args:
            window: ATR calculation window period
            multiplier: Stop distance multiplier (e.g., 3.0 means 3 * ATR below peak)
            allocate: Fraction of portfolio to allocate (0.0 to 1.0)
        """
        self.window = window
        self.multiplier = multiplier
        self.allocate = allocate
        
        if window <= 0:
            raise ValueError("Window must be positive")
        if multiplier <= 0:
            raise ValueError("Multiplier must be positive")
        if not 0 <= allocate <= 1:
            raise ValueError("Allocate must be between 0 and 1")
    
    def calculate_atr(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR).
        
        Args:
            data: DataFrame with OHLCV data
            window: Lookback period for ATR calculation
            
        Returns:
            ATR values
        """
        # Calculate True Range
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift(1))
        low_close = np.abs(data['Low'] - data['Close'].shift(1))
        
        # True Range is the maximum of these three values
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        
        # Calculate ATR as the rolling mean of True Range
        atr = true_range.rolling(window=window).mean()
        
        return atr
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on ATR Trailing Stop.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        # Calculate ATR
        atr = self.calculate_atr(data, self.window)
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Track the highest price since entry (peak)
        peak_price = data['Close'].copy()
        in_position = False
        entry_price = 0
        
        for i in range(1, len(data)):
            current_price = data['Close'].iloc[i]
            current_atr = atr.iloc[i]
            
            if not in_position:
                # Simple entry condition: price above its 20-day moving average
                ma20 = data['Close'].rolling(window=20).mean().iloc[i]
                if current_price > ma20:
                    signals.iloc[i] = 1  # Buy signal
                    in_position = True
                    entry_price = current_price
                    peak_price.iloc[i] = current_price
            else:
                # Update peak price if current price is higher
                if current_price > peak_price.iloc[i-1]:
                    peak_price.iloc[i] = current_price
                else:
                    peak_price.iloc[i] = peak_price.iloc[i-1]
                
                # Calculate trailing stop
                stop_distance = self.multiplier * current_atr
                stop_price = peak_price.iloc[i] - stop_distance
                
                # Check if stop is hit
                if current_price <= stop_price:
                    signals.iloc[i] = -1  # Sell signal
                    in_position = False
        
        return signals

class DonchianChannel(Strategy):
    """
    Donchian Channel Breakout Strategy.
    
    Buy when price breaks above the N-day high (uptrend breakout)
    Sell when price breaks below the N-day low (downtrend breakout)
    """
    
    def __init__(self, window: int = 20, allocate: float = 1.0, tolerance: float = 0.01):
        """
        Initialize Donchian Channel strategy.
        
        Args:
            window: Lookback window for high/low channel
            allocate: Fraction of portfolio to allocate (0.0 to 1.0)
            tolerance: Percentage tolerance for breakout detection (0.01 = 1%)
        """
        self.window = window
        self.allocate = allocate
        self.tolerance = tolerance
        
        if window <= 0:
            raise ValueError("Window must be positive")
        if not 0 <= allocate <= 1:
            raise ValueError("Allocate must be between 0 and 1")
        if tolerance < 0:
            raise ValueError("Tolerance must be non-negative")
    
    def calculate_donchian_channels(self, data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """
        Calculate Donchian Channels.
        
        Args:
            data: DataFrame with OHLCV data
            window: Lookback window for channel calculation
            
        Returns:
            DataFrame with 'upper', 'middle', and 'lower' channels
        """
        # Calculate upper channel (highest high over window)
        upper = data['High'].rolling(window=window).max()
        
        # Calculate lower channel (lowest low over window)
        lower = data['Low'].rolling(window=window).min()
        
        # Calculate middle channel (average of upper and lower)
        middle = (upper + lower) / 2
        
        return pd.DataFrame({
            'upper': upper,
            'middle': middle,
            'lower': lower
        })
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on Donchian Channel breakouts.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        # Calculate Donchian Channels
        channels = self.calculate_donchian_channels(data, self.window)
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Skip the first window periods where channels are NaN
        valid_data = channels['upper'].notna() & channels['lower'].notna()
        
        # Buy signal: price is above upper channel (uptrend breakout)
        # Use tolerance for more realistic breakout detection
        upper_threshold = channels['upper'] * (1 - self.tolerance)
        breakout_up = data['Close'] > upper_threshold
        signals[breakout_up & valid_data] = 1
        
        # Sell signal: price is below lower channel (downtrend breakout)
        # Use tolerance for more realistic breakout detection
        lower_threshold = channels['lower'] * (1 + self.tolerance)
        breakout_down = data['Close'] < lower_threshold
        signals[breakout_down & valid_data] = -1
        
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
