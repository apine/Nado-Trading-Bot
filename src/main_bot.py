import time
from datetime import datetime
import traceback
from dotenv import load_dotenv

from src.logger import logger
from src.strategy import moving_average_crossover_strategy
from src.trade_execution import (
    place_market_order_for_product,
    place_stop_loss_order,
    place_take_profit_order
)
from src.account_summary import get_account_summary
from src.nado_client import get_nado_client, NadoClientMode

# Load environment variables
load_dotenv()

# --- Bot Configuration ---
PRODUCT_ID = 2             # BTC Perpetual
INTERVAL = "1H"            # Candlestick interval for strategy
SHORT_WINDOW = 10          # Short-term SMA window
LONG_WINDOW = 30           # Long-term SMA window
TRADE_AMOUNT = 0.0001      # Amount to trade for each position
CHECK_INTERVAL_SECONDS = 300 # 5 minutes

# --- Risk Management Configuration ---
STOP_LOSS_PERCENT = 2.0  # % below entry price for stop-loss
TAKE_PROFIT_PERCENT = 4.0 # % above entry price for take-profit

# --- Bot State ---
current_position = None # Can be 'long', 'short', or None

def run_bot():
    """
    The main function to run the trading bot continuously.
    """
    global current_position

    logger.info("Starting Nado Trading Bot...")
    logger.info(f"Configuration: Product ID={PRODUCT_ID}, Interval={INTERVAL}, Strategy={SHORT_WINDOW}/{LONG_WINDOW} SMA Crossover")

    # Get subaccount for trading
    try:
        nado_client = get_nado_client()
        subaccounts = nado_client.subaccount.get_subaccounts(address=nado_client.context.signer.address)
        if not subaccounts or not subaccounts.subaccounts:
            logger.error("No subaccounts found for the provided private key. Exiting.")
            return
        subaccount_id = subaccounts.subaccounts[0].subaccount
        logger.info(f"Using subaccount ID: {subaccount_id}")
    except Exception as e:
        logger.error(f"Failed to initialize bot and get subaccount: {e}")
        logger.error(traceback.format_exc())
        return

    while True:
        try:
            logger.info("Checking for new trading signals...")

            # 1. Get strategy data and the latest signal
            strategy_df = moving_average_crossover_strategy(
                PRODUCT_ID, INTERVAL, SHORT_WINDOW, LONG_WINDOW
            )

            if strategy_df.empty:
                logger.warning("Could not generate strategy data. Skipping this cycle.")
                time.sleep(CHECK_INTERVAL_SECONDS)
                continue

            latest_signal = strategy_df.iloc[-1]
            last_crossover = latest_signal['Position'] # 1 for buy, -1 for sell, 0 for no change

            entry_price = latest_signal['close']

            # 2. Execute trades based on signals
            if last_crossover == 1 and current_position is None:
                # --- Buy Signal ---
                logger.info(f"Buy signal detected at price {entry_price:.2f}. Opening a long position.")
                current_position = 'long'

                # --- EXECUTE LIVE TRADE ---
                # **WARNING**: Uncommenting the following lines will place REAL orders on the TESTNET.
                logger.info(f"Placing market BUY order for {TRADE_AMOUNT} of product {PRODUCT_ID}")
                buy_order_result = place_market_order_for_product(
                    product_id=PRODUCT_ID,
                    subaccount=subaccount_id,
                    is_buy=True,
                    amount=TRADE_AMOUNT
                )
                if buy_order_result:
                    logger.info(f"Market buy order successful: {buy_order_result}")

                    # Place Stop-Loss and Take-Profit orders
                    stop_price = entry_price * (1 - STOP_LOSS_PERCENT / 100)
                    take_profit_price = entry_price * (1 + TAKE_PROFIT_PERCENT / 100)

                    logger.info(f"Placing stop-loss order at {stop_price:.2f}")
                    place_stop_loss_order(
                        PRODUCT_ID, subaccount_id, position_is_long=True,
                        stop_price=stop_price, amount_to_close=TRADE_AMOUNT
                    )

                    logger.info(f"Placing take-profit order at {take_profit_price:.2f}")
                    place_take_profit_order(
                        PRODUCT_ID, subaccount_id, position_is_long=True,
                        take_profit_price=take_profit_price, amount_to_close=TRADE_AMOUNT
                    )
                else:
                    logger.error("Market buy order failed. No risk management orders placed.")
                    current_position = None # Reset position as entry failed


            elif last_crossover == -1 and current_position == 'long':
                # --- Sell Signal ---
                logger.info(f"Sell signal detected. Closing long position.")
                current_position = None

                # --- EXECUTE LIVE TRADE ---
                # **WARNING**: Uncommenting the following lines will place REAL orders on the TESTNET.
                # In a real scenario, you'd cancel existing TP/SL orders first.
                # Here, we assume a simple market order to close the position.
                logger.info(f"Placing market SELL order for {TRADE_AMOUNT} of product {PRODUCT_ID}")
                sell_order_result = place_market_order_for_product(
                    product_id=PRODUCT_ID,
                    subaccount=subaccount_id,
                    is_buy=False,
                    amount=TRADE_AMOUNT
                )
                if sell_order_result:
                    logger.info(f"Market sell order successful: {sell_order_result}")
                else:
                    logger.error("Market sell order failed to close position.")
                    current_position = 'long' # Revert state as closing failed

            else:
                logger.info("No new trading opportunities. Holding current position.")

            logger.info(f"Next check at {datetime.fromtimestamp(time.time() + CHECK_INTERVAL_SECONDS)}")
            time.sleep(CHECK_INTERVAL_SECONDS)

        except Exception as e:
            logger.error(f"An unexpected error occurred in the main trading loop: {e}")
            logger.error(traceback.format_exc())
            time.sleep(CHECK_INTERVAL_SECONDS) # Wait before retrying


if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info("Bot shutting down gracefully...")
        print("\nBot stopped by user.")
