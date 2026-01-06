from src.nado_client import get_nado_client, NadoClientMode
from nado_protocol.client import NadoClientMode
import os

PRODUCT_ID = 2

def get_subaccount_id(nado_client):
    """Retrieves the first subaccount ID."""
    subaccounts = nado_client.subaccount.get_subaccounts(address=nado_client.context.signer.address)
    if subaccounts and subaccounts.subaccounts:
        return subaccounts.subaccounts[0].subaccount
    return None

def test():
    """
    Initializes Nado client and run test
    """
    try:
        nado_client = get_nado_client() # Ensure TESTNET is used for development
        #nado_client = get_nado_client(mode=NadoClientMode.MAINNET)
        subaccount_id = get_subaccount_id(nado_client)

        if not subaccount_id:
            print("No subaccount found. Exiting.")
            return

        print(f"Using Subaccount: {subaccount_id}")
        summary = nado_client.subaccount.get_engine_subaccount_summary(subaccount=subaccount_id)
        position_amount_x18 = 0
        v_quote_balance_x18 = 0
        if summary and summary.perp_balances:
            for bal in summary.perp_balances:
                if bal.product_id == PRODUCT_ID:
                    position_amount_x18 = int(bal.balance.amount)
                    v_quote_balance_x18 = int(bal.balance.v_quote_balance)

        position_amount = position_amount_x18 / 1e18
        has_open_position = abs(position_amount) > 0.00001
        entry_price = abs(v_quote_balance_x18 / position_amount_x18) if position_amount_x18 != 0 else 0

        print(position_amount)
        print(entry_price)
    except Exception as e:
        print(f"An error occurred while running test: {e}")
        return None

def get_account_summary():
    """
    Initializes Nado client and fetches the account summary.
    """
    try:
        #nado_client = get_nado_client(mode=NadoClientMode.TESTNET) # Ensure TESTNET is used for development
        nado_client = get_nado_client()

        main_address = nado_client.context.signer.address
        subaccounts = nado_client.subaccount.get_subaccounts(address=main_address)

        if not subaccounts.subaccounts:
            print("No subaccounts found.")
            return None

        # Assuming we want the first subaccount for the summary
        first_subaccount = subaccounts.subaccounts[0]
        first_subaccount_id = first_subaccount.subaccount
        print(f"Fetching summary for subaccount ID: {first_subaccount_id}")

        # 2. Get the engine subaccount summary
        summary = nado_client.subaccount.get_engine_subaccount_summary(subaccount=first_subaccount_id)

        return summary
    except Exception as e:
        print(f"An error occurred while fetching account summary: {e}")
        return None

if __name__ == "__main__":
    test()
