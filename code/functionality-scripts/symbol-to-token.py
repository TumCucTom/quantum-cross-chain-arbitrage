import requests

# Define the API endpoint for fetching token addresses (using CoinGecko as an example)
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/list"
ETHERSCAN_API_URL = "https://api.etherscan.io/api"
ETHERSCAN_API_KEY = "YourEtherscanAPIKey"  # Replace with your actual key

FEED_IDS = {
    "AAVE": "0x01414156452f555344000000000000000000000000",
    "ADA": "0x014144412f55534400000000000000000000000000",
    "ALGO": "0x01414c474f2f555344000000000000000000000000",
    "APT": "0x014150542f55534400000000000000000000000000",
    "ARB": "0x014152422f55534400000000000000000000000000",
    "ATOM": "0x0141544f4d2f555344000000000000000000000000",
    "AVAX": "0x01415641582f555344000000000000000000000000",
    "BCH": "0x014243482f55534400000000000000000000000000",
    "BNB": "0x01424e422f55534400000000000000000000000000",
    "BTC": "0x014254432f55534400000000000000000000000000",
    "DOGE": "0x01444f47452f555344000000000000000000000000",
    "DOT": "0x01444f542f55534400000000000000000000000000",
    "ETC": "0x014554432f55534400000000000000000000000000",
    "ETH": "0x014554482f55534400000000000000000000000000",
    "FIL": "0x0146494c2f55534400000000000000000000000000",
    "FLR": "0x01464c522f55534400000000000000000000000000",
    "FTM": "0x0146544d2f55534400000000000000000000000000",
    "HBAR": "0x01484241522f555344000000000000000000000000",
    "ICP": "0x014943502f55534400000000000000000000000000",
    "LINK": "0x014c494e4b2f555344000000000000000000000000",
    "LTC": "0x014c54432f55534400000000000000000000000000",
    "NEAR": "0x014e4541522f555344000000000000000000000000",
    "QNT": "0x01514e542f55534400000000000000000000000000",
    "SHIB": "0x01534849422f555344000000000000000000000000",
    "SOL": "0x01534f4c2f55534400000000000000000000000000",
    "UNI": "0x01554e492f55534400000000000000000000000000",
    "USDC": "0x01555344432f555344000000000000000000000000",
    "USDT": "0x01555344542f555344000000000000000000000000",
    "XLM": "0x01584c4d2f55534400000000000000000000000000",
    "XRP": "0x015852502f55534400000000000000000000000000",
}

def fetch_token_addresses(symbols):
    """Fetch token contract addresses for given symbols using CoinGecko API with better handling."""
    response = requests.get(COINGECKO_API_URL)
    if response.status_code != 200:
        print("Failed to fetch data from CoinGecko.")
        return {}

    token_list = response.json()
    symbol_to_coingecko_id = {token['symbol'].upper(): token['id'] for token in token_list if token['symbol'].upper() in symbols}

    contract_addresses = {}
    for symbol, gecko_id in symbol_to_coingecko_id.items():
        token_data = requests.get(f"https://api.coingecko.com/api/v3/coins/{gecko_id}").json()
        platforms = token_data.get('platforms', {})
        contract_address = platforms.get('ethereum') or platforms.get('binance-smart-chain') or platforms.get('polygon-pos')
        if contract_address:
            contract_addresses[symbol] = contract_address
        else:
            print(f"Warning: No contract address found for {symbol}")

    return contract_addresses

def fetch_etherscan_contract(symbols):
    """Fetch token contract addresses using Etherscan API."""
    addresses = {}
    for symbol in symbols:
        params = {
            "module": "token",
            "action": "tokeninfo",
            "contractaddress": symbol,
            "apikey": ETHERSCAN_API_KEY
        }
        response = requests.get(ETHERSCAN_API_URL, params=params)
        if response.status_code == 200 and "result" in response.json():
            addresses[symbol] = response.json()["result"]["contractAddress"]
    return addresses

def main():
    symbols = list(FEED_IDS.keys())  # Replace with your desired symbols
    token_addresses = fetch_token_addresses(symbols)
    print("Token Addresses from CoinGecko:", token_addresses)

    #etherscan_addresses = fetch_etherscan_contract(symbols)
    #print("Token Addresses from Etherscan:", etherscan_addresses)

if __name__ == "__main__":
    main()
