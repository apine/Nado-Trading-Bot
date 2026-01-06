from src.nado_client import get_nado_client, NadoClientMode
from nado_protocol.engine_client.types.execute import PlaceMarketOrderParams
from nado_protocol.utils.math import to_x18
from nado_protocol.utils.expiration import get_expiration_timestamp
from nado_protocol.client import NadoClientMode
from src.account_summary import get_account_summary

def place_market_order_for_product(
    product_id: int,
    subaccount: str,
    is_buy: bool,
    amount: float
):
    """
    Places a market order for a given product.

    Args:
        product_id (int): The ID of the product.
        subaccount (str): The subaccount ID to place the order from.
        is_buy (bool): True for a buy order, False for a sell order.
        amount (float): The amount to trade.
    """
    try:
        nado_client = get_nado_client()

        scaled_amount = to_x18(amount)

        params = PlaceMarketOrderParams(
            product_id=product_id,
            subaccount=subaccount,
            is_buy=is_buy,
            amount=scaled_amount,
        )

        order_result = nado_client.market.place_market_order(params)
        print(f"Market order placed successfully: {order_result}")
        return order_result
    except Exception as e:
        print(f"An error occurred while placing market order: {e}")
        return None

def place_stop_loss_order(
    product_id: int,
    subaccount: str,
    position_is_long: bool,  # True if current position is long, False if short
    stop_price: float,
    amount_to_close: float,
    limit_price: float = None # Optional limit price for the triggered order
):
    """
    Places a stop-loss order.

    Args:
        product_id (int): The ID of the product.
        subaccount (str): The subaccount ID.
        position_is_long (bool): True if the current position is long, False if short.
        stop_price (float): The price at which to trigger the stop-loss.
        amount_to_close (float): The amount of the position to close.
        limit_price (float, optional): The limit price for the order once triggered.
                                      If None, it becomes a market order at trigger.
    """
    try:
        nado_client = get_nado_client()

        scaled_amount = to_x18(amount_to_close)
        scaled_stop_price = to_x18(stop_price)
        scaled_limit_price = to_x18(limit_price) if limit_price else 0 # Use 0 for market if no limit

        # If long position, stop-loss is a sell order triggered when price goes below stop_price
        # If short position, stop-loss is a buy order triggered when price goes above stop_price
        is_buy_order = not position_is_long
        trigger_type = "last_price_below" if position_is_long else "last_price_above"

        # Amount to close should be negative for sell orders, positive for buy orders.
        order_amount_x18 = -scaled_amount if position_is_long else scaled_amount

        trigger_order_result = nado_client.market.place_price_trigger_order(
            product_id=product_id,
            sender=subaccount,
            price_x18=str(scaled_limit_price), # Limit price for the order once triggered
            amount_x18=str(order_amount_x18),
            trigger_price_x18=str(scaled_stop_price),
            trigger_type=trigger_type,
            expiration=get_expiration_timestamp(3600 * 24 * 7),
            reduce_only=True,
        )
        print(f"Stop-loss order placed successfully: {trigger_order_result}")
        return trigger_order_result
    except Exception as e:
        print(f"An error occurred while placing stop-loss order: {e}")
        return None

