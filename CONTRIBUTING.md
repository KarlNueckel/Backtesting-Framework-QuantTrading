# Contributing to Backtesting Framework

Thank you for your interest in contributing to the Backtesting Framework for Quantitative Trading! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .[dev]
   ```

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- pip

### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/Backtesting-Framework-QuantTrading.git
cd Backtesting-Framework-QuantTrading

# Install dependencies
pip install -r requirements.txt
pip install -e .[dev]

# Run tests to ensure everything works
python main.py test
```

## Project Structure

```
Backtesting-Framework-QuantTrading/
├── qb/                    # Core backtesting engine
│   ├── backtester.py     # Main backtesting logic
│   ├── data.py           # Data loading and management
│   ├── metrics.py        # Performance calculations
│   └── strategy.py       # Strategy base classes
├── strategies/           # Strategy configurations (YAML files)
├── scripts/              # Utility scripts
├── tests/                # Test suite
├── notebooks/            # Jupyter notebooks for analysis
├── data/                 # Stock data (gitignored)
├── reports/              # Generated reports (gitignored)
└── main.py               # Main entry point
```

## Adding a New Strategy

### 1. Create Strategy Class
Add your strategy class to `qb/strategy.py`:

```python
class MyStrategy(Strategy):
    """
    My Custom Strategy Description.
    
    Brief explanation of the strategy logic.
    """
    
    def __init__(self, param1: float = 1.0, param2: int = 20, allocate: float = 1.0):
        """
        Initialize My Strategy.
        
        Args:
            param1: Description of parameter 1
            param2: Description of parameter 2
            allocate: Fraction of portfolio to allocate (0.0 to 1.0)
        """
        self.param1 = param1
        self.param2 = param2
        self.allocate = allocate
        
        # Validate parameters
        if param1 <= 0:
            raise ValueError("param1 must be positive")
        if not 0 <= allocate <= 1:
            raise ValueError("Allocate must be between 0 and 1")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on My Strategy.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        # Your strategy logic here
        signals = pd.Series(0, index=data.index)
        
        # Example logic
        # signals[condition] = 1  # Buy signal
        # signals[condition] = -1  # Sell signal
        
        return signals
```

### 2. Create Configuration File
Create a YAML configuration file in `strategies/`:

```yaml
# My Custom Strategy
name: my_strategy
params:
  param1: 1.0
  param2: 20
  allocate: 1.0
initial_cash: 100000
```

### 3. Update CLI
Add your strategy to `cli/run_batch.py`:

```python
elif strategy_name == "my_strategy":
    strategy = MyStrategy(**params)
```

### 4. Add Tests
Create tests in `tests/test_strategies.py`:

```python
def test_my_strategy(self):
    """Test My Strategy"""
    strategy = MyStrategy(param1=1.0, param2=20, allocate=1.0)
    signals = strategy.generate_signals(self.test_data)
    
    # Test logic here
    self.assertTrue(len(signals[signals != 0]) > 0)
    self.assertTrue(all(signals.isin([1, -1, 0])))
```

### 5. Update Documentation
- Add your strategy to the README.md table
- Update the strategy descriptions

## Running Tests

```bash
# Run all tests
python main.py test

# Run specific test file
python -m pytest tests/test_strategies.py -v

# Run with coverage
python -m pytest tests/ --cov=qb --cov-report=html
```

## Code Style

We follow PEP 8 style guidelines. Use the provided tools:

```bash
# Format code
black qb/ scripts/ tests/

# Check style
flake8 qb/ scripts/ tests/

# Type checking
mypy qb/ scripts/ tests/
```

## Submitting Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-new-strategy
   ```

2. **Make your changes** and commit them:
   ```bash
   git add .
   git commit -m "Add new strategy: My Strategy"
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/my-new-strategy
   ```

4. **Create a Pull Request** on GitHub

## Pull Request Guidelines

- **Title**: Clear, descriptive title
- **Description**: Explain what the PR does and why
- **Tests**: Include tests for new functionality
- **Documentation**: Update README and docstrings
- **Examples**: Provide usage examples if applicable

## Testing Checklist

Before submitting a PR, ensure:

- [ ] All tests pass: `python main.py test`
- [ ] Code is formatted: `black .`
- [ ] No style issues: `flake8 .`
- [ ] Type checking passes: `mypy .`
- [ ] Documentation is updated
- [ ] New strategy works with all existing functionality

## Questions?

If you have questions about contributing, please:

1. Check the existing issues and discussions
2. Create a new issue with the "question" label
3. Join our community discussions

Thank you for contributing to the Backtesting Framework! 🚀
