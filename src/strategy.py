import pandas as pd
from src.data_acquisition import get_historical_candlesticks

def calculate_sma(data: pd.Series, window: int) -> pd.Series:
    """
    Calculates the Simple Moving Average (SMA) for a given data series.
    """
    return data.rolling(window=window).mean()

def moving_average_crossover_strategy(
    product_id: int,
    interval: str,
    short_window: int,
    long_window: int
) -> pd.DataFrame:
    """
    Implements a moving average crossover strategy.

    Args:
        product_id (int): The ID of the product (e.g., 1 for BTC).
        interval (str): The candlestick interval (e.g., "1H", "4H", "1D").
        short_window (int): The window size for the short-term SMA.
        long_window (int): The window size for the long-term SMA.

    Returns:
        pd.DataFrame: A DataFrame with historical data, SMAs, and buy/sell signals.
    """
    candlesticks = get_historical_candlesticks(product_id, interval)

    if not candlesticks:
        return pd.DataFrame()

    # Convert to pandas DataFrame
    df = pd.DataFrame([
        {
            'timestamp': int(c.timestamp),
            'open': int(c.open_x18) / (10**18),
            'high': int(c.high_x18) / (10**18),
            'low': int(c.low_x18) / (10**18),
            'close': int(c.close_x18) / (10**18),
            'volume': int(c.volume) # Volume might not be scaled, checking docs needed.
        } for c in candlesticks
    ])

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True) # Ensure data is sorted by time

    # Calculate SMAs
    df['SMA_Short'] = calculate_sma(df['close'], short_window)
    df['SMA_Long'] = calculate_sma(df['close'], long_window)

    # Generate signals
    df['Signal'] = 0 # 0 for hold, 1 for buy, -1 for sell
    df.loc[df.index[short_window:], 'Signal'] = \
        (df['SMA_Short'][short_window:] > df['SMA_Long'][short_window:]).astype(int)

    # Detect actual trade signals (crossover points)
    df['Position'] = df['Signal'].diff()

    return df

if __name__ == "__main__":
    product_id_btc = 2
    interval_1h = "1H"
    short_window = 10
    long_window = 30

    strategy_data = moving_average_crossover_strategy(
        product_id_btc, interval_1h, short_window, long_window
    )

    if not strategy_data.empty:
        print(f"Strategy Data for BTC ({interval_1h} interval, {short_window}/{long_window} SMA):")
        print(strategy_data.tail()) # Print last few rows

        buy_signals = strategy_data[strategy_data['Position'] == 1]
        sell_signals = strategy_data[strategy_data['Position'] == -1]

        if not buy_signals.empty:
            print("\nBuy Signals:")
            print(buy_signals[['close', 'SMA_Short', 'SMA_Long', 'Position']])

        if not sell_signals.empty:
            print("\nSell Signals:")
            print(sell_signals[['close', 'SMA_Short', 'SMA_Long', 'Position']])
    else:
        print("Failed to generate strategy data.")