def place_take_profit_order(
    product_id: int,
    subaccount: str,
    position_is_long: bool,  # True if current position is long, False if short
    take_profit_price: float,
    amount_to_close: float,
    limit_price: float = None # Optional limit price for the triggered order
):
    """
    Places a take-profit order.

    Args:
        product_id (int): The ID of the product.
        subaccount (str): The subaccount ID.
        position_is_long (bool): True if the current position is long, False if short.
        take_profit_price (float): The price at which to trigger the take-profit.
        amount_to_close (float): The amount of the position to close.
        limit_price (float, optional): The limit price for the order once triggered.
                                      If None, it becomes a market order at trigger.
    """
    try:
        nado_client = get_nado_client()

        scaled_amount = to_x18(amount_to_close)
        scaled_take_profit_price = to_x18(take_profit_price)
        scaled_limit_price = to_x18(limit_price) if limit_price else 0 # Use 0 for market if no limit

        # If long position, take-profit is a sell order triggered when price goes above take_profit_price
        # If short position, take-profit is a buy order triggered when price goes below take_profit_price
        is_buy_order = not position_is_long
        trigger_type = "last_price_above" if position_is_long else "last_price_below"

        # Amount to close should be negative for sell orders, positive for buy orders.
        order_amount_x18 = -scaled_amount if position_is_long else scaled_amount

        trigger_order_result = nado_client.market.place_price_trigger_order(
            product_id=product_id,
            sender=subaccount,
            price_x18=str(scaled_limit_price), # Limit price for the order once triggered
            amount_x18=str(order_amount_x18),
            trigger_price_x18=str(scaled_take_profit_price),
            trigger_type=trigger_type,
            expiration=get_expiration_timestamp(3600 * 24 * 7),
            reduce_only=True,
        )
        print(f"Take-profit order placed successfully: {trigger_order_result}")
        return trigger_order_result
    except Exception as e:
        print(f"An error occurred while placing take-profit order: {e}")
        return None

if __name__ == "__main__":
    # Example usage (requires a valid subaccount and API key in .env)
    # NOTE: This will attempt to place real trigger orders on the TESTNET!
    # Ensure your private key is configured correctly and you understand the implications.

    subaccount_summary_data = get_account_summary()
    test_subaccount_id = None
    if subaccount_summary_data and hasattr(subaccount_summary_data, 'subaccount'):
        test_subaccount_id = subaccount_summary_data.subaccount
    else:
        from src.data_acquisition import get_nado_client
        nado_client_temp = get_nado_client()
        subaccounts_list = nado_client_temp.subaccount.get_subaccounts()
        if subaccounts_list and subaccounts_list.subaccounts:
            test_subaccount_id = subaccounts_list.subaccounts[0].subaccount
            print(f"DEBUG: Retrieved subaccount from list: {test_subaccount_id}")

    if test_subaccount_id:
        print(f"Using subaccount ID: {test_subaccount_id} for order placement simulation.")

        product_id_btc = 2 # BTC
        trade_amount = 0.0001 # Small amount for testing

        # --- Simulate Market Order ---
        print("\nSimulating a BUY market order with parameters:")
        print(f"  product_id={product_id_btc}")
        print(f"  subaccount={test_subaccount_id}")
        print(f"  is_buy={True}")
        print(f"  amount={trade_amount}")
        # buy_order_result = place_market_order_for_product(
        #     product_id=product_id_btc,
        #     subaccount=test_subaccount_id,
        #     is_buy=True,
        #     amount=trade_amount
        # )

        # --- Simulate Stop-Loss Order ---
        # Assuming a long position for BTC (buy order)
        current_price = 90000 # Placeholder for current price
        stop_loss_price = 89000

        print(f"\nSimulating a Stop-Loss order for a LONG position (current price {current_price}):")
        print(f"  product_id={product_id_btc}")
        print(f"  subaccount={test_subaccount_id}")
        print(f"  position_is_long={True}")
        print(f"  stop_price={stop_loss_price}")
        print(f"  amount_to_close={trade_amount}")
        # stop_loss_result = place_stop_loss_order(
        #     product_id=product_id_btc,
        #     subaccount=test_subaccount_id,
        #     position_is_long=True,
        #     stop_price=stop_loss_price,
        #     amount_to_close=trade_amount
        # )

        # --- Simulate Take-Profit Order ---
        # Assuming a long position for BTC (buy order)
        take_profit_price = 95000

        print(f"\nSimulating a Take-Profit order for a LONG position (current price {current_price}):")
        print(f"  product_id={product_id_btc}")
        print(f"  subaccount={test_subaccount_id}")
        print(f"  position_is_long={True}")
        print(f"  take_profit_price={take_profit_price}")
        print(f"  amount_to_close={trade_amount}")
        # take_profit_result = place_take_profit_order(
        #     product_id=product_id_btc,
        #     subaccount=test_subaccount_id,
        #     position_is_long=True,
        #     take_profit_price=take_profit_price,
        #     amount_to_close=trade_amount
        # )

    else:
        print("Skipping order placement and trigger order simulations due to missing subaccount ID.")