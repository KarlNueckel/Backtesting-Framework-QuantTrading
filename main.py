#!/usr/bin/env python3
"""
Main entry point for the Backtesting Framework for Quantitative Trading

This script provides a unified interface to all framework functionality.
"""

import argparse
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.run_all_strategies import main as run_all_strategies
from scripts.generate_report import ReportGenerator
from scripts.strategy_comparison import main as run_strategy_comparison
from scripts.fetch_data import main as fetch_data
from tests.test_strategies import run_toy_examples

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Backtesting Framework for Quantitative Trading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py run-all                    # Run all strategies on all stocks
  python main.py compare --stock GOOGL      # Compare all strategies on GOOGL
  python main.py report                     # Generate comprehensive HTML report
  python main.py fetch-data                 # Fetch stock data
  python main.py test                       # Run strategy tests
  python main.py notebook                   # Create Jupyter notebooks
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run all strategies command
    run_parser = subparsers.add_parser('run-all', help='Run all strategies on all stocks')
    
    # Compare strategies command
    compare_parser = subparsers.add_parser('compare', help='Compare all strategies on a single stock')
    compare_parser.add_argument('--stock', default='GOOGL', help='Stock ticker to analyze')
    
    # Generate report command
    report_parser = subparsers.add_parser('report', help='Generate comprehensive HTML report')
    
    # Fetch data command
    fetch_parser = subparsers.add_parser('fetch-data', help='Fetch stock data')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run strategy tests')
    
    # Create notebooks command
    notebook_parser = subparsers.add_parser('notebook', help='Create Jupyter notebooks')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'run-all':
            print("Running all strategies on all stocks...")
            run_all_strategies()
            
        elif args.command == 'compare':
            print(f"Comparing all strategies on {args.stock}...")
            # Modify the strategy comparison to use the specified stock
            import scripts.strategy_comparison as sc
            sc.main = lambda: sc.run_strategy_comparison(args.stock)
            run_strategy_comparison()
            
        elif args.command == 'report':
            print("Generating comprehensive HTML report...")
            generator = ReportGenerator()
            generator.run()
            
        elif args.command == 'fetch-data':
            print("Fetching stock data...")
            fetch_data()
            
        elif args.command == 'test':
            print("Running strategy tests...")
            run_toy_examples()
            print("\nRunning unit tests...")
            import unittest
            # Discover and run all tests
            loader = unittest.TestLoader()
            start_dir = os.path.join(project_root, 'tests')
            suite = loader.discover(start_dir, pattern='test_*.py')
            runner = unittest.TextTestRunner(verbosity=2)
            runner.run(suite)
            
        elif args.command == 'notebook':
            print("Creating Jupyter notebooks...")
            from scripts.create_notebooks import main as create_notebooks
            create_notebooks()
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
