import os
import requests
from dotenv import load_dotenv
from web3 import Web3
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Load environment variables
load_dotenv()
FLARE_RPC_URL = os.getenv("FLARE_RPC_URL")
ETH_RPC_URL = os.getenv("ETH_RPC_URL")

# Initialize Web3 clients
web3_flare = Web3(Web3.HTTPProvider(FLARE_RPC_URL))
web3_eth = Web3(Web3.HTTPProvider(ETH_RPC_URL))

# GraphQL endpoints for Uniswap and Curve
UNISWAP_SUBGRAPH = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
CURVE_SUBGRAPH = "https://api.thegraph.com/subgraphs/name/curvefi/curve"

# -----------------------------
# 1️⃣ Fetch Price Data from Flare's FTSO
# -----------------------------

def get_ftso_price(asset_symbol):
    """
    Fetch real-time price from Flare's Time Series Oracle (FTSO).
    """
    try:
        response = requests.get(f"https://flare-ftso-api.com/price/{asset_symbol}")
        price = response.json().get("price")
        print(f"[FTSO] {asset_symbol}: {price} USD")
        return price
    except Exception as e:
        print(f"[ERROR] FTSO price fetch failed: {e}")
        return None

# -----------------------------
# 2️⃣ Fetch Liquidity Pool Data from Uniswap & Curve
# -----------------------------

def get_uniswap_liquidity():
    """
    Fetch Uniswap liquidity pool data using The Graph API.
    """
    try:
        client = Client(transport=RequestsHTTPTransport(url=UNISWAP_SUBGRAPH))
        query = gql("""
            query {
                pair(id: "0xYourPoolAddress") {
                    reserve0 reserve1
                    token0 { symbol }
                    token1 { symbol }
                }
            }
        """)
        data = client.execute(query)
        print(f"[Uniswap] Liquidity: {data['pair']}")
        return data["pair"]
    except Exception as e:
        print(f"[ERROR] Uniswap liquidity fetch failed: {e}")
        return None

def get_curve_liquidity():
    """
    Fetch Curve liquidity pool data using The Graph API.
    """
    try:
        client = Client(transport=RequestsHTTPTransport(url=CURVE_SUBGRAPH))
        query = gql("""
            query {
                pool(id: "0xYourCurvePoolAddress") {
                    reserves
                }
            }
        """)
        data = client.execute(query)
        print(f"[Curve] Liquidity: {data['pool']}")
        return data["pool"]
    except Exception as e:
        print(f"[ERROR] Curve liquidity fetch failed: {e}")
        return None

# -----------------------------
# 3️⃣ Fetch Gas Fees from Ethereum & Flare
# -----------------------------

def get_gas_prices():
    """
    Fetch gas prices for Ethereum and Flare networks.
    """
    try:
        eth_gas_price = web3_eth.eth.gas_price
        flare_gas_price = web3_flare.eth.gas_price
        print(f"[Gas Prices] Ethereum: {eth_gas_price} wei | Flare: {flare_gas_price} wei")
        return {"eth_gas_price": eth_gas_price, "flare_gas_price": flare_gas_price}
    except Exception as e:
        print(f"[ERROR] Gas price fetch failed: {e}")
        return None

# -----------------------------
# 4️⃣ Verify Cross-Chain Transactions with Flare's State Connector
# -----------------------------

def verify_cross_chain_transaction(tx_hash):
    """
    Verify cross-chain transaction state using Flare's State Connector.
    """
    try:
        response = requests.get(f"https://flare-state-connector-api.com/verify/{tx_hash}")
        result = response.json().get("verified", False)
        if result:
            print(f"[State Connector] ✅ Transaction {tx_hash} is verified.")
        else:
            print(f"[State Connector] ❌ Transaction {tx_hash} verification failed.")
        return result
    except Exception as e:
        print(f"[ERROR] State Connector verification failed: {e}")
        return False

# -----------------------------
# 5️⃣ Run All Data Collection Steps
# -----------------------------

if __name__ == "__main__":
    print("🚀 Starting Data Collection...")

    # Fetch Market Data
    eth_price = get_ftso_price("ETH")
    btc_price = get_ftso_price("BTC")
    usdt_price = get_ftso_price("USDT")

    # Fetch DEX Liquidity
    uniswap_liquidity = get_uniswap_liquidity()
    curve_liquidity = get_curve_liquidity()

    # Fetch Gas Prices
    gas_prices = get_gas_prices()

    # Verify a Cross-Chain Transaction
    test_tx_hash = "0xYourTestTransactionHash"
    verified = verify_cross_chain_transaction(test_tx_hash)
