import os
import json
import asyncio
import requests
from datetime import datetime
from dotenv import load_dotenv
from web3 import Web3, AsyncWeb3, AsyncHTTPProvider

# Load environment variables
load_dotenv()
FLARE_RPC_URL = os.getenv("FLARE_RPC_URL")
ETH_RPC_URL = os.getenv("ETH_RPC_URL")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

# Initialize Web3 clients
web3_flare = Web3(Web3.HTTPProvider(FLARE_RPC_URL))
web3_eth = Web3(Web3.HTTPProvider(ETH_RPC_URL))

# Flare FTSO Feeds
FTSOV2_ADDRESS = "0x3d893C53D9e8056135C26C8c638B76C8b60Df726"
RPC_URL = "https://coston2-api.flare.network/ext/C/rpc"

FEED_IDS = {
    "FLR/USD": "0x01464c522f55534400000000000000000000000000",
    "BTC/USD": "0x014254432f55534400000000000000000000000000",
    "ETH/USD": "0x014554482f55534400000000000000000000000000",
}
TOKEN_ADDRESSES = {
    "FLR": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",  # Placeholder for FLR (Not native on Ethereum)
    "BTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",  # Wrapped BTC (WBTC)
    "ETH": "0xC02aaa39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # Wrapped ETH (WETH)
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # Tether USDT
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USD Coin (USDC)
    "USD": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # Map "USD" → USDC (or use USDT)
}

# Convert ABI from JSON string to Python list
ABI = json.loads('''[
    {"inputs":[{"internalType":"address","name":"_addressUpdater","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},
    {"inputs":[],"name":"FTSO_PROTOCOL_ID","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"bytes21","name":"_feedId","type":"bytes21"}],"name":"getFeedById","outputs":[
        {"internalType":"uint256","name":"","type":"uint256"},
        {"internalType":"int8","name":"","type":"int8"},
        {"internalType":"uint64","name":"","type":"uint64"}
    ],"stateMutability":"payable","type":"function"}
]''')

# -----------------------------
# 1️⃣ Fetch Price Data from Flare's FTSO (Async)
# -----------------------------

async def get_ftso_prices() -> dict:
    """Fetch real-time prices from Flare's FTSO."""
    w3 = AsyncWeb3(AsyncHTTPProvider(RPC_URL))

    # Verify connection
    if not await w3.is_connected():
        raise ConnectionError("Failed to connect to the Flare Web3 provider.")

    ftsov2 = w3.eth.contract(address=w3.to_checksum_address(FTSOV2_ADDRESS), abi=ABI)

    prices = {}
    for symbol, feed_id in FEED_IDS.items():
        try:
            feeds, decimals, timestamp = await ftsov2.functions.getFeedById(feed_id).call()
            real_price = feeds / (10 ** decimals)
            human_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
            prices[symbol] = {"price": real_price, "timestamp": human_time}
            print(f"[FTSO] {symbol}: {real_price} USD (Updated: {human_time})")
        except Exception as e:
            print(f"[ERROR] FTSO fetch failed for {symbol}: {e}")

    return prices

# -----------------------------
# 2️⃣ Fetch Uniswap & Curve Pool Addresses Dynamically
# -----------------------------

def get_uniswap_pool_address(token0: str, token1: str) -> str:
    """
    Fetch Uniswap v3 pool address using the Uniswap v3 Factory contract.
    """
    try:
        UNISWAP_FACTORY_ADDRESS = "0x1F98431c8aD98523631AE4a59f267346ea31F984"  # Uniswap V3 Factory
        UNISWAP_FACTORY_ABI = get_contract_abi(UNISWAP_FACTORY_ADDRESS)

        if not UNISWAP_FACTORY_ABI:
            print(f"[ERROR] Failed to get Uniswap Factory ABI.")
            return None

        web3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))
        factory_contract = web3.eth.contract(address=UNISWAP_FACTORY_ADDRESS, abi=UNISWAP_FACTORY_ABI)

        # Fetch contract addresses for token0 and token1
        token0_address = TOKEN_ADDRESSES.get(token0)
        token1_address = TOKEN_ADDRESSES.get(token1)

        if not token0_address or not token1_address:
            print(f"[ERROR] Token address missing for {token0}/{token1}")
            return None

        # ✅ Convert to checksum addresses
        token0_address = Web3.to_checksum_address(token0_address)
        token1_address = Web3.to_checksum_address(token1_address)

        # ✅ Ensure token0 < token1 to match Uniswap's expected ordering
        token0_address, token1_address = (token0_address, token1_address) if int(token0_address, 16) < int(token1_address, 16) else (token1_address, token0_address)

        # ✅ Uniswap v3 uses fee tiers (500, 3000, 10000)
        pool_address = factory_contract.functions.getPool(token0_address, token1_address, 3000).call()
        print(f"[Uniswap] Pool Address for {token0}/{token1}: {pool_address}")

        return pool_address if pool_address != "0x0000000000000000000000000000000000000000" else None
    except Exception as e:
        print(f"[ERROR] Failed to fetch Uniswap pool address: {e}")
        return None


