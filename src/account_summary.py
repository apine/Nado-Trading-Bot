from src.nado_client import get_nado_client, NadoClientMode
from nado_protocol.client import NadoClientMode
import os

def get_account_summary():
    """
    Initializes Nado client and fetches the account summary.
    """
    try:
        nado_client = get_nado_client()
        main_account_address = nado_client.context.signer.address
        print(f"Fetching subaccounts for main account address: {main_account_address}")

        subaccounts = nado_client.subaccount.get_subaccounts(address=main_account_address)

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
    account_data = get_account_summary()
    if account_data:
        print("\n--- Account Summary ---")
        print(f"Subaccount ID: {account_data.subaccount}")
        print(f"Account Exists: {account_data.exists}")

        # Summarize Healths
        if account_data.healths:
            first_health = account_data.healths[0]
            # Assuming assets are scaled by 1e18, common in Nado SDK
            assets_descaled = int(first_health.assets) / (10**18) if first_health.assets else 0
            liabilities_descaled = int(first_health.liabilities) / (10**18) if first_health.liabilities else 0
            health_descaled = int(first_health.health) / (10**18) if first_health.health else 0
            print(f"\nAccount Health (Sample - first health metric):")
            print(f"  Assets: {assets_descaled:.6f}")
            print(f"  Liabilities: {liabilities_descaled:.6f}")
            print(f"  Health: {health_descaled:.6f}")
        else:
            print("\nNo account health data available.")

        # Summarize Spot Balances
        print("\nSpot Balances:")
        if account_data.spot_balances:
            for balance in account_data.spot_balances:
                amount_descaled = int(balance.balance.amount) / (10**18) if balance.balance.amount else 0
                print(f"  Product ID {balance.product_id}: Amount = {amount_descaled:.6f}")
        else:
            print("  No spot balances found.")

        # Summarize Perpetual Balances
        print("\nPerpetual Balances:")
        if account_data.perp_balances:
            for balance in account_data.perp_balances:
                amount_descaled = int(balance.balance.amount) / (10**18) if balance.balance.amount else 0
                v_quote_balance_descaled = int(balance.balance.v_quote_balance) / (10**18) if balance.balance.v_quote_balance else 0
                print(f"  Product ID {balance.product_id}: Amount = {amount_descaled:.6f}, Virtual Quote Balance = {v_quote_balance_descaled:.6f}")
        else:
            print("  No perpetual balances found.")

    else:
        print("Failed to retrieve account summary.")
