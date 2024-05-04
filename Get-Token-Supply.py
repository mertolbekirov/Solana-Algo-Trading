import requests
import json

def get_token_supply(token_address):
    url = "https://api.mainnet-beta.solana.com"
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenSupply",
        "params": [token_address]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()
    # Extracting the amount (adjusting for decimals as needed)
    supply = int(result['result']['value']['amount']) / (10 ** result['result']['value']['decimals'])
    return supply

token_address = "Ee8LeXBM2XqFKoGSeiMmuQPAZ51GN8otr2tVEp4FJjf5"
token_details = get_token_supply(token_address)
print()
print(token_details)