def get_curve_pool_address(token0: str, token1: str) -> str:
    """
    Fetch Curve pool address using the Curve Factory contract.
    """
    try:
        CURVE_FACTORY_ADDRESS = "0xF18056Bbd320E96A48e3Fbf8bC061322531aac99"  # Curve Pool Factory
        CURVE_FACTORY_ABI = get_contract_abi(CURVE_FACTORY_ADDRESS)

        if not CURVE_FACTORY_ABI:
            print(f"[ERROR] Failed to get Curve Factory ABI.")
            return None

        web3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))
        factory_contract = web3.eth.contract(address=CURVE_FACTORY_ADDRESS, abi=CURVE_FACTORY_ABI)

        # Fetch contract addresses for token0 and token1
        token0_address = TOKEN_ADDRESSES.get(token0)
        token1_address = TOKEN_ADDRESSES.get(token1)

        if not token0_address or not token1_address:
            print(f"[ERROR] Token address missing for {token0}/{token1}")
            return None

        # Call factory contract to get Curve pool address
        pool_address = factory_contract.functions.find_pool_for_coins(token0_address, token1_address).call()
        print(f"[Curve] Pool Address for {token0}/{token1}: {pool_address}")

        return pool_address if pool_address != "0x0000000000000000000000000000000000000000" else None
    except Exception as e:
        print(f"[ERROR] Failed to fetch Curve pool address: {e}")
        return None


# -----------------------------
# 3️⃣ Fetch Smart Contract ABI from Etherscan
# -----------------------------

def get_contract_abi(address: str) -> list:
    """Fetch contract ABI from Etherscan."""
    try:
        url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={ETHERSCAN_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return json.loads(data["result"]) if "result" in data else None
    except Exception as e:
        print(f"[ERROR] Failed to fetch ABI for {address}: {e}")
        return None

# -----------------------------
# 4️⃣ Fetch Liquidity Pool Data using Web3
# -----------------------------

def get_pool_liquidity(pool_address: str, abi: list):
    """Fetch liquidity data from Uniswap or Curve pools."""
    try:
        pool_contract = web3_eth.eth.contract(address=pool_address, abi=abi)
        liquidity = pool_contract.functions.liquidity().call()
        print(f"[Liquidity] Pool: {pool_address}, Liquidity: {liquidity}")
        return liquidity
    except Exception as e:
        print(f"[ERROR] Liquidity fetch failed: {e}")
        return None

# -----------------------------
# 5️⃣ Run All Data Collection Steps
# -----------------------------

async def main():
    print("🚀 Starting Data Collection...")

    # ✅ Fetch Market Data
    ftso_prices = await get_ftso_prices()

    # ✅ Prepare output JSON
    live_data = {}

    # ✅ Fetch Pool Addresses & Liquidity
    for pair in FEED_IDS.keys():
        token0, token1 = pair.split("/")  # Extract tokens correctly

        # ✅ Convert "USD" → "USDC"
        token0 = "USDC" if token0 == "USD" else token0
        token1 = "USDC" if token1 == "USD" else token1

        # ✅ Ensure token contract addresses exist
        token0_address = TOKEN_ADDRESSES.get(token0)
        token1_address = TOKEN_ADDRESSES.get(token1)

        if not token0_address or not token1_address:
            print(f"[ERROR] Token address missing for {token0}/{token1}")
            continue  # Skip this pair if any address is missing

        # ✅ Fetch Uniswap & Curve Pool Addresses
        uniswap_pool = get_uniswap_pool_address(token0, token1)
        curve_pool = get_curve_pool_address(token0, token1)

        # ✅ Fetch Uniswap & Curve Liquidity
        uniswap_liquidity = get_pool_liquidity(uniswap_pool, get_contract_abi(uniswap_pool)) if uniswap_pool else None
        curve_liquidity = get_pool_liquidity(curve_pool, get_contract_abi(curve_pool)) if curve_pool else None

        # ✅ Get Latest Price from FTSO
        asset_symbol = token0 if token0 != "USDC" else token1
        asset_data = ftso_prices.get(f"{asset_symbol}/USD", {})

        # ✅ Construct JSON Output
        live_data[asset_symbol] = {
            "price": asset_data.get("price", None),
            "uniswap_liquidity": uniswap_liquidity,
            "curve_liquidity": curve_liquidity,
            "timestamp": asset_data.get("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        }

    # ✅ Print JSON Output for API Usage
    print(json.dumps(live_data, indent=4))

    return live_data

if __name__ == "__main__":
    asyncio.run(main())
