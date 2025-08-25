import pandas as pd
import numpy as np
from typing import Dict, Any
from .strategy import Strategy

class Backtester:
    """
    Backtesting engine that simulates trading based on strategy signals.
    """
    
    def __init__(self, data: pd.DataFrame, strategy: Strategy, initial_cash: float = 100000):
        """
        Initialize backtester.
        
        Args:
            data: OHLCV price data
            strategy: Trading strategy object
            initial_cash: Starting capital
        """
        self.data = data
        self.strategy = strategy
        self.initial_cash = initial_cash
        
    def run(self) -> Dict[str, pd.Series]:
        """
        Run the backtest simulation.
        
        Returns:
            Dictionary with 'equity' and 'positions' series
        """
        # Generate trading signals
        signals = self.strategy.generate_signals(self.data)
        
        # Initialize tracking variables
        cash = self.initial_cash
        shares = 0
        equity = []
        positions = []
        
        # Simulate trading day by day
        for i, (date, row) in enumerate(self.data.iterrows()):
            signal = signals.iloc[i] if i < len(signals) else 0
            price = row['Close']
            
            # Execute trades based on signals
            if signal == 1 and cash > 0:  # Buy signal
                # Calculate how many shares to buy
                shares_to_buy = int((cash * self.strategy.allocate) / price)
                if shares_to_buy > 0:
                    shares += shares_to_buy
                    cash -= shares_to_buy * price
                    
            elif signal == -1 and shares > 0:  # Sell signal
                # Sell all shares
                cash += shares * price
                shares = 0
            
            # Calculate current portfolio value
            current_equity = cash + (shares * price)
            equity.append(current_equity)
            positions.append(shares)
        
        # Create result series
        equity_series = pd.Series(equity, index=self.data.index)
        positions_series = pd.Series(positions, index=self.data.index)
        
        return {
            'equity': equity_series,
            'positions': positions_series
        }
