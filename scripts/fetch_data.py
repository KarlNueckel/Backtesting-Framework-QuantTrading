# scripts/fetch_data.py
# Usage: python scripts/fetch_data.py --tickers GOOGL WMT AMD --start 2015-01-01 --end 2025-01-01
import argparse, os
import yfinance as yf
import pandas as pd

def save_csv(ticker: str, outdir: str, start: str, end: str, interval: str):
    df = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=False)
    if df.empty:
        print(f"[WARN] No data for {ticker}")
        return
    df = df.reset_index()
    # Standardize columns for our loader: Date,Open,High,Low,Close,Volume
    keep = ["Date", "Open", "High", "Low", "Close", "Volume"]
    df = df[keep]
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, f"{ticker}.csv")
    df.to_csv(out, index=False)
    print(f"[OK] Saved {out}  ({len(df)} rows)")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--tickers", nargs="+", default=["GOOGL", "WMT", "AMD"])
    p.add_argument("--start", default="2015-01-01")
    p.add_argument("--end",   default="2025-01-01")
    p.add_argument("--interval", default="1d")  # try "1h" later
    p.add_argument("--outdir", default="data")
    args = p.parse_args()
    for t in args.tickers:
        save_csv(t, args.outdir, args.start, args.end, args.interval)
