# Nado-Trading-Bot

A Python-based algorithmic trading bot designed to interact with the Nado Protocol, focusing on modularity for data acquisition, strategy development, trade execution, backtesting, and logging.

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Trading Strategy](#trading-strategy)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Adjusting the Bot](#adjusting-the-bot)
- [Deployment Strategy](#deployment-strategy)
- [License](#license)

## Features

*   **Nado Protocol Integration**: Seamless interaction with the Nado Protocol for market data and trade execution.
*   **Data Acquisition**: Fetches real-time prices and historical candlestick data for perpetual products.
*   **Modular Strategy Development**: Easily swap or enhance trading strategies.
*   **Moving Average Crossover Strategy**: A pre-implemented sample strategy for trend following.
*   **Trade Execution**: Functions for placing market, stop-loss, and take-profit orders.
*   **Risk Management**: Basic stop-loss and take-profit mechanisms integrated.
*   **Backtesting Framework**: Evaluate strategy performance on historical data with configurable capital, commissions, and slippage.
*   **Robust Logging**: Comprehensive logging to console and rotating log files for monitoring and debugging.
*   **Configurable**: Easily adjust strategy parameters, backtest settings, and API credentials.

## Architecture

The bot is structured into several key modules, each with a distinct responsibility:

*   **`src/nado_client.py`**: Handles the initialization and connection to the Nado Protocol, loading API credentials from environment variables.
*   **`src/data_acquisition.py`**: Manages fetching market data, including the latest prices and historical candlestick data.
*   **`src/strategy.py`**: Contains the logic for various trading strategies. Currently implements a Moving Average Crossover strategy.
*   **`src/trade_execution.py`**: Provides functions for executing trades (market orders) and managing risk (stop-loss, take-profit orders) on the Nado exchange.
*   **`src/backtester.py`**: A framework for simulating the trading strategy against historical data to evaluate its performance.
*   **`src/logger.py`**: Sets up a comprehensive logging system for recording bot activities, errors, and performance metrics.
*   **`src/main_bot.py`**: Starting point of the trading bot

## Trading Strategy

The current default trading strategy implemented is a **Moving Average Crossover Strategy**.

*   **Principle**: It identifies potential trend changes by analyzing the relationship between two Simple Moving Averages (SMAs) of different lengths.
*   **Mechanism**:
    *   Calculates a **short-term SMA** (faster) and a **long-term SMA** (slower) based on closing prices.
    *   **Buy Signal**: Generated when the short-term SMA crosses *above* the long-term SMA, indicating an upward trend.
    *   **Sell Signal**: Generated when the short-term SMA crosses *below* the long-term SMA, indicating a downward trend.
*   **Implementation**: See the `moving_average_crossover_strategy` function in `src/strategy.py`.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/apine/Nado-Trading-Bot
    cd Nado-Trading-Bot
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip3 install -r requirements.txt
    ```

## Configuration

1.  **Create a `.env` file:**
    In the root directory of the project, create a file named `.env` and add your Nado Protocol private key:
    ```
    NADO_PRIVATE_KEY=your_private_key_here
    ```
    **WARNING**: Never commit your `.env` file or private key to version control. Keep it secure.

## Usage

You can run individual components of the bot for testing and development.

### Get Account Summary (Example)
To fetch and display a summarized account overview:
```bash
python3 -m src.account_summary
```

### Get Latest BTC Perpetual Price
To fetch the latest mark price for BTC perpetual:
```bash
python3 -m src.data_acquisition
```
*(This script also includes a test for historical candlestick data)*

### Run the Strategy (Signal Generation)
To see the moving average crossover strategy generate signals (without execution):
```bash
python3 -m src.strategy
```

### Run a Backtest
To evaluate the strategy using historical data:
```bash
python3 -m src.backtester
```

### Simulate Trade Execution
To simulate (print parameters for) placing market, stop-loss, and take-profit orders:
```bash
python3 -m src.trade_execution
```
**NOTE**: The actual order placement calls are commented out in `src/trade_execution.py` for safety. Uncomment them *only* when you are ready to place real orders (preferably on a testnet first!).

## Adjusting the Bot

### Strategy Parameters
Modify `src/strategy.py`:
*   In the `if __name__ == "__main__":` block, adjust `short_window` and `long_window` for the SMA periods.
    ```python
    short_window = 10  # e.g., 10 periods
    long_window = 30   # e.g., 30 periods
    ```

### Backtesting Parameters
Modify `src/backtester.py`:
*   In the `if __name__ == "__main__":` block, adjust `initial_capital`, `commission_rate`, and `slippage`.
    ```python
    initial_capital = 100000.0
    commission_rate = 0.001 # 0.1%
    slippage = 0.0001     # 0.01%
    ```

### Trade Execution & Live Trading
Modify `src/trade_execution.py`:
*   To enable live order placement (market, stop-loss, take-profit), **uncomment** the respective function calls within the `if __name__ == "__main__":` block.
    *   **CRITICAL WARNING**: Always test thoroughly on a testnet before deploying to a mainnet. Understand the risks involved with live trading.

### Nado Client Mode
The `get_nado_client` function in `src/nado_client.py` defaults to `NadoClientMode.TESTNET`. To switch to mainnet, you would change:
```python
nado_client = get_nado_client(mode=NadoClientMode.TESTNET)
# To mainnet:
# nado_client = get_nado_client(mode=NadoClientMode.MAINNET)
```

### Extending Functionality
*   **New Strategies**: Create new functions or files in `src/strategy.py` for different trading logic.
*   **Advanced Risk Management**: Implement more complex risk controls in `src/trade_execution.py` or a dedicated module.

## Deployment Strategy

A recommended deployment approach is using **Docker** for portability, isolation, and ease of management.

1.  **Containerization**: Create a `Dockerfile` to package the bot and its dependencies.
2.  **Environment Variables**: Inject sensitive credentials (like `NADO_PRIVATE_KEY`) as Docker secrets or environment variables at runtime.
3.  **Orchestration**: Use Docker Compose for single-host deployments or Kubernetes for scalable, multi-host environments.
4.  **Monitoring**: Integrate with Docker's logging mechanisms; consider external logging services.
5.  **CI/CD**: Automate build, test, and deployment with CI/CD pipelines.
6.  **Security**: Follow Docker best practices (e.g., non-root user, updated base images).

## License

This project is open-source and available under the [MIT License](LICENSE).
