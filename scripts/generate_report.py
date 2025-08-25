#!/usr/bin/env python3
"""
Automated Report Generator for Backtesting Results

This script automatically:
1. Reads all batch_stats_*.csv files
2. Creates a comprehensive comparison table
3. Generates visualizations (charts and graphs)
4. Saves everything to an HTML report
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
from datetime import datetime
import numpy as np

# Set style for better-looking plots
try:
    plt.style.use('seaborn-v0_8')
except:
    plt.style.use('default')
sns.set_palette("husl")

class ReportGenerator:
    def __init__(self):
        self.results_dir = "."
        self.output_dir = "reports"
        self.csv_files = []
        self.all_data = pd.DataFrame()
        
    def find_csv_files(self):
        """Find all batch_stats CSV files"""
        pattern = os.path.join(self.results_dir, "batch_stats_*.csv")
        self.csv_files = glob.glob(pattern)
        print(f"Found {len(self.csv_files)} CSV files:")
        for file in self.csv_files:
            print(f"  - {os.path.basename(file)}")
    
    def load_all_data(self):
        """Load and combine all CSV files"""
        dataframes = []
        
        for file in self.csv_files:
            # Extract strategy name from filename
            strategy_name = os.path.basename(file).replace("batch_stats_", "").replace(".csv", "")
            
            # Load CSV
            df = pd.read_csv(file)
            df['strategy'] = strategy_name
            dataframes.append(df)
        
        if dataframes:
            self.all_data = pd.concat(dataframes, ignore_index=True)
            print(f"Loaded data for {len(self.all_data)} strategy-stock combinations")
        else:
            print("No CSV files found!")
    
    def create_summary_table(self):
        """Create a comprehensive summary table"""
        if self.all_data.empty:
            return pd.DataFrame()
        
        # Convert returns to percentages for better readability
        summary = self.all_data.copy()
        summary['total_return_pct'] = summary['total_return'] * 100
        summary['max_drawdown_pct'] = summary['max_drawdown'] * 100
        summary['volatility_pct'] = summary['volatility'] * 100
        
        # Round for display
        summary['total_return_pct'] = summary['total_return_pct'].round(1)
        summary['volatility_pct'] = summary['volatility_pct'].round(1)
        summary['sharpe'] = summary['sharpe'].round(3)
        summary['max_drawdown_pct'] = summary['max_drawdown_pct'].round(1)
        
        return summary[['strategy', 'ticker', 'total_return_pct', 'volatility_pct', 'sharpe', 'max_drawdown_pct']]
    
    def create_performance_chart(self):
        """Create a bar chart comparing total returns by strategy and stock"""
        if self.all_data.empty:
            return None
        
        plt.figure(figsize=(14, 8))
        
        # Create pivot table for plotting
        pivot_data = self.all_data.pivot(index='ticker', columns='strategy', values='total_return')
        
        # Create bar chart
        ax = pivot_data.plot(kind='bar', figsize=(14, 8))
        plt.title('Total Returns by Strategy and Stock', fontsize=16, fontweight='bold')
        plt.xlabel('Stock Ticker', fontsize=12)
        plt.ylabel('Total Return (Decimal)', fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title='Strategy', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        return plt.gcf()
    
    def create_sharpe_heatmap(self):
        """Create a heatmap of Sharpe ratios"""
        if self.all_data.empty:
            return None
        
        plt.figure(figsize=(10, 6))
        
        # Create pivot table for heatmap
        pivot_data = self.all_data.pivot(index='ticker', columns='strategy', values='sharpe')
        
        # Create heatmap
        sns.heatmap(pivot_data, annot=True, cmap='RdYlGn', center=0, 
                   fmt='.3f', cbar_kws={'label': 'Sharpe Ratio'})
        plt.title('Sharpe Ratio Heatmap by Strategy and Stock', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return plt.gcf()
    
    def create_risk_return_scatter(self):
        """Create a scatter plot of risk vs return"""
        if self.all_data.empty:
            return None
        
        plt.figure(figsize=(12, 8))
        
        # Create scatter plot
        for strategy in self.all_data['strategy'].unique():
            strategy_data = self.all_data[self.all_data['strategy'] == strategy]
            plt.scatter(strategy_data['volatility'], strategy_data['total_return'], 
                       label=strategy, s=100, alpha=0.7)
            
            # Add ticker labels
            for _, row in strategy_data.iterrows():
                plt.annotate(row['ticker'], (row['volatility'], row['total_return']), 
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        plt.xlabel('Volatility (Risk)', fontsize=12)
        plt.ylabel('Total Return', fontsize=12)
        plt.title('Risk vs Return by Strategy and Stock', fontsize=16, fontweight='bold')
        plt.legend(title='Strategy')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return plt.gcf()
    
    def create_strategy_comparison_chart(self):
        """Create a comparison chart showing average performance by strategy"""
        if self.all_data.empty:
            return None
        
        # Calculate average metrics by strategy
        strategy_avg = self.all_data.groupby('strategy').agg({
            'total_return': 'mean',
            'volatility': 'mean',
            'sharpe': 'mean',
            'max_drawdown': 'mean'
        }).round(4)
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Strategy Performance Comparison (Averages)', fontsize=16, fontweight='bold')
        
        # Total Return
        strategy_avg['total_return'].plot(kind='bar', ax=axes[0,0], color='green', alpha=0.7)
        axes[0,0].set_title('Average Total Return')
        axes[0,0].set_ylabel('Total Return')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # Volatility
        strategy_avg['volatility'].plot(kind='bar', ax=axes[0,1], color='red', alpha=0.7)
        axes[0,1].set_title('Average Volatility')
        axes[0,1].set_ylabel('Volatility')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # Sharpe Ratio
        strategy_avg['sharpe'].plot(kind='bar', ax=axes[1,0], color='blue', alpha=0.7)
        axes[1,0].set_title('Average Sharpe Ratio')
        axes[1,0].set_ylabel('Sharpe Ratio')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # Max Drawdown
        strategy_avg['max_drawdown'].plot(kind='bar', ax=axes[1,1], color='orange', alpha=0.7)
        axes[1,1].set_title('Average Max Drawdown')
        axes[1,1].set_ylabel('Max Drawdown')
        axes[1,1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        return plt.gcf()
    
    def generate_html_report(self):
        """Generate an HTML report with all tables and charts"""
        if self.all_data.empty:
            print("No data to generate report!")
            return
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save charts
        charts = {}
        
        # Performance chart
        perf_chart = self.create_performance_chart()
        if perf_chart:
            perf_path = os.path.join(self.output_dir, f"performance_chart_{timestamp}.png")
            perf_chart.savefig(perf_path, dpi=300, bbox_inches='tight')
            charts['performance'] = perf_path
            plt.close(perf_chart)
        
        # Sharpe heatmap
        sharpe_chart = self.create_sharpe_heatmap()
        if sharpe_chart:
            sharpe_path = os.path.join(self.output_dir, f"sharpe_heatmap_{timestamp}.png")
            sharpe_chart.savefig(sharpe_path, dpi=300, bbox_inches='tight')
            charts['sharpe'] = sharpe_path
            plt.close(sharpe_chart)
        
        # Risk-return scatter
        scatter_chart = self.create_risk_return_scatter()
        if scatter_chart:
            scatter_path = os.path.join(self.output_dir, f"risk_return_scatter_{timestamp}.png")
            scatter_chart.savefig(scatter_path, dpi=300, bbox_inches='tight')
            charts['scatter'] = scatter_path
            plt.close(scatter_chart)
        
        # Strategy comparison
        comp_chart = self.create_strategy_comparison_chart()
        if comp_chart:
            comp_path = os.path.join(self.output_dir, f"strategy_comparison_{timestamp}.png")
            comp_chart.savefig(comp_path, dpi=300, bbox_inches='tight')
            charts['comparison'] = comp_path
            plt.close(comp_chart)
        
        # Create summary table
        summary_table = self.create_summary_table()
        
        # Generate HTML
        html_content = self.create_html_report(summary_table, charts, timestamp)
        
        # Save HTML report
        html_path = os.path.join(self.output_dir, f"backtesting_report_{timestamp}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n📊 Report generated successfully!")
        print(f"📁 HTML Report: {html_path}")
        print(f"📈 Charts saved in: {self.output_dir}")
        
        return html_path
    
    def create_html_report(self, summary_table, charts, timestamp):
        """Create HTML content for the report"""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Backtesting Results Report - {timestamp}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #e8f4fd;
        }}
        .chart-container {{
            margin: 30px 0;
            text-align: center;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
        }}
        .timestamp {{
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Backtesting Results Report</h1>
        
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-number">{len(self.all_data['strategy'].unique())}</div>
                <div>Strategies Tested</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(self.all_data['ticker'].unique())}</div>
                <div>Stocks Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(self.all_data)}</div>
                <div>Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.all_data['total_return'].max():.1%}</div>
                <div>Best Return</div>
            </div>
        </div>
        
        <h2>📋 Detailed Results Table</h2>
        {summary_table.to_html(index=False, classes='data-table')}
        
        <h2>📈 Performance Comparison</h2>
        <div class="chart-container">
            <img src="{os.path.basename(charts.get('performance', ''))}" alt="Performance Chart">
        </div>
        
        <h2>🔥 Sharpe Ratio Heatmap</h2>
        <div class="chart-container">
            <img src="{os.path.basename(charts.get('sharpe', ''))}" alt="Sharpe Ratio Heatmap">
        </div>
        
        <h2>⚖️ Risk vs Return Analysis</h2>
        <div class="chart-container">
            <img src="{os.path.basename(charts.get('scatter', ''))}" alt="Risk Return Scatter">
        </div>
        
        <h2>📊 Strategy Comparison</h2>
        <div class="chart-container">
            <img src="{os.path.basename(charts.get('comparison', ''))}" alt="Strategy Comparison">
        </div>
        
        <div class="timestamp">
            Report generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
        </div>
    </div>
</body>
</html>
        """
        return html
    
    def run(self):
        """Run the complete report generation process"""
        print("Starting automated report generation...")
        
        # Step 1: Find CSV files
        self.find_csv_files()
        
        # Step 2: Load data
        self.load_all_data()
        
        # Step 3: Generate report
        if not self.all_data.empty:
            report_path = self.generate_html_report()
            print(f"\n✅ Report generation complete!")
            print(f"🌐 Open {report_path} in your web browser to view the report")
        else:
            print("❌ No data found to generate report")

if __name__ == "__main__":
    generator = ReportGenerator()
    generator.run()
