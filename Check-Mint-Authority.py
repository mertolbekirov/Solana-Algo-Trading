from solana.rpc.api import Client  # Import the Client class from Solana's RPC API to interact with the Solana blockchain.
from solders.pubkey import Pubkey  # Pubkey for handling public keys within Solana's ecosystem.

solana_client = Client("https://api.mainnet-beta.solana.com")  # Initializes a client connected to the Solana mainnet.
token_address = "BY4CGbCLfXiu4oXpw3Uq5hkHS6XQbk7TndMb9zPZ9tcd"

mintAuthority = "Disabled"

account_info = solana_client.get_account_info_json_parsed(Pubkey.from_string(token_address))
mintAuthority_Check = account_info.value.data.parsed['info']['mintAuthority']
if str(mintAuthority_Check) != "None":
    mintAuthority = "Enabled"
else:
    mintAuthority = "Disabled"

print (f'Mint Authority for token: {mintAuthority}')