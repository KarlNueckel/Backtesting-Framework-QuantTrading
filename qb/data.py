import pandas as pd
from typing import Optional

def load_csv(filepath: str) -> pd.DataFrame:
    """
    Load price data from CSV file.
    
    Expected columns: Date, Open, High, Low, Close, Volume
    Returns DataFrame with Date as index and OHLCV columns.
    """
    df = pd.read_csv(filepath)
    
    # Remove any rows that have non-numeric values in the first column (like ticker symbols)
    df = df[df.iloc[:, 0].str.match(r'^\d{4}-\d{2}-\d{2}', na=False)]
    
    # Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Set Date as index
    df.set_index('Date', inplace=True)
    
    # Ensure we have the required columns
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Convert numeric columns to float
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove any rows with NaN values
    df = df.dropna()
    
    # Sort by date to ensure chronological order
    df.sort_index(inplace=True)
    
    return df
