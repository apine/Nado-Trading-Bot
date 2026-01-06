import os
from nado_protocol.client import create_nado_client, NadoClientMode
from nado_protocol.utils.backend import Signer

def get_nado_client(mode=None):
    """
    Initializes and returns a Nado client.
    """
    if mode is None:
        mode = NadoClientMode.TESTNET

    private_key = os.getenv("NADO_PRIVATE_KEY")
    if not private_key:
        raise ValueError("NADO_PRIVATE_KEY must be set in the .env file.")

    client = create_nado_client(mode, private_key)
    return client

if __name__ == "__main__":
    try:
        nado_client = get_nado_client()
        print("Successfully initialized Nado client.")
        # You can add more checks here, like fetching account information
        # print(nado_client.get_account())
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

