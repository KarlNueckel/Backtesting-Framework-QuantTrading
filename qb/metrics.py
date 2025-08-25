import pandas as pd
import numpy as np
from typing import Dict, Any

def equity_stats(equity: pd.Series) -> Dict[str, float]:
    """
    Calculate performance metrics from equity curve.
    
    Args:
        equity: Series of portfolio values over time
        
    Returns:
        Dictionary of performance metrics
    """
    if len(equity) < 2:
        return {
            'total_return': 0.0,
            'volatility': 0.0,
            'sharpe': 0.0,
            'max_drawdown': 0.0
        }
    
    # Calculate returns
    returns = equity.pct_change().dropna()
    
    # Total return
    total_return = (equity.iloc[-1] / equity.iloc[0]) - 1
    
    # Annualized volatility (assuming daily data)
    volatility = returns.std() * np.sqrt(252)  # 252 trading days per year
    
    # Sharpe ratio (assuming risk-free rate of 0)
    if volatility > 0:
        sharpe = (returns.mean() * 252) / volatility
    else:
        sharpe = 0.0
    
    # Maximum drawdown
    rolling_max = equity.expanding().max()
    drawdown = (equity - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    
    return {
        'total_return': total_return,
        'volatility': volatility,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown
    }
