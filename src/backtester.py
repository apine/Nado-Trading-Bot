import pandas as pd
from src.strategy import moving_average_crossover_strategy

def run_backtest(
    product_id: int,
    interval: str,
    short_window: int,
    long_window: int,
    initial_capital: float = 10000.0,
    commission_rate: float = 0.001, # 0.1% commission
    slippage: float = 0.0001 # 0.01% slippage
) -> dict:
    """
    Runs a backtest of the moving average crossover strategy.

    Args:
        product_id (int): The ID of the product (e.g., 1 for BTC).
        interval (str): The candlestick interval (e.g., "1H", "4H", "1D").
        short_window (int): The window size for the short-term SMA.
        long_window (int): The window size for the long-term SMA.
        initial_capital (float): Starting capital for the backtest.
        commission_rate (float): Commission rate per trade (e.g., 0.001 for 0.1%).
        slippage (float): Slippage percentage per trade.

    Returns:
        dict: A dictionary containing backtest results (e.g., final capital, PnL, trades).
    """
    strategy_data = moving_average_crossover_strategy(
        product_id, interval, short_window, long_window
    )

    if strategy_data.empty:
        print("No strategy data to backtest.")
        return {}

    capital = initial_capital
    position = 0  # 0 for no position, 1 for long, -1 for short
    trades = []
    current_trade_pnl = 0
    in_trade = False

    for i, row in strategy_data.iterrows():
        # Buy signal
        if row['Position'] == 1 and position == 0:
            # Open a long position
            trade_price = row['close'] * (1 + slippage)
            shares = capital / trade_price
            capital -= shares * trade_price
            capital -= shares * trade_price * commission_rate
            position = 1
            in_trade = True
            trades.append({'date': i, 'type': 'BUY', 'price': trade_price, 'shares': shares, 'capital': capital})
            print(f"BUY: {i} - Price: {trade_price:.2f}, Shares: {shares:.6f}, Capital: {capital:.2f}")

        # Sell signal (to close long position)
        elif row['Position'] == -1 and position == 1:
            # Close long position
            trade_price = row['close'] * (1 - slippage)
            capital += shares * trade_price
            capital -= shares * trade_price * commission_rate
            current_trade_pnl = (shares * trade_price) - (trades[-1]['shares'] * trades[-1]['price']) # Simple PnL for this trade
            position = 0
            in_trade = False
            trades.append({'date': i, 'type': 'SELL', 'price': trade_price, 'shares': shares, 'capital': capital, 'pnl': current_trade_pnl})
            print(f"SELL: {i} - Price: {trade_price:.2f}, Shares: {shares:.6f}, Capital: {capital:.2f}, PnL: {current_trade_pnl:.2f}")

        # Additional logic for short selling if desired:
        # if row['Position'] == -1 and position == 0:
        #     # Open a short position
        #     trade_price = row['close'] * (1 - slippage)
        #     shares = capital / trade_price # Assuming we can short with full capital value
        #     capital += shares * trade_price # Shorting increases capital initially
        #     capital -= shares * trade_price * commission_rate
        #     position = -1
        #     in_trade = True
        #     trades.append({'date': i, 'type': 'SHORT', 'price': trade_price, 'shares': shares, 'capital': capital})
        #     print(f"SHORT: {i} - Price: {trade_price:.2f}, Shares: {shares:.6f}, Capital: {capital:.2f}")

        # elif row['Position'] == 1 and position == -1:
        #     # Close short position
        #     trade_price = row['close'] * (1 + slippage)
        #     capital -= shares * trade_price # Closing short decreases capital
        #     capital -= shares * trade_price * commission_rate
        #     current_trade_pnl = (trades[-1]['shares'] * trades[-1]['price']) - (shares * trade_price) # PnL for short
        #     position = 0
        #     in_trade = False
        #     trades.append({'date': i, 'type': 'COVER', 'price': trade_price, 'shares': shares, 'capital': capital, 'pnl': current_trade_pnl})
        #     print(f"COVER: {i} - Price: {trade_price:.2f}, Shares: {shares:.6f}, Capital: {capital:.2f}, PnL: {current_trade_pnl:.2f}")

    # If still in a position at the end, close it
    if position == 1: # Long position
        trade_price = strategy_data.iloc[-1]['close'] * (1 - slippage)
        capital += shares * trade_price
        capital -= shares * trade_price * commission_rate
        current_trade_pnl = (shares * trade_price) - (trades[-1]['shares'] * trades[-1]['price'])
        trades.append({'date': strategy_data.index[-1], 'type': 'SELL_FINAL', 'price': trade_price, 'shares': shares, 'capital': capital, 'pnl': current_trade_pnl})
        print(f"SELL_FINAL: {strategy_data.index[-1]} - Price: {trade_price:.2f}, Shares: {shares:.6f}, Capital: {capital:.2f}, PnL: {current_trade_pnl:.2f}")
    elif position == -1: # Short position
        trade_price = strategy_data.iloc[-1]['close'] * (1 + slippage)
        capital -= shares * trade_price
        capital -= shares * trade_price * commission_rate
        current_trade_pnl = (trades[-1]['shares'] * trades[-1]['price']) - (shares * trade_price)
        trades.append({'date': strategy_data.index[-1], 'type': 'COVER_FINAL', 'price': trade_price, 'shares': shares, 'capital': capital, 'pnl': current_trade_pnl})
        print(f"COVER_FINAL: {strategy_data.index[-1]} - Price: {trade_price:.2f}, Shares: {shares:.6f}, Capital: {capital:.2f}, PnL: {current_trade_pnl:.2f}")


    final_pnl = capital - initial_capital
    return {
        'initial_capital': initial_capital,
        'final_capital': capital,
        'total_pnl': final_pnl,
        'num_trades': len(trades),
        'trades': trades
    }

if __name__ == "__main__":
    product_id_btc = 2
    interval_1h = "1H"
    short_window = 10
    long_window = 30
    initial_capital = 100000.0 # Increased initial capital for better visibility

    results = run_backtest(
        product_id_btc, interval_1h, short_window, long_window, initial_capital
    )

    if results:
        print("\n--- Backtest Results ---")
        print(f"Initial Capital: {results['initial_capital']:.2f}")
        print(f"Final Capital: {results['final_capital']:.2f}")
        print(f"Total PnL: {results['total_pnl']:.2f}")
        print(f"Number of Trades: {results['num_trades']}")
    else:
        print("Backtest failed or no trades executed.")
