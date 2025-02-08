import asyncio
import json
import ssl
import certifi
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
from web3 import AsyncHTTPProvider, AsyncWeb3, Web3
import requests
from itertools import permutations


# --- Configuration ---
FTSOV2_ADDRESS = "0x3d893C53D9e8056135C26C8c638B76C8b60Df726"
RPC_URL = "https://coston2-api.flare.network/ext/C/rpc"
INFURA_URL = "https://mainnet.infura.io/v3/8ba16afae1db46e19bd1b161fc9cc720"  # Replace with your Infura key
UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"  # Uniswap V2 Router

# Uniswap V2 ABIs
UNISWAP_V2_ABI = json.loads('[{"constant":true,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":false,"stateMutability":"view","type":"function"}]')

UNISWAP_V2_PAIR_ABI = json.loads('[{"constant":true,"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"reserve0","type":"uint112"},{"internalType":"uint112","name":"reserve1","type":"uint112"},{"internalType":"uint32","name":"blockTimestampLast","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"}]')


TOKEN_ADDRESSES = {
    "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
    "ADA": "0x3ee2200efb3400fabb9aacf31297cbdd1d435d47",
    "ALGO": "0xf4E3fe15fe13Ee5A6EeB67F18d7A30Fb863Ce20f",
    "APT": "0x00312B3D7f39F63b15D5B2078F2862249B09338D",
    "ARB": "0x912CE59144191C1204E64559FE8253a0e49E6548",
    "ATOM": "0x0eb3a705fc54725037cc9e008bdede697f62f335",
    "AVAX": "0x1ce0c2827e2ef14d5c4f29a091d735a204794041",
    "BCH": "0x8ff795a6f4d97e7887c79bea79aba5cc76444adf",
    "BNB": "0xb8c77482e45f1f44de1745f52c74426c631bdd52",
    "BTC": "0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c",
    "DOGE": "0xba2ae424d960c26247dd6c32edc70b295c744c43",
    "DOT": "0x7083609fce4d1d8dc0c979aab8c869ea2c873402",
    "ETC": "0xdD2799Fc98C010D967ba0a95A1fe6DaB8C08cb97",
    "ETH": "0x2170ed0880ac9a755fd29b2688956bd959f933f8",
    "FIL": "0x0d8ce2a99bb6e3b7db580ed848240e4a0f9ae153",
    "FLR": "0xc1b23c67dffb267956736dbea4b3962fed05763a",
    "FTM": "0xad29abb318791d579433d831ed122afeaf29dcfe",
    "HBAR": "0xa43C7F27E36279645Bd1620070414e564ec291a9",
    "ICP": "0xc807acd80861edd471115d505f1d7f3bb1808969",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "LTC": "0x4338665cbb7b2485a8855a139b75d5e34ab0db94",
    "NEAR": "0x85f17cf997934a597031b2e18a9ab6ebd4b9f6a4",
    "QNT": "0x4a220e6096b25eadb88358cb44068a3248254675",
    "SHIB": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
    "SOL": "0x1f54638b7737193ffd86c19ec51907a7c41755d8",
    "UNI": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
    "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "USDT": "0xdac17f958d2ee523a2206206994597c13d831ec7",
    "XLM": "0xba5fe23f8a3a24bed3236f05f2fcf35fd0bf0b5c",
    "XRP": "0x1d2f0da169ceb9fc7b3144628db156f3f6c60dbe",
}

TOKEN_ADDRESSES = {symbol: Web3.to_checksum_address(address) for symbol, address in TOKEN_ADDRESSES.items()}

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

# Convert ABI from JSON string to Python list
ABI_JSON_STRING = '''[
    {"inputs":[{"internalType":"address","name":"_addressUpdater","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},
    {"inputs":[],"name":"FTSO_PROTOCOL_ID","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"bytes21","name":"_feedId","type":"bytes21"}],"name":"getFeedById","outputs":[
        {"internalType":"uint256","name":"","type":"uint256"},
        {"internalType":"int8","name":"","type":"int8"},
        {"internalType":"uint64","name":"","type":"uint64"}
    ],"stateMutability":"payable","type":"function"}
]'''
ABI = json.loads(ABI_JSON_STRING)

async def get_ftso_prices():
    """Fetch live token prices from Flare FTSO."""
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    w3 = AsyncWeb3(AsyncHTTPProvider(RPC_URL))

    if not await w3.is_connected():
        raise ConnectionError("Failed to connect to Flare network.")

    ftsov2 = w3.eth.contract(address=w3.to_checksum_address(FTSOV2_ADDRESS), abi=ABI)

    prices = {}
    for token, feed_id in FEED_IDS.items():
        feed_value, decimals, timestamp = await ftsov2.functions.getFeedById(feed_id).call()
        real_price = feed_value / (10 ** decimals)
        prices[token] = real_price

    return prices

