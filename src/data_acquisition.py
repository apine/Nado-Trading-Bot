from src.nado_client import get_nado_client, NadoClientMode
from datetime import datetime
from nado_protocol.indexer_client.types.query import IndexerCandlesticksParams, IndexerCandlesticksGranularity

# Mapping for candlestick intervals
INTERVAL_MAP = {
    "1M": IndexerCandlesticksGranularity.ONE_MINUTE,
    "5M": IndexerCandlesticksGranularity.FIVE_MINUTES,
    "15M": IndexerCandlesticksGranularity.FIFTEEN_MINUTES,
    "1H": IndexerCandlesticksGranularity.ONE_HOUR,
    "2H": IndexerCandlesticksGranularity.TWO_HOURS,
    "4H": IndexerCandlesticksGranularity.FOUR_HOURS,
    "1D": IndexerCandlesticksGranularity.ONE_DAY,
    "1W": IndexerCandlesticksGranularity.ONE_WEEK,
    "4W": IndexerCandlesticksGranularity.FOUR_WEEKS,
}

def get_latest_btc_perp_price():
    """
    Initializes Nado client and fetches the latest Perpetual BTC price.
    """
    try:
        nado_client = get_nado_client()
        perp_prices_data = nado_client.perp.get_prices(2)

        if perp_prices_data:
            mark_price = int(perp_prices_data.mark_price_x18) / (10**18)
            return mark_price
        else:
            print("Could not retrieve perpetual BTC prices.")
            return None
    except Exception as e:
        print(f"An error occurred while fetching BTC Perpetual price: {e}")
        return None

def get_historical_candlesticks(product_id: int, interval: str):
    """
    Fetches historical candlestick data for a given product.

    Args:
        product_id (int): The ID of the product (e.g., 1 for BTC).
        interval (str): The candlestick interval (e.g., "1H", "4H", "1D").

    Returns:
        list: A list of candlestick data, or None if an error occurs.
    """
    try:
        nado_client = get_nado_client()

        granularity = INTERVAL_MAP.get(interval)
        if not granularity:
            raise ValueError(f"Invalid interval: {interval}. Supported intervals are {list(INTERVAL_MAP.keys())}")

        params = IndexerCandlesticksParams(
            product_id=product_id,
            granularity=granularity
        )

        candlesticks_data = nado_client.market.get_candlesticks(params)
        if candlesticks_data and hasattr(candlesticks_data, 'candlesticks'):
            return candlesticks_data.candlesticks
        else:
            print("No candlestick data found or invalid response structure.")
            return None
    except Exception as e:
        print(f"An error occurred while fetching historical candlesticks: {e}")
        return None

if __name__ == "__main__":
    # Test getting latest BTC perp price
    latest_price = get_latest_btc_perp_price()
    if latest_price:
        print(f"Latest Perpetual BTC Mark Price: {latest_price}")

    print("\n--- Testing Historical Candlesticks ---")
    # Example: Fetch 1-hour candlesticks for BTC (product_id=2)
    product_id_btc = 2
    interval_1h = "1H"

    historical_data = get_historical_candlesticks(
        product_id=product_id_btc,
        interval=interval_1h
    )

    if historical_data:
        print(f"Fetched {len(historical_data)} historical candlesticks for BTC (1H interval).")
        # Print the first few candlesticks to inspect the structure
        for i, candle in enumerate(historical_data[:5]):
            print(f"  Candle {i+1}: {candle}")
    else:
        print("Failed to retrieve historical candlestick data.")