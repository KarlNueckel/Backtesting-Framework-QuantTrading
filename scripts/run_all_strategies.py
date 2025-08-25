#!/usr/bin/env python3
"""
Run All Strategies Script

This script automatically runs all available strategies on all available assets.
It then generates a comprehensive report with all results.

Usage:
    python scripts/run_all_strategies.py
"""

import os
import subprocess
import sys
import glob
from datetime import datetime

class StrategyRunner:
    def __init__(self):
        self.strategies_dir = "strategies"
        self.data_dir = "data"
        self.available_strategies = []
        self.available_assets = []
        
    def find_strategies(self):
        """Find all available strategy YAML files"""
        pattern = os.path.join(self.strategies_dir, "*.yaml")
        strategy_files = glob.glob(pattern)
        
        self.available_strategies = [os.path.basename(f) for f in strategy_files]
        print(f"📋 Found {len(self.available_strategies)} strategies:")
        for strategy in self.available_strategies:
            print(f"  - {strategy}")
    
    def find_assets(self):
        """Find all available asset CSV files"""
        pattern = os.path.join(self.data_dir, "*.csv")
        asset_files = glob.glob(pattern)
        
        # Extract ticker symbols from filenames
        self.available_assets = [os.path.basename(f).replace('.csv', '') for f in asset_files]
        print(f"📈 Found {len(self.available_assets)} assets:")
        for asset in self.available_assets:
            print(f"  - {asset}")
    
    def run_strategy(self, strategy_file, assets):
        """Run a single strategy on all assets"""
        print(f"\n🚀 Running {strategy_file}...")
        
        # Build the command
        cmd = [
            sys.executable, "-m", "cli.run_batch",
            "--tickers"
        ] + assets + [
            "--config", os.path.join(self.strategies_dir, strategy_file)
        ]
        
        try:
            # Run the command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ {strategy_file} completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running {strategy_file}: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def run_all_strategies(self):
        """Run all strategies on all assets"""
        print("🎯 Starting comprehensive strategy testing...")
        print("=" * 60)
        
        # Find available strategies and assets
        self.find_strategies()
        print()
        self.find_assets()
        print()
        
        if not self.available_strategies:
            print("❌ No strategy files found in strategies/ directory")
            return False
        
        if not self.available_assets:
            print("❌ No asset files found in data/ directory")
            return False
        
        # Run each strategy
        successful_runs = 0
        total_runs = len(self.available_strategies)
        
        for strategy in self.available_strategies:
            if self.run_strategy(strategy, self.available_assets):
                successful_runs += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Strategy Testing Complete!")
        print(f"✅ Successful runs: {successful_runs}/{total_runs}")
        
        return successful_runs > 0
    
    def generate_report(self):
        """Generate the comprehensive report"""
        print("\n📋 Generating comprehensive report...")
        
        try:
            # Run the report generator
            cmd = [sys.executable, "scripts/generate_report.py"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ Report generated successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error generating report: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def open_report(self):
        """Open the latest report in the browser"""
        print("\n🌐 Opening latest report...")
        
        # Find the most recent report
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            print("❌ Reports directory not found")
            return False
        
        report_files = glob.glob(os.path.join(reports_dir, "backtesting_report_*.html"))
        if not report_files:
            print("❌ No report files found")
            return False
        
        # Get the most recent report
        latest_report = max(report_files, key=os.path.getctime)
        
        try:
            # Open the report
            subprocess.run(["start", latest_report], shell=True, check=True)
            print(f"✅ Opened report: {os.path.basename(latest_report)}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error opening report: {e}")
            return False
    
    def run(self):
        """Run the complete process"""
        print("🚀 Starting All Strategies Runner")
        print("=" * 60)
        
        # Step 1: Run all strategies
        success = self.run_all_strategies()
        
        if not success:
            print("❌ Strategy testing failed. Exiting.")
            return
        
        # Step 2: Generate report
        report_success = self.generate_report()
        
        if not report_success:
            print("❌ Report generation failed.")
            return
        
        # Step 3: Open report
        self.open_report()
        
        print("\n🎉 All done! Your comprehensive backtesting analysis is complete.")
        print("📊 Check the generated report for detailed results and visualizations.")

def main():
    """Main function"""
    runner = StrategyRunner()
    runner.run()

if __name__ == "__main__":
    main()