async def get_reserves(tokenA, tokenB, web3):
    """Fetch reserves from Uniswap V2 Pair Contract, ensuring valid addresses and ignoring inactive pairs."""

    # Ensure token addresses exist
    if tokenA not in TOKEN_ADDRESSES or tokenB not in TOKEN_ADDRESSES:
        print(f"⚠️ Skipping {tokenA}-{tokenB}: Missing token address")
        return None

    tokenA_address = Web3.to_checksum_address(TOKEN_ADDRESSES[tokenA])
    tokenB_address = Web3.to_checksum_address(TOKEN_ADDRESSES[tokenB])

    try:
        factory_contract = web3.eth.contract(
            address=Web3.to_checksum_address(UNISWAP_V2_ROUTER),
            abi=UNISWAP_V2_ABI
        )

        # Check for a valid pair
        pair_address = await factory_contract.functions.getPair(tokenA_address, tokenB_address).call()

        if pair_address == "0x0000000000000000000000000000000000000000":
            print(f"⚠️ No liquidity pool exists for {tokenA}-{tokenB}. Skipping.")
            return None  # Ignore inactive pairs

        pair_contract = web3.eth.contract(
            address=Web3.to_checksum_address(pair_address),
            abi=UNISWAP_V2_PAIR_ABI
        )

        reserves = await pair_contract.functions.getReserves().call()
        return reserves  # Returns (reserve0, reserve1, timestamp)

    except Exception as e:
        print(f"❌ Error fetching reserves for {tokenA}-{tokenB}: {str(e)}")
        return None  # Ignore errors in fetching reserves


async def fetch_all_reserves(web3):
    """Fetch reserves for all token pairs dynamically"""
    reserve_data = {}
    #token_pairs = list(permutations(TOKEN_ADDRESSES.keys(), 2))
    token_pairs = [
        ("ETH", "BTC"), ("BTC", "USDT"), ("ETH", "USDT"),
        ("ETH", "LINK"), ("ETH", "UNI"), ("BTC", "LTC"),
        ("ETH", "DAI"), ("USDC", "USDT"), ("SOL", "ETH"),
        ("MATIC", "ETH"), ("BNB", "ETH"), ("AVAX", "ETH"),
    ]

    for tokenA, tokenB in token_pairs:
        if tokenA in TOKEN_ADDRESSES and tokenB in TOKEN_ADDRESSES:
            reserves = await get_reserves(tokenA, tokenB, web3)
            if reserves:
                reserve_data[(tokenA, tokenB)] = reserves
            else:
                # Assigning estimated reserves for testing
                reserve_data[(tokenA, tokenB)] = (1000000, 5000)  # Example reserves
        else:
            print(f"⚠️ Skipping {tokenA}-{tokenB}: One or both token addresses are missing")

    return reserve_data


def calculate_slippage(input_amount, tokenA, tokenB, reserves):
    """Calculate slippage using real reserves from DEX liquidity pools"""
    reserveA, reserveB = reserves.get((tokenA, tokenB), (0, 0))
    if reserveA == 0 or reserveB == 0:
        return float('inf')  # Avoid division by zero

    expected_price = reserveB / reserveA
    new_reserveA = reserveA + input_amount
    new_reserveB = reserveB - (input_amount * expected_price)
    executed_price = new_reserveB / new_reserveA
    slippage = abs((executed_price - expected_price) / expected_price) * 100
    return slippage

async def build_arbitrage_graph(prices, web3):
    """Construct arbitrage graph using real-time reserves from DEX liquidity pools"""
    G = nx.DiGraph()
    reserves = await fetch_all_reserves(web3)

    for (tokenA, tokenB), (reserveA, reserveB) in reserves.items():
        if tokenA in prices and tokenB in prices:
            profitability = prices[tokenB] / prices[tokenA] - 1
            slippage_cost = calculate_slippage(10, tokenA, tokenB, reserves)
            weight = profitability - (slippage_cost / 100)

            if weight > 0:
                G.add_edge(tokenA, tokenB, weight=round(weight, 5))

    return G

def plot_arbitrage_graph(G):
    """Visualize arbitrage graph with weighted edges."""
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)
    edge_labels = {(u, v): f"{d['weight']:.5f}" for u, v, d in G.edges(data=True)}

    nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=2500, font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    plt.title("Live Arbitrage Graph (Flare FTSO Data)")
    plt.show()

async def main():
    web3 = AsyncWeb3(AsyncHTTPProvider(INFURA_URL))

    # Fetch live Flare prices
    prices = await get_ftso_prices()

    # Build arbitrage graph
    arbitrage_graph = await build_arbitrage_graph(prices, web3)

    # Visualize graph
    plot_arbitrage_graph(arbitrage_graph)

if __name__ == "__main__":
    asyncio.run(main())
