import requests

def get_token_price_and_details(token_address):
    url = f"https://api.dexscreener.io/latest/dex/tokens/{token_address}"
    response = requests.get(url)
    data = response.json()

    if 'pairs' in data and data['pairs']:
        for pair in data['pairs']:
            if 'quoteToken' in pair and pair['quoteToken'].get('symbol') == 'SOL':
                
                return pair
    return "Token pair with SOL not found or token does not exist."

# Example usage
token_address = "BY4CGbCLfXiu4oXpw3Uq5hkHS6XQbk7TndMb9zPZ9tcd"

print(get_token_price_and_details(token_address))